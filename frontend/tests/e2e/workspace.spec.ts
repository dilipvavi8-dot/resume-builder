import { expect, test } from "@playwright/test";

const routes = [
  { path: "/dashboard", text: "Career command center" },
  { path: "/jobs", text: "Curated job feed" },
  { path: "/manual-jd", text: "Job description studio" },
  { path: "/resumes", text: "Resume library" },
  { path: "/tracker", text: "Application tracker" },
  { path: "/monitor", text: "Pipeline monitor" },
  { path: "/approvals", text: "Full-time review queue" },
];

for (const route of routes) {
  test(`loads ${route.path}`, async ({ page }) => {
    await page.goto(route.path, { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: route.text })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Failed to fetch")).toHaveCount(0);
    await expect(page.getByText("Runtime SyntaxError")).toHaveCount(0);
  });
}

test("dashboard fetch jobs button works", async ({ page }) => {
  await page.goto("/dashboard");
  await page.getByRole("button", { name: "Fetch jobs" }).click();
  await expect(page.getByText(/new roles saved|existing roles refreshed/)).toBeVisible({ timeout: 15_000 });
});

test("jobs feed re-score and mark applied work", async ({ page }) => {
  await page.goto("/jobs");
  await page.getByRole("button", { name: "Refresh feed" }).click();
  await expect(page.getByRole("button", { name: "Re-score" }).first()).toBeVisible({ timeout: 15_000 });
  await page.getByRole("button", { name: "Re-score" }).first().click();
  await expect(page.getByText(/evidence-based match/)).toBeVisible({ timeout: 15_000 });
  await page.getByRole("button", { name: "Mark applied" }).first().click();
  await expect(page.getByText(/added to your tracker/)).toBeVisible({ timeout: 15_000 });
});

test("notification bell opens and can mark read", async ({ page }) => {
  await page.goto("/dashboard");
  await page.getByRole("button", { name: "Open notifications" }).click();
  await expect(page.getByText("Notifications")).toBeVisible();
  const markRead = page.getByRole("button", { name: "Mark read" });
  if (await markRead.count()) {
    await markRead.click();
  }
});
