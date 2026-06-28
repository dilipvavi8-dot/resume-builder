import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  use: { baseURL: "http://localhost:3001", screenshot: "only-on-failure" },
  reporter: "list",
});
