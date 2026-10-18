// The smallest browser control both engines share: navigate, evaluate, screenshot. No network domain is enabled and
// no request is intercepted, so the browser's traffic is exactly what the tool's page produces.
import { spawn } from "node:child_process";
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";

const PORT = 9222;

const FIREFOX_PREFS = {
  "app.update.disabledForTesting": true,
  "browser.shell.checkDefaultBrowser": false,
  "browser.startup.homepage_override.mstone": "ignore",
  "browser.aboutwelcome.enabled": false,
  "datareporting.policy.dataSubmissionEnabled": false,
  "toolkit.telemetry.reportingpolicy.firstRun": false,
};

function launchProcess(binary, args, banner) {
  // Its own process group, so quitting can kill every helper process the browser started.
  const child = spawn(binary, args, { stdio: ["ignore", "ignore", "pipe"], detached: true });
  return new Promise((resolve, reject) => {
    let log = "";
    const timer = setTimeout(() => reject(new Error(`no debugging endpoint from ${binary}:\n${log}`)), 30_000);
    child.stderr.on("data", (chunk) => {
      log += chunk;
      const match = banner.exec(log);
      if (match) {
        clearTimeout(timer);
        resolve({ child, endpoint: match[1] });
      }
    });
    child.on("exit", (code) => reject(new Error(`${binary} exited with ${code}:\n${log}`)));
  });
}

function connect(url) {
  const socket = new WebSocket(url);
  const pending = new Map();
  let next = 1;
  socket.onmessage = ({ data }) => {
    const message = JSON.parse(data);
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(`${message.error.message ?? message.error}: ${message.message ?? ""}`));
    else waiter.resolve(message.result);
  };
  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const id = next++;
      pending.set(id, { resolve, reject });
      socket.send(JSON.stringify({ id, method, params }));
    });
  return new Promise((resolve, reject) => {
    socket.onopen = () => resolve({ send, close: () => socket.close() });
    socket.onerror = () => reject(new Error(`cannot connect to ${url}`));
  });
}

// Expressions run as async functions and return JSON, so both protocols hand back the same plain values.
const wrap = (expression) => `(async () => JSON.stringify(await (${expression})))()`;

async function chrome(binary, profile) {
  const { child } = await launchProcess(
    binary,
    [
      `--user-data-dir=${profile}`,
      `--remote-debugging-port=${PORT}`,
      "--no-first-run",
      "--no-default-browser-check",
      "--no-sandbox",
      "--window-size=1280,900",
      "about:blank",
    ],
    /DevTools listening on (ws:\/\/\S+)/,
  );
  const targets = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
  const cdp = await connect(targets.find((target) => target.type === "page").webSocketDebuggerUrl);
  return {
    child,
    goto: (url) => cdp.send("Page.navigate", { url }),
    async evaluate(expression) {
      const { result, exceptionDetails } = await cdp.send("Runtime.evaluate", {
        expression: wrap(expression),
        awaitPromise: true,
        returnByValue: true,
      });
      if (exceptionDetails) throw new Error(exceptionDetails.exception?.description ?? exceptionDetails.text);
      return result.value === undefined ? undefined : JSON.parse(result.value);
    },
    screenshot: async () => (await cdp.send("Page.captureScreenshot", { format: "png" })).data,
    close: () => cdp.close(),
  };
}

async function firefox(binary, profile) {
  mkdirSync(profile, { recursive: true });
  writeFileSync(
    `${profile}/user.js`,
    Object.entries(FIREFOX_PREFS)
      .map(([key, value]) => `user_pref(${JSON.stringify(key)}, ${JSON.stringify(value)});`)
      .join("\n"),
  );
  const { child, endpoint } = await launchProcess(
    binary,
    ["-no-remote", "-profile", profile, "--remote-debugging-port", String(PORT), "-width", "1280", "-height", "900"],
    /WebDriver BiDi listening on (ws:\/\/\S+)/,
  );
  const bidi = await connect(`${endpoint}/session`);
  await bidi.send("session.new", { capabilities: {} });
  const { contexts } = await bidi.send("browsingContext.getTree", {});
  const context = contexts[0].context;
  return {
    child,
    goto: (url) => bidi.send("browsingContext.navigate", { context, url, wait: "none" }),
    async evaluate(expression) {
      const reply = await bidi.send("script.evaluate", {
        expression: wrap(expression),
        target: { context },
        awaitPromise: true,
        resultOwnership: "none",
      });
      if (reply.type === "exception") throw new Error(reply.exceptionDetails.text);
      return reply.result.type === "string" ? JSON.parse(reply.result.value) : undefined;
    },
    screenshot: async () => (await bidi.send("browsingContext.captureScreenshot", { context })).data,
    close: () => bidi.close(),
  };
}

const TICKS = 100;

// CPU seconds of the browser's whole process tree; exited children count through the main process's reaped time.
export function cpuSeconds(root) {
  const stats = new Map();
  for (const entry of readdirSync("/proc")) {
    if (!/^\d+$/.test(entry)) continue;
    try {
      const fields = readFileSync(`/proc/${entry}/stat`, "utf8").split(") ")[1].split(" ");
      stats.set(Number(entry), { ppid: Number(fields[1]), ticks: fields.slice(11, 15).map(Number) });
    } catch {}
  }
  const inTree = (pid) => {
    for (let p = pid; p > 1; p = stats.get(p)?.ppid ?? 0) if (p === root) return true;
    return false;
  };
  let ticks = 0;
  for (const [pid, { ticks: [utime, stime, cutime, cstime] }] of stats)
    if (inTree(pid)) ticks += utime + stime + (pid === root ? cutime + cstime : 0);
  return ticks / TICKS;
}

export async function launch(kind, binary, profile) {
  const browser = await (kind === "chrome" ? chrome : firefox)(binary, profile);
  return {
    ...browser,
    cpuSeconds: () => cpuSeconds(browser.child.pid),
    async quit() {
      browser.close();
      process.kill(-browser.child.pid, "SIGKILL");
    },
  };
}
