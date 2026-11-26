// Regression tests for the double-submit guard in api_calendar.js (issue #575).
// Run with: node --test tests/js/
// Uses only Node built-ins (node:test, node:vm); no dependencies to install.
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const SRC =
  process.env.API_CALENDAR_SRC ||
  path.join(__dirname, "../../ap_src/ap_app/static/js/api_calendar.js");
const source = fs.readFileSync(SRC, "utf8");

// Load the script into a fresh sandbox with minimal DOM/browser stubs.
// fetch() is controlled by the test so requests can be held in flight.
function load() {
  const fetchCalls = [];
  const pending = [];
  const state = { reloads: 0 };
  const fakeEl = () => ({ style: {}, dataset: {}, classList: { add() {}, remove() {} } });
  const location = { origin: "http://test", reload: () => state.reloads++ };
  const sandbox = {
    console: { log() {} },
    document: {
      currentScript: { getAttribute: () => "tok" },
      addEventListener() {},
      getElementById: () => fakeEl(),
      querySelectorAll: () => [],
    },
    window: { location },
    location,
    fetch: (url, opts) => {
      fetchCalls.push({ url, opts });
      return new Promise((resolve, reject) => pending.push({ resolve, reject }));
    },
  };
  sandbox.window.onclick = null;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox, { filename: SRC });
  return { sandbox, fetchCalls, pending, state };
}

const flush = () => new Promise((r) => setImmediate(r));

test("repeated sendData calls while a request is in flight send only one request", async () => {
  const { sandbox, fetchCalls, pending, state } = load();

  // Simulate a spam-click / slow response: three calls before the first resolves.
  sandbox.sendData("bob", "2026-01-05", false, "N", "add", "E");
  sandbox.sendData("bob", "2026-01-05", false, "N", "add", "E");
  sandbox.sendData("bob", "2026-01-05", false, "N", "add", "E");

  assert.strictEqual(fetchCalls.length, 1, "only one POST should be issued");
  assert.match(fetchCalls[0].url, /\/absence\/click_add$/);

  pending[0].resolve({ ok: true });
  await flush();
  assert.strictEqual(state.reloads, 1, "successful request reloads the page");
});

test("guard is released after a failed request so the user can retry", async () => {
  const { sandbox, fetchCalls, pending } = load();

  sandbox.sendData("bob", "2026-01-05", false, "N", "add", "E");
  assert.strictEqual(fetchCalls.length, 1);

  pending[0].reject(new Error("network down"));
  await flush();

  sandbox.sendData("bob", "2026-01-05", false, "N", "add", "E");
  assert.strictEqual(fetchCalls.length, 2, "retry after failure should send a new request");
});
