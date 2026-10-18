// Presses the page's own start control and reads the results it shows once its status reads "All done".
import { navigate, until } from "../wait.js";

const number = (text) => (text === "" || text == null || Number.isNaN(Number(text)) ? null : Number(text));

export async function run(page, url, deadline) {
  await navigate(page, url, deadline);
  // The controls are SVG elements, which have no click(); the page listens for a click event on them.
  await until(
    page,
    `(() => {
      const start = document.getElementById("startButtonDesk");
      if (!start || getComputedStyle(document.getElementById("loading_app")).display !== "none") return false;
      start.dispatchEvent(new MouseEvent("click", { bubbles: true }));
      return true;
    })()`,
    deadline,
  );
  await until(page, `document.getElementById("oDoLiveStatus")?.textContent.trim() === "All done"`, deadline);
  const text = await page.evaluate(
    `Object.fromEntries(["downResult", "upRestxt", "pingResult", "jitterDesk"].map((id) => [id, document.getElementById(id)?.textContent.trim() ?? ""]))`,
  );
  const download = number(text.downResult);
  const upload = number(text.upRestxt);
  return {
    outcome: download != null && upload != null ? "complete" : "incomplete",
    downloadMbit: download,
    uploadMbit: upload,
    idleLatencyMs: number(text.pingResult),
    loadedLatencyDownMs: null,
    loadedLatencyUpMs: null,
    screen: Object.values(text),
    detail: { jitterMs: number(text.jitterDesk) },
  };
}
