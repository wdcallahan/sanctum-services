"use strict";
// Aggregate exact source IPs from bounded, fixed NPM proxy-host 11 log tails.
// In an operator-owned private network, source addresses are useful
// diagnostics, not credentials. Show each observed IP + request count,
// NEVER output raw request lines, paths, cookies, query strings, tokens,
// forwarded headers, response bodies, or other log fields.
const fs = require("node:fs");
const path = require("node:path");
const net = require("node:net");
const ROOT = "/data";
const LOG_DIR = path.join(ROOT, "logs");
const NAMES = ["proxy-host-11_access.log", "proxy-host-11_access.log.1"];
const MAX_BYTES = 1024 * 1024;
const MAX_DISTINCT = 24;
const MONTHS = {Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,
                Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11};
const KNOWN_SOURCES = new Map([
  ["192.168.0.192", "known_kvin_observer"],
  ["192.168.0.7", "known_kvar_host"],
  ["127.0.0.1", "known_kvar_loopback"],
]);

function boundedTail(file) {
  let fd;
  try {
    const stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink()) return {
      readable:false, truncated:false, content:""};
    const length = Math.min(MAX_BYTES, stat.size);
    const from = Math.max(0, stat.size - MAX_BYTES);
    const buffer = Buffer.alloc(length);
    fd = fs.openSync(file, "r");
    let read = 0;
    while (read < length) {
      const n = fs.readSync(fd, buffer, read, length - read, from + read);
      if (!n) break;
      read += n;
    }
    let content = buffer.subarray(0, read).toString("utf8");
    if (from > 0) {
      const firstLineEnd = content.indexOf("\n");
      content = firstLineEnd === -1 ? "" : content.slice(firstLineEnd + 1);
    }
    return {readable:true, truncated:from > 0, content};
  } catch (_) {
    return {readable:false, truncated:false, content:""};
  } finally {
    if (fd !== undefined) {
      try {fs.closeSync(fd);} catch (_) {}
    }
  }
}
function dateFromLine(line) {
  const m = line.match(/\[(\d\d)\/([A-Za-z]{3})\/(\d{4}):(\d\d):(\d\d):(\d\d) ([+-])(\d\d)(\d\d)\]/);
  if (!m || !(m[2] in MONTHS)) return null;
  const offset = (Number(m[8]) * 60 + Number(m[9])) * (m[7] === "+" ? 1 : -1);
  const t = Date.UTC(Number(m[3]), MONTHS[m[2]], Number(m[1]),
    Number(m[4]), Number(m[5]), Number(m[6])) - offset * 60000;
  return Number.isFinite(t) ? t : null;
}
function sourceFromLine(line) {
  // The logged [Client 1.2.3.4] field, never a guessed address elsewhere.
  const matches = [...line.matchAll(/\[Client ([0-9]{1,3}(?:\.[0-9]{1,3}){3})\]/g)];
  if (matches.length !== 1) return null;
  const ip = matches[0][1];
  return net.isIP(ip) === 4 ? ip : null;
}
function inspect() {
  const counts = new Map();
  let lines = 0, records30 = 0, unknown = 0, readCount = 0, truncated = false;
  let unreadableCount = 0;
  const now = Date.now();
  for (const name of NAMES) {
    const r = boundedTail(path.join(LOG_DIR, name));
    truncated ||= r.truncated;
    if (!r.readable) {unreadableCount++; continue;}
    readCount++;
    for (const line of r.content.split("\n").filter(Boolean)) {
      lines++;
      const t = dateFromLine(line);
      if (t === null || t > now || now - t > 30 * 86400000) continue;
      records30++;
      const source = sourceFromLine(line);
      if (source === null) {unknown++; continue;}
      counts.set(source, (counts.get(source) || 0) + 1);
    }
  }
  const entries = [...counts.entries()]
    .map(([ip, requests]) => ({
      source_ip: ip,
      requests,
      classification: KNOWN_SOURCES.get(ip) || "other_observed_source",
    }))
    .sort((a, b) => b.requests - a.requests || a.source_ip.localeCompare(b.source_ip));
  const limited = entries.length > MAX_DISTINCT;
  const rendered = limited ? entries.slice(0, MAX_DISTINCT) : entries;
  return {
    observer: "kvar.outer.sanctum",
    frontend: "yarn.inner.sanctum",
    source_field: "NPM logged [Client IPv4] only",
    sampled_logs_readable: readCount,
    sampled_logs_unreadable_or_missing: unreadableCount,
    log_tail_truncated: truncated,
    lines_examined: lines,
    requests_with_recent_timestamps: records30,
    unclassified_recent_entries: unknown,
    distinct_source_addresses_seen: entries.length,
    source_address_list_truncated: limited,
    sources_last_30_days: rendered,
    source_ips_exposed_intentionally: true,
    raw_http_requests_cookies_urls_and_log_lines_exposed: false,
    current_client_dependency_proven: false,
    safe_to_retire_proven: false,
    configuration_changed: false,
    limitation: "Exact IPs are source addresses recorded by the legacy NPM access log, not verified device identities; NAT/proxying may hide original clients. Logs cover only two fixed bounded tails. Services tests may appear. Do not retire or enable old Yarn solely from these counts."
  };
}
try {process.stdout.write(JSON.stringify(inspect()) + "\n");}
catch (_) {
  process.stdout.write(JSON.stringify({
    observer: "kvar.outer.sanctum", outcome: "not_observed",
    configuration_changed:false, safe_to_retire_proven:false
  }) + "\n");
}
