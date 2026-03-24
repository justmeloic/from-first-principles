import { expect, test } from "@playwright/test";

test.describe("Homepage", () => {
  test("loads successfully", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/From First Principles/i);
  });

  test("has main navigation links", async ({ page }) => {
    await page.goto("/");

    // Check for main nav elements
    await expect(page.getByRole("link", { name: /blog/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /engineering/i })).toBeVisible();
  });

  test("can navigate to blog", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: /blog/i }).click();
    await expect(page).toHaveURL(/\/blog/);
  });

  test("can navigate to engineering", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: /engineering/i }).click();
    await expect(page).toHaveURL(/\/engineering/);
  });
});
