import { expect, test } from "@playwright/test";

test.describe("Agent Page", () => {
  test("loads agent page", async ({ page }) => {
    await page.goto("/agent");
    await expect(page).toHaveURL(/\/agent/);
  });

  test("has chat input", async ({ page }) => {
    await page.goto("/agent");
    await page.waitForLoadState("networkidle");

    // Look for the chat input (case insensitive)
    const chatInput = page.getByPlaceholder(/ask anything/i);
    await expect(chatInput).toBeVisible({ timeout: 10000 });
  });

  test("can type in chat input", async ({ page }) => {
    await page.goto("/agent");
    await page.waitForLoadState("networkidle");

    const chatInput = page.getByPlaceholder(/ask anything/i);
    await chatInput.waitFor({ state: "visible", timeout: 10000 });
    await chatInput.fill("Hello, how are you?");
    await expect(chatInput).toHaveValue("Hello, how are you?");
  });

  // Note: Actual message sending test would require backend to be running
  // and would be more of an integration test
});
