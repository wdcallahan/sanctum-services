"use strict";

/*
 * Uptime Kuma 2.5.9 native Socket.IO administrator initialization.
 * Executed exclusively INSIDE the running pinned Kuma image with Node.
 * The password arrives over stdin, never as an argv value or in output.
 * This is deliberately NOT a direct SQLite write or invented REST API.
 */
const { io } = require("socket.io-client");

const mode = process.argv[1];
if (!["status", "diagnose", "bootstrap"].includes(mode)) {
    process.stderr.write("Unsupported Kuma administrator operation\n");
    process.exit(2);
}

const socket = io("http://127.0.0.1:3001", {
    transports: ["websocket"],
    reconnection: false,
    timeout: 8000,
});

function waitForConnection() {
    return new Promise((resolve, reject) => {
        if (socket.connected) {
            resolve();
            return;
        }
        const timeout = setTimeout(() => reject(new Error("Kuma Socket.IO connect timeout")), 10000);
        socket.once("connect", () => {
            clearTimeout(timeout);
            resolve();
        });
        socket.once("connect_error", () => {
            clearTimeout(timeout);
            reject(new Error("Kuma Socket.IO connection rejected"));
        });
    });
}

function eventAck(event, ...args) {
    return new Promise((resolve, reject) => {
        socket.timeout(10000).emit(event, ...args, (err, reply) => {
            if (err) {
                reject(new Error("Kuma Socket.IO acknowledgement timed out"));
            } else {
                resolve(reply);
            }
        });
    });
}

function credentialsFromStdin() {
    // Ansible sends one JSON object through the process's stdin, not argv.
    // Synchronous fd-0 read has a deterministic EOF under podman exec -i
    // and under the source-only child_process simulation.
    const raw = require("node:fs").readFileSync(0, "utf8");
    const result = JSON.parse(raw);
    if (result.username !== "sanctum-admin"
        || typeof result.password !== "string"
        || result.password.length === 0) {
        throw new Error("Invalid private administrator secret format");
    }
    return result;
}

async function main() {
    // Read the Vault-decrypted secret from stdin, never from arguments or disk
    // inside the managed container. Status is intentionally unauthenticated.
    const credentials = mode === "status" ? null : credentialsFromStdin();
    await waitForConnection();

    // These events and argument positions are from tagged upstream 2.5.9.
    const needsSetup = await eventAck("needSetup");
    if (typeof needsSetup !== "boolean") {
        throw new Error("Unexpected Kuma initial-setup status");
    }
    if (mode === "status") {
        process.stdout.write(JSON.stringify({ needs_setup: needsSetup }) + "\n");
        return;
    }
    if (mode === "diagnose") {
        // Exactly the dependency already used by tagged upstream Kuma 2.5.9.
        // This is read-only: no "setup", "login", database or monitor writes.
        const { passwordStrength } = require("check-password-strength");
        const upstreamAllows = passwordStrength(credentials.password).value !== "Too weak";
        process.stdout.write(JSON.stringify({
            needs_setup: needsSetup,
            password_meets_upstream_setup_rule: upstreamAllows,
        }) + "\n");
        return;
    }

    if (needsSetup) {
        // The upstream handler refuses setup once a user already exists.
        const setup = await eventAck("setup", credentials.username, credentials.password);
        if (!setup || setup.ok !== true) {
            throw new Error("Kuma rejected one-time administrator initialization");
        }
    }

    // No password, token, raw login response or app cookies enter stdout.
    const auth = await eventAck("login", {
        username: credentials.username,
        password: credentials.password,
    });
    if (!auth || auth.ok !== true) {
        throw new Error("Kuma administrator login verification failed");
    }
    process.stdout.write(JSON.stringify({
        administrator_created: needsSetup,
        administrator_login_verified: true,
    }) + "\n");
}

main().catch(() => {
    // Deliberately no raw exception / server response: these are auth paths.
    process.stderr.write("Kuma administrator operation failed (private details suppressed)\n");
    process.exitCode = 1;
}).finally(() => socket.disconnect());
