"use strict";
/* Real Node execution with fake Socket.IO transport; never contacts Kvin. */
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const child = require("node:child_process");
const assert = require("node:assert/strict");
const temp = fs.mkdtempSync(path.join(os.tmpdir(), "kuma-admin-fixture-"));
const lib = path.join(temp, "socket.io-client");
fs.mkdirSync(lib, { recursive: true });
fs.writeFileSync(path.join(lib, "index.js"), `
const EventEmitter = require("node:events");
module.exports.io = function () {
    const socket = new EventEmitter();
    // Real Socket.IO tracks connected state, including when a connection
    // completed before a caller attaches its handler.
    socket.connected = false;
    socket.timeout = () => socket;
    const emit = socket.emit.bind(socket);
    socket.emit = (event, ...args) => {
        const cb = args[args.length - 1];
        if (event === "needSetup") cb(null, process.env.SIM_NEEDS_SETUP === "yes");
        else if (event === "setup") cb(null, { ok: process.env.SIM_SETUP_OK !== "no" });
        else if (event === "login") cb(null, { ok: process.env.SIM_LOGIN_OK !== "no", token: "DO-NOT-PRINT-THIS-TOKEN" });
        else emit(event, ...args);
        return socket;
    };
    socket.disconnect = () => {};
    process.nextTick(() => { socket.connected = true; emit("connect"); });
    return socket;
};
`);
const code = fs.readFileSync(path.join(__dirname, "../../tools/kuma-admin-init.js"), "utf8");
function run(mode, input, opts = {}) {
    return child.spawnSync(process.execPath, ["-e", code, mode], {
        encoding: "utf8",
        input,
        env: { ...process.env, NODE_PATH: temp, ...opts },
        timeout: 5000,
    });
}
try {
    const secret = JSON.stringify({ username: "sanctum-admin", password: "X".repeat(48) });
    let s = run("status", "", { SIM_NEEDS_SETUP: "yes" });
    assert.equal(s.status, 0, s.stderr);
    assert.deepEqual(JSON.parse(s.stdout), { needs_setup: true });
    s = run("bootstrap", secret, { SIM_NEEDS_SETUP: "yes" });
    assert.equal(s.status, 0, s.stderr);
    assert.deepEqual(JSON.parse(s.stdout), { administrator_created: true, administrator_login_verified: true });
    s = run("bootstrap", secret, { SIM_NEEDS_SETUP: "no" });
    assert.equal(s.status, 0, s.stderr);
    assert.deepEqual(JSON.parse(s.stdout), { administrator_created: false, administrator_login_verified: true });
    s = run("bootstrap", secret, { SIM_NEEDS_SETUP: "yes", SIM_SETUP_OK: "no" });
    assert.notEqual(s.status, 0);
    s = run("bootstrap", secret, { SIM_NEEDS_SETUP: "no", SIM_LOGIN_OK: "no" });
    assert.notEqual(s.status, 0);
    for (const marker of ["DO-NOT-PRINT-THIS-TOKEN", "X".repeat(48)]) {
        assert.ok(!s.stdout.includes(marker) && !s.stderr.includes(marker));
    }
    console.log("PASS: Kuma 2.5.9 socket event contract bootstrap/repeat/failures, no credential output");
} finally {
    fs.rmSync(temp, { recursive: true, force: true });
}
