// SPDX-License-Identifier: BSD-3-Clause
const path = require("node:path");
const { defineConfig, devices } = require("@playwright/test");

const remoteURL = process.env.DETIME_BASE_URL;
const baseURL = remoteURL
  ? `${remoteURL.replace(/\/+$/, "")}/`
  : "http://127.0.0.1:8765/";

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: "**/*.spec.js",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: 2,
  timeout: 45000,
  expect: { timeout: 12000 },
  outputDir: path.join(__dirname, "test-results"),
  reporter: [
    ["list"],
    ["html", { outputFolder: path.join(__dirname, "playwright-report"), open: "never" }],
    ["json", { outputFile: path.join(__dirname, "test-results/results.json") }],
  ],
  use: {
    baseURL,
    browserName: "chromium",
    actionTimeout: 12000,
    navigationTimeout: 30000,
    reducedMotion: "no-preference",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "desktop-chromium",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 1000 } },
    },
    {
      name: "mobile-chromium",
      use: {
        ...devices["Pixel 5"],
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 1,
      },
    },
  ],
  // The same tests can inspect the deployed /DeTime/ site. A remote URL must
  // never start a local server or silently fall back to a local build.
  webServer: remoteURL ? undefined : {
    command: "python3 -m http.server 8765 --bind 127.0.0.1 --directory ../../site",
    cwd: __dirname,
    url: baseURL,
    reuseExistingServer: false,
    timeout: 15000,
    stdout: "ignore",
    stderr: "pipe",
  },
});
