// Presses the page's own "Start test" and reads the result it saves to History, the same record its History view shows.
import { navigate, until } from "../wait.js";

const readLatest = (after) => `new Promise((resolve) => {
  const open = indexedDB.open("graphite-meter");
  open.onerror = () => resolve(null);
  open.onsuccess = () => {
    const db = open.result;
    if (!db.objectStoreNames.contains("results")) return resolve(null);
    const all = db.transaction("results").objectStore("results").getAll();
    all.onsuccess = () => resolve(all.result.filter((r) => r.completedAt >= ${after}).sort((a, b) => b.completedAt - a.completedAt)[0] ?? null);
    all.onerror = () => resolve(null);
  };
})`;

const START = `(() => {
  const button = [...document.querySelectorAll("button")].find((b) =>
    [b.textContent, b.getAttribute("aria-label")].some((label) => label?.trim().startsWith("Start test")));
  if (!button || button.disabled) return false;
  button.click();
  return true;
})()`;

const mbit = (stage) => (stage?.reportedBytesPerSec == null ? null : (stage.reportedBytesPerSec * 8) / 1e6);

export async function run(page, url, deadline, options = {}) {
  await navigate(page, url, deadline);
  // History is a display preference; measurement settings stay the defaults unless a variant sets a documented one.
  const stored = JSON.stringify({ resultHistoryPreference: "enabled", ...(options.config ? { config: options.config } : {}) });
  await page.evaluate(`localStorage.setItem("graphite-meter:v1", ${JSON.stringify(stored)})`);
  await navigate(page, url, deadline);
  const startedAt = await page.evaluate("Date.now()");
  // A press before the page has checked its connection path is ignored, so press until the run leaves idle.
  await until(page, START, deadline);
  await until(page, `document.querySelector("#console")?.dataset.phase !== "idle" || (${START} && false)`, deadline);
  await until(page, `["complete", "aborted", "error"].includes(document.querySelector("#console")?.dataset.phase)`, deadline);
  const record = await until(page, readLatest(startedAt), deadline);
  const result = record.result;
  const latency = result.latencyByStage ?? {};
  return {
    outcome: result.outcome,
    downloadMbit: mbit(result.download),
    uploadMbit: mbit(result.upload),
    idleLatencyMs: latency.latency?.p50Ms ?? null,
    loadedLatencyDownMs: latency.download?.p50Ms ?? null,
    loadedLatencyUpMs: latency.upload?.p50Ms ?? null,
    screen: await page.evaluate(
      `[...document.querySelectorAll(".results .card .headline")].map((h) => h.textContent.replace(/\\s+/g, " ").trim())`,
    ),
    detail: {
      engineVersion: record.engine,
      protocol: result.multiServer?.servers?.[0]?.throughput ?? null,
      participants: result.multiServer?.participants ?? null,
    },
  };
}
