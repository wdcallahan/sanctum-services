"use strict";
// Read only, inside the EXISTING Kvar NPM container, never copy raw logs.
// Reports aggregate counts from exactly proxy-host 11's known access logs.
// Missing logs, incomplete rotation and Kvin's own diagnostic requests mean
// this is merely a client-use SIGNAL, never evidence it is safe to retire.
const fs = require("node:fs");
const path = require("node:path");
const ROOT = "/data";
const CONF = path.join(ROOT, "nginx/proxy_host/11.conf");
const LOG_DIR = path.join(ROOT, "logs");
const LOG_NAME = "proxy-host-11_access.log";
const MAX_BYTES_EACH = 1024 * 1024;
const MONTHS = {Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,
                Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11};

function readTextFileFixed(file, limit) {
  try {
    const stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink()) return null;
    if (stat.size > limit) return null;
    return fs.readFileSync(file, "utf8");
  } catch (_) { return null; }
}
function safeTail(file) {
  let fd;
  try {
    const stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink()) return {
      status: "not_regular", truncated: false, text: ""};
    const size = stat.size;
    const position = Math.max(0, size - MAX_BYTES_EACH);
    const len = Math.min(size, MAX_BYTES_EACH);
    fd = fs.openSync(file, "r");
    const buf = Buffer.alloc(len);
    let offset = 0;
    while (offset < len) {
      const n = fs.readSync(fd, buf, offset, len - offset, position + offset);
      if (!n) break;
      offset += n;
    }
    let text = buf.subarray(0, offset).toString("utf8");
    if (position > 0) {
      const first = text.indexOf("\n");
      text = first < 0 ? "" : text.slice(first + 1);
    }
    return {status:"readable", truncated: position > 0, text};
  } catch (_) { return {status:"not_readable", truncated:false, text:""}; }
  finally { if (fd !== undefined) { try { fs.closeSync(fd); } catch (_) {} } }
}
function parseTimestamp(line) {
  // Nginx default access time_local: [10/Nov/2026:18:40:22 -0600].
  // Different formats are reported as unparseable, not guessed.
  const match = line.match(/\[(\d\d)\/([A-Za-z]{3})\/(\d{4}):(\d\d):(\d\d):(\d\d) ([+-])(\d\d)(\d\d)\]/);
  if (!match || !(match[2] in MONTHS)) return null;
  const [, day, mon, year, hour, minute, second, sign, offsetHour, offsetMinute] = match;
  const timezoneMinutes = (Number(offsetHour) * 60 + Number(offsetMinute))
    * (sign === "+" ? 1 : -1);
  const instant = Date.UTC(Number(year), MONTHS[mon], Number(day),
      Number(hour), Number(minute), Number(second))
      - timezoneMinutes * 60000;
  return Number.isFinite(instant) ? instant : null;
}
function inspect() {
  const cfg = readTextFileFixed(CONF, 1024 * 1024);
  const knownLogDirective = /(?:^|\n)\s*access_log\s+\/data\/logs\/proxy-host-11_access\.log(?:\s|;)/;
  const loggingDeclared = cfg === null ? "not_observed" : knownLogDirective.test(cfg);
  let files = [];
  let rotationUnknown = false;
  try {
    const names = fs.readdirSync(LOG_DIR);
    const known = [LOG_NAME, LOG_NAME + ".1"];
    files = known.filter(name => names.includes(name));
    rotationUnknown = names.some(name => name.startsWith(LOG_NAME)
       && !known.includes(name));
  } catch (_) {}
  let entries = 0, parsed = 0, last30 = 0, last7 = 0, latest = null;
  let tailTruncated = false;
  const coverage = [];
  const now = Date.now();
  for (const name of files) {
    const result = safeTail(path.join(LOG_DIR, name));
    coverage.push(result.status);
    tailTruncated ||= result.truncated;
    if (result.status !== "readable") continue;
    const lines = result.text.split("\n").filter(Boolean);
    for (const line of lines) {
      entries++;
      const when = parseTimestamp(line);
      if (when === null) continue;
      parsed++;
      if (when <= now && now - when <= 30 * 86400000) last30++;
      if (when <= now && now - when <= 7 * 86400000) last7++;
      if (when <= now && (latest === null || when > latest)) latest = when;
    }
  }
  const coverageClass = files.length === 0 ? "no_current_or_plain_rotation"
    : coverage.every(x => x === "readable") ? "all_selected_files_readable"
    : "partial_or_unreadable";
  return {
    observer: "kvar.outer.sanctum",
    proxy: "legacy_kvar_npm",
    legacy_frontend: "yarn.inner.sanctum",
    generated_proxy_host_file_present: cfg !== null,
    exact_access_log_directive: loggingDeclared,
    examined_plain_log_count: files.length,
    log_coverage: coverageClass,
    additional_or_compressed_rotations_seen: rotationUnknown,
    selected_log_tail_truncated: tailTruncated,
    lines_examined_in_bounded_tails: entries,
    timestamp_parseable_lines: parsed,
    recorded_requests_last_7_days_in_sample: last7,
    recorded_requests_last_30_days_in_sample: last30,
    newest_timestamp_age_days_if_parseable:
      latest === null ? "not_observed" : Math.floor((now - latest) / 86400000),
    current_client_use_proven: false,
    safe_to_retire_proven: false,
    raw_logs_urls_ips_cookies_exposed: false,
    configuration_changed: false,
    limitation: "Bounded samples of two fixed NPM access logs; rotated history may be incomplete. Probes by Services may be counted as requests. No IPs, URLs or client identity observed. Counts do not prove real clients need the old name, and zero does not justify retirement."
  };
}
try { process.stdout.write(JSON.stringify(inspect()) + "\n"); }
catch (_) {
  process.stdout.write(JSON.stringify({
    observer: "kvar.outer.sanctum", outcome: "not_observed",
    configuration_changed: false, raw_logs_urls_ips_cookies_exposed: false
  }) + "\n");
}
