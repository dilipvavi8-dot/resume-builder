import { expect, test } from "@playwright/test";

test("analyzes a JD without a browser fetch failure", async ({ page }) => {
  await page.goto("/manual-jd");
  await page.getByPlaceholder("Job title").fill("DevOps Engineer");
  await page.getByPlaceholder("Company").fill("Local verification");
  await page.getByPlaceholder("Paste the complete job description here...").fill(
    "DevOps engineer with AWS, Kubernetes, Docker, CI/CD, Terraform, Python, and production monitoring experience."
  );
  const analyzeButton = page.getByRole("button", { name: "Analyze match" });
  await expect(analyzeButton).toBeEnabled();
  await analyzeButton.click();
  await expect(page.getByText("Match result")).toBeVisible();
  await expect(page.getByText("Resume updater plan")).toBeVisible();
  await expect(page.getByText("Failed to fetch")).toHaveCount(0);
});

test("blocks final output when required skills are unsupported", async ({ page }) => {
  await page.goto("/manual-jd");
  await page.getByPlaceholder("Job title").fill("DevOps Engineer");
  await page.getByPlaceholder("Company").fill("Playwright verification");
  await page.getByPlaceholder("Paste the complete job description here...").fill(
    "DevOps engineer with AWS, Kubernetes, Docker, CI/CD, Terraform, Python, REST APIs, TypeScript, and Playwright."
  );
  await page.getByRole("button", { name: "Analyze match" }).click();
  await expect(page.getByText("Match result")).toBeVisible();
  await page.getByRole("button", { name: "Create reviewable resume draft" }).click();
  await expect(page.getByText("Resume draft — review required")).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText("TypeScript: gap — not added")).toBeVisible();
  await expect(page.getByText(/Final output is blocked/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Approve draft and generate DOCX" })).toHaveCount(0);
});

test("approves a gate-passing draft and exposes a download link", async ({ page }) => {
  await page.goto("/manual-jd");
  await page.getByPlaceholder("Job title").fill("DevOps Engineer");
  await page.getByPlaceholder("Company").fill("Playwright verification");
  await page.getByPlaceholder("Paste the complete job description here...").fill(
    "We are hiring a DevOps Engineer to own AWS infrastructure, manage EKS clusters, write Terraform modules, build GitHub Actions pipelines, and support Python automation with Prometheus and Grafana monitoring."
  );
  await page.getByRole("button", { name: "Analyze match" }).click();
  await expect(page.getByText("Match result")).toBeVisible();
  await page.getByRole("button", { name: "Create reviewable resume draft" }).click();
  await expect(page.getByText("Resume draft — review required")).toBeVisible({ timeout: 20_000 });
  await page.getByRole("button", { name: "Approve draft and generate DOCX" }).click();
  await expect(page.getByRole("link", { name: "Download verified DOCX" })).toBeVisible({ timeout: 20_000 });
});
