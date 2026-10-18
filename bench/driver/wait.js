// Polls an expression until it is truthy; navigation can briefly make evaluation fail, which counts as not yet.
export async function until(page, expression, deadline) {
  for (;;) {
    const value = await page.evaluate(expression).catch(() => null);
    if (value) return value;
    if (Date.now() > deadline) throw new Error(`timed out waiting for: ${expression.slice(0, 120)}`);
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
}

// A marker on the old document proves the new one replaced it before anything reads the page.
export async function navigate(page, url, deadline) {
  await page.evaluate("window.__benchOld = true").catch(() => {});
  await page.goto(url);
  await until(page, `!window.__benchOld && document.readyState === "complete"`, deadline);
}
