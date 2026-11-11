"use strict";
// Privacy-preserving supplementary old Yarn consumer signal.
// Read only two fixed, bounded old NPM proxy-host 11 access logs.
// Categorize [Client ...] into known test-host sources or "other".
// NEVER emit an address, path, request string, timestamp, cookie, or
// raw input. Malformed or different log formats remain unclassified.
// Counts do not prove client use or authorize removal of the old hostname.
const fs = require("node:fs");
const path = require("node:path");
const ROOT = "/data";
const DIR = path.join(ROOT, "logs");
const NAMES = ["proxy-host-11_access.log", "proxy-host-11_access.log.1"];
const MAX_BYTES = 1024 * 1024;
const TEST_SOURCES = new Map([
  ["192.168.0.192", "known_kvin_observer"],
  ["192.168.0.7", "known_kvar_host"],
  ["127.0.0.1", "known_kvar_loopback"],
]);
const MONTHS = {Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,
                Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11};

function boundedTail(file) {
  let fd;
  try {
    const stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink()) {
      return {kind:"not_readable", truncated:false, body:""};
    }
    const length = Math.min(MAX_BYTES, stat.size);
    const start = Math.max(0, stat.size - MAX_BYTES);
    const buffer = Buffer.alloc(length);
    fd = fs.openSync(file, "r");
    let done = 0;
    while (done < length) {
      const read = fs.readSync(fd, buffer, done, length - done, start + done);
      if (!read) break;
      done += read;
    }
    let body = buffer.subarray(0, done).toString("utf8");
    if (start) {
      const pos = body.indexOf("\n");
      body = pos === -1 ? "" : body.slice(pos + 1);
    }
    return {kind:"readable", truncated:start > 0, body};
  } catch (_) {
    return {kind:"not_readable", truncated:false, body:""};
  } finally {
    if (fd !== undefined) {
      try { fs.closeSync(fd); } catch (_) {}
    }
  }
}

function loggedTime(line) {
  // A strict local-time field: [10/Nov/2026:20:37:31 -0600].
  const m = line.match(/\[(\d\d)\/([A-Za-z]{3})\/(\d{4}):(\d\d):(\d\d):(\d\d) ([+-])(\d\d)(\d\d)\]/);
  if (!m || !(m[2] in MONTHS)) return null;
  const tz = (Number(m[8]) * 60 + Number(m[9])) * (m[7] === "+" ? 1 : -1);
  const val = Date.UTC(Number(m[3]), MONTHS[m[2]], Number(m[1]),
    Number(m[4]), Number(m[5]), Number(m[6])) - tz * 60000;
  return Number.isFinite(val) ? val : null;
}

function clientCategory(line) {
  // NPM's explicit [Client IPv4] field ONLY; do not guess an IP from a
  // request URI, upstream address, forwarded proxy chain, or text.
  const matches = [...line.matchAll(/\[Client ([0-9]{1,3}(?:\.[0-9]{1,3}){3})\]/g)];
  if (matches.length !== 1) return "unclassified_format";
  const ip = matches[0][1];
  const octets = ip.split(".").map(Number);
  if (octets.length !== 4 || octets.some(n => n > 255)) {
    return "unclassified_format";
  }
  return TEST_SOURCES.get(ip) || "other_observed_source";
}
function main() {
  let filesRead = 0, truncated = false, lines = 0, within30 = 0;
  const counts = {
    known_kvin_observer: 0, known_kvar_host: 0,
    known_kvar_loopback: 0, other_observed_source: 0,
    unclassified_format: 0,
  };
  const now = Date.now();
  const observedFileState = [];
  for (const name of NAMES) {
    const r = boundedTail(path.join(DIR, name));
    observedFileState.push(r.kind);
    truncated ||= r.truncated;
    if (r.kind !== "readable") continue;
    filesRead++;
    for (const line of r.body.split("\n").filter(Boolean)) {
      lines++;
      const when = loggedTime(line);
      if (when === null || when > now || now - when > 30 * 86400000) continue;
      within30++;
      counts[clientCategory(line)]++;
    }
  }
  process.stdout.write(JSON.stringify({
    observer: "kvar.outer.sanctum",
    frontend: "yarn.inner.sanctum",
    source_label_policy: "fixed_known_test_hosts_and_other_only",
    sample_files_read: filesRead,
    samples_truncated: truncated,
    possible_rotated_or_unobserved_history: true,
    lines_examined: lines,
    entries_last_30_days: within30,
    observed_source_classes_last_30_days: counts,
    all_classified_sources_known_tests: (
      within30 > 0 &&
      counts.other_observed_source === 0 &&
      counts.unclassified_format === 0
    ),
    real_client_dependency_proven: false,
    safe_to_retire_proven: false,
    raw_ips_urls_log_lines_exposed: false,
    configuration_changed: false,
    limitation: "Source classes are metadata from fixed log tails only. Kvin/Kvar labels identify known diagnostic host addresses, not a verified human or process. Other includes possible NAT/proxy traffic; unclassified means unknown format. Zero other sources does not establish disuse or authorize retirement."
  }) + "\n");
}
try { main(); }
catch (_) {
  process.stdout.write(JSON.stringify({
    observer: "kvar.outer.sanctum", result: "not_observed",
    raw_ips_urls_log_lines_exposed: false,
    configuration_changed: false, safe_to_retire_proven: false
  }) + "\n");
}
