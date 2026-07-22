import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));
  page.__consoleErrors = consoleErrors;
  await page.goto("/qa/browser/site/");
  await page.waitForFunction(() => window.__zutatQa?.complete === true);
});

test("small UI metrics stay stable", async ({ page }) => {
  const qa = await page.evaluate(() => window.__zutatQa);
  expect(qa.failures, JSON.stringify(qa.checks, null, 2)).toEqual([]);
  expect(qa.checks.length).toBeGreaterThanOrEqual(35);
  expect(page.__consoleErrors).toEqual([]);
});

test("page has no horizontal overflow", async ({ page }) => {
  const overflow = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(overflow.content).toBeLessThanOrEqual(overflow.viewport + 1);
});

test("small UI visual regression", async ({ page }) => {
  await expect(page).toHaveScreenshot("zutat-font-small-ui.png", { fullPage: true });
});
