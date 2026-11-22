<?php
// Executed inside the disposable Apache container, not on the production host.
// Credentials come from stdin; report only fixed stages, HTTP codes and counts.
const BASE = 'http://127.0.0.1';
const LIMIT = 8388608;

function request($method, $path, $user = null, $password = null, $headers = [], $body = null) {
    if (!str_starts_with($path, '/') || str_starts_with($path, '//') || preg_match('/[\r\n]/', $path)) {
        throw new RuntimeException('invalid_local_path');
    }
    $ch = curl_init(BASE . $path);
    $out = '';
    curl_setopt_array($ch, [
        CURLOPT_CUSTOMREQUEST => $method, CURLOPT_HTTPHEADER => $headers,
        CURLOPT_FOLLOWLOCATION => false, CURLOPT_PROXY => '',
        CURLOPT_CONNECTTIMEOUT => 3, CURLOPT_TIMEOUT => 30,
        CURLOPT_WRITEFUNCTION => function($ch, $chunk) use (&$out) {
            if (strlen($out) + strlen($chunk) > LIMIT) return 0;
            $out .= $chunk;
            return strlen($chunk);
        },
    ]);
    if ($user !== null) {
        curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
        curl_setopt($ch, CURLOPT_USERNAME, $user);
        curl_setopt($ch, CURLOPT_PASSWORD, $password);
    }
    if ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
    $ok = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    // CurlHandle is released automatically; curl_close emits a deprecation on PHP 8.5.
    unset($ch);
    return [$ok !== false ? $code : 0, $out];
}

function davpath($href, $prefix) {
    $path = parse_url($href, PHP_URL_PATH);
    if (!is_string($path) || !str_starts_with($path, $prefix)
            || preg_match('/[\r\n]/', $path)) return null;
    foreach (explode('/', rawurldecode($path)) as $part) {
        if ($part === '..' || $part === '.') return null;
    }
    return $path;
}

function davxml($body) {
    $doc = new DOMDocument();
    if (!@$doc->loadXML($body, LIBXML_NONET | LIBXML_NOERROR | LIBXML_NOWARNING))
        throw new RuntimeException('invalid_dav_xml');
    $xp = new DOMXPath($doc);
    $xp->registerNamespace('d', 'DAV:');
    $xp->registerNamespace('c', 'urn:ietf:params:xml:ns:caldav');
    return $xp;
}

function probe($user, $password) {
    $result = [
        'stage' => 'http_startup', 'http_ready' => false,
        'authenticated_as_restored_user' => false, 'webdav_listing_passed' => false,
        'restored_file_read_passed' => false, 'file_sample_bytes' => 0,
        'caldav_listing_passed' => false, 'calendar_count' => 0,
        'calendar_query_passed' => false, 'calendar_event_objects' => 0,
        'browser_login_not_tested' => true,
    ];
    for ($i = 0; $i < 30; $i++) {
        [$code, $body] = request('GET', '/status.php');
        $data = json_decode($body, true);
        if ($code === 200 && is_array($data) && ($data['installed'] ?? false)
            && !($data['maintenance'] ?? true) && !($data['needsDbUpgrade'] ?? true)
            && preg_match('/^34[.]0[.]5([.][0-9]+)?$/', $data['version'] ?? '')) {
            $result['http_ready'] = true;
            break;
        }
        sleep(1);
    }
    $result['status_http_code'] = $code;
    if (!$result['http_ready']) return $result;

    // OCS authenticates using the restored account, without creating a new user.
    $result['stage'] = 'authenticated_user';
    [$code, $body] = request('GET', '/ocs/v2.php/cloud/user?format=json', $user, $password,
        ['OCS-APIRequest: true', 'Accept: application/json']);
    $result['identity_http_code'] = $code;
    $identity = json_decode($body, true)['ocs'] ?? [];
    $uid = $identity['data']['id'] ?? null;
    if ($code !== 200 || !in_array((int)($identity['meta']['statuscode'] ?? 0), [100, 200], true)
        || !is_string($uid) || $uid === '') return $result;
    $result['authenticated_as_restored_user'] = true;
    $encoded = rawurlencode($uid);

    // Read pre-existing user data; no upload, scan, repair or database upgrade.
    $result['stage'] = 'webdav';
    $root = '/remote.php/dav/files/' . $encoded . '/';
    $prop = '<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/><d:getcontentlength/></d:prop></d:propfind>';
    $queue = [$root]; $seen = []; $sample = null; $visited = 0;
    while ($queue && $visited < 40 && $sample === null) {
        $dir = array_shift($queue);
        if (isset($seen[$dir])) continue;
        $seen[$dir] = true; $visited++;
        [$code, $body] = request('PROPFIND', $dir, $user, $password,
            ['Depth: 1', 'Content-Type: application/xml'], $prop);
        $result['webdav_http_code'] = $code;
        if ($code !== 207) break;
        $result['webdav_listing_passed'] = true;
        $xp = davxml($body);
        foreach ($xp->query('/d:multistatus/d:response') as $row) {
            $path = davpath($xp->evaluate('string(d:href)', $row), $root);
            if ($path === null || rtrim($path, '/') === rtrim($dir, '/')) continue;
            if ($xp->query('d:propstat/d:prop/d:resourcetype/d:collection', $row)->length) {
                if (count($queue) < 100) $queue[] = $path;
                continue;
            }
            $size = $xp->evaluate('string(d:propstat/d:prop/d:getcontentlength)', $row);
            if (ctype_digit($size) && (int)$size > 0) {
                $sample = $path;
                break;
            }
        }
    }
    $result['file_directories_checked'] = $visited;
    if ($sample !== null) {
        [$code, $body] = request('GET', $sample, $user, $password, ['Range: bytes=0-4095']);
        $result['file_http_code'] = $code;
        $result['file_sample_bytes'] = strlen($body);
        $result['restored_file_read_passed'] = in_array($code, [200, 206], true) && strlen($body) > 0;
    }

    $result['stage'] = 'caldav';
    $root = '/remote.php/dav/calendars/' . $encoded . '/';
    [$code, $body] = request('PROPFIND', $root, $user, $password,
        ['Depth: 1', 'Content-Type: application/xml'],
        '<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>');
    $result['caldav_http_code'] = $code;
    if ($code !== 207) return $result;
    $result['caldav_listing_passed'] = true;
    $xp = davxml($body);
    $calendars = [];
    foreach ($xp->query('/d:multistatus/d:response') as $row) {
        if (!$xp->query('d:propstat/d:prop/d:resourcetype/c:calendar', $row)->length) continue;
        $path = davpath($xp->evaluate('string(d:href)', $row), $root);
        if ($path !== null && rtrim($path, '/') !== rtrim($root, '/')) $calendars[$path] = true;
    }
    $result['calendar_count'] = count($calendars);
    $query = '<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:prop><d:getetag/></d:prop><c:filter><c:comp-filter name="VCALENDAR"><c:comp-filter name="VEVENT"/></c:comp-filter></c:filter></c:calendar-query>';
    foreach (array_slice(array_keys($calendars), 0, 10) as $path) {
        [$code, $body] = request('REPORT', $path, $user, $password,
            ['Depth: 1', 'Content-Type: application/xml'], $query);
        $result['calendar_query_http_code'] = $code;
        if ($code !== 207) continue;
        $result['calendar_query_passed'] = true;
        $xp = davxml($body);
        $result['calendar_event_objects'] += $xp->query('/d:multistatus/d:response')->length;
        if ($result['calendar_event_objects'] > 0) break;
    }
    $result['stage'] = 'complete';
    return $result;
}

function emit_probe_result(array $result) {
    // A single JSON record is the entire stdout contract. Any PHP output
    // emitted during the probe (including unexpected library warnings) is
    // discarded, never mixed with the bounded result or sent to the operator.
    fwrite(STDOUT, json_encode($result, JSON_THROW_ON_ERROR) . "\n");
}

if (!defined('NEXTCLOUD_HTTP_TEST')) {
    ini_set('display_errors', 'stderr');
    ini_set('log_errors', '0');
    ob_start();
    try {
        $secret = json_decode(stream_get_contents(STDIN), true, 8, JSON_THROW_ON_ERROR);
        if (!is_string($secret['username'] ?? null) || !is_string($secret['password'] ?? null)
            || $secret['username'] === '' || $secret['password'] === '') throw new RuntimeException('missing_credentials');
        $result = probe($secret['username'], $secret['password']);
    } catch (Throwable $err) {
        // Never return an exception message: it might include private data.
        $result = ['stage'=>'probe_exception', 'http_ready'=>false,
            'authenticated_as_restored_user'=>false, 'restored_file_read_passed'=>false,
            'calendar_query_passed'=>false];
    } finally {
        ob_end_clean();
    }
    emit_probe_result($result);
}
