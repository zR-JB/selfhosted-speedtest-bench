// Runs one tool once in one browser inside the client container and prints the result as one JSON line.
import { rmSync, writeFileSync } from "node:fs";
import { launch } from "./browser.js";

const { tool, browser, binary, url, screenshot, timeoutMs } = JSON.parse(process.argv[2]);
const { run } = await import(`./adapters/${tool}.js`);
const profile = `/tmp/profile-${process.pid}`;
const page = await launch(browser, binary, profile);
const output = { startedAt: Date.now() };
try {
  const cpuBefore = page.cpuSeconds();
  Object.assign(output, await run(page, url, Date.now() + timeoutMs));
  output.browserCpuSeconds = page.cpuSeconds() - cpuBefore;
} catch (error) {
  output.outcome = "harness-error";
  output.error = String(error.stack ?? error);
} finally {
  output.endedAt = Date.now();
  writeFileSync(screenshot, Buffer.from(await page.screenshot().catch(() => ""), "base64"));
  await page.quit();
  rmSync(profile, { recursive: true, force: true });
}
console.log(JSON.stringify(output));
