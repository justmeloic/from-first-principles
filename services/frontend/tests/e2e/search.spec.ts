import { expect, test } from "@playwright/test";

test.describe("Search Page", () => {
  test("loads search page", async ({ page }) => {
    await page.goto("/search");
    await expect(page).toHaveURL(/\/search/);
  });

  test("has search input", async ({ page }) => {
    await page.goto("/search");

    // Wait for page to be fully loaded
    await page.waitForLoadState("networkidle");

    // Look for search input (partial placeholder match)
    const searchInput = page.getByPlaceholder(/knowledge base/i);
    await expect(searchInput).toBeVisible();
  });

  test("can type in search input", async ({ page }) => {
    await page.goto("/search");
    await page.waitForLoadState("networkidle");

    const searchInput = page.getByPlaceholder(/knowledge base/i);
    await searchInput.fill("machine learning");
    await expect(searchInput).toHaveValue("machine learning");
  });
});
