// Presses the page's own start button and reads the numbers it displays when the button leaves its running state.
import { navigate, until } from "../wait.js";

const number = (text) => (text === "" || text == null || Number.isNaN(Number(text)) ? null : Number(text));

export async function run(page, url, deadline) {
  await navigate(page, url, deadline);
  // Newer pages show a loading state until their server list is ready; the Go backend's older page has none.
  await until(page, `!!document.getElementById("startStopBtn") && ["hidden", undefined].includes(document.getElementById("loading")?.className)`, deadline);
  await page.evaluate(`document.getElementById("startStopBtn").click()`);
  await until(page, `document.getElementById("startStopBtn").className === "running"`, deadline);
  await until(page, `document.getElementById("startStopBtn").className === ""`, deadline);
  const text = await page.evaluate(
    `Object.fromEntries(["dlText", "ulText", "pingText", "jitText"].map((id) => [id, document.getElementById(id)?.textContent.trim() ?? ""]))`,
  );
  const download = number(text.dlText);
  const upload = number(text.ulText);
  return {
    outcome: download != null && upload != null ? "complete" : "incomplete",
    downloadMbit: download,
    uploadMbit: upload,
    idleLatencyMs: number(text.pingText),
    loadedLatencyDownMs: null,
    loadedLatencyUpMs: null,
    screen: Object.values(text),
    detail: { page: await page.evaluate("location.pathname"), jitterMs: number(text.jitText) },
  };
}
