// SPDX-License-Identifier: BSD-3-Clause
const fs = require("node:fs");
const path = require("node:path");
const { test, expect } = require("@playwright/test");
const { PNG } = require("pngjs");

const manifest = JSON.parse(fs.readFileSync(
  path.join(__dirname, "../../docs/assets/generated/method-animations/manifest.json"),
  "utf8",
));
const methods = manifest.methods;
const representatives = new Set(["SSA", "MVMD", "NBEATS_INTERPRETABLE"]);

if (methods.length !== 31 || new Set(methods.map((row) => row.slug)).size !== 31) {
  throw new Error("Browser acceptance requires the complete, unique 31-entry manifest.");
}

function controls(page) {
  const figure = page.locator("figure.method-animation");
  return {
    figure,
    image: figure.locator("img"),
    toggle: figure.locator("button.animation-toggle"),
    status: figure.locator('[role="status"]'),
  };
}

async function visit(page, slug) {
  const response = await page.goto(`gallery/${slug}/`, { waitUntil: "domcontentloaded" });
  expect(response && response.ok(), `${slug} page must be served successfully`).toBeTruthy();
  const view = controls(page);
  await expect(view.figure).toHaveCount(1);
  await view.figure.scrollIntoViewIfNeeded();
  await expect(view.toggle).toBeVisible();
  return view;
}

async function loaded(image, extension) {
  await expect(image).toBeVisible();
  await expect.poll(async () => image.evaluate((element, suffix) => (
    element.complete && element.naturalWidth > 0 && element.naturalHeight > 0
    && new URL(element.currentSrc).pathname.endsWith(suffix)
  ), extension), { message: `Browser must decode the ${extension} image` }).toBe(true);
}

async function activate(toggle, mobile) {
  if (mobile) await toggle.tap();
  else await toggle.click();
}

async function assertNoHorizontalOverflow(page) {
  const widths = await page.evaluate(() => ({
    viewport: window.innerWidth,
    document: document.documentElement.scrollWidth,
    body: document.body.scrollWidth,
  }));
  expect(Math.max(widths.document, widths.body), JSON.stringify(widths))
    .toBeLessThanOrEqual(widths.viewport + 2);
}

function plotDifference(beforeBytes, afterBytes) {
  const before = PNG.sync.read(beforeBytes);
  const after = PNG.sync.read(afterBytes);
  expect([after.width, after.height]).toEqual([before.width, before.height]);
  // Inspect the plotted data area, excluding the animated heading, progress
  // bar and captions. A changing progress bar cannot satisfy this check.
  const x0 = Math.ceil(before.width * 50 / 1280);
  const x1 = Math.floor(before.width * 1250 / 1280);
  const y0 = Math.ceil(before.height * 175 / 820);
  const y1 = Math.floor(before.height * 685 / 820);
  let changed = 0;
  let pixels = 0;
  for (let y = y0; y < y1; y += 1) {
    for (let x = x0; x < x1; x += 1) {
      const offset = (y * before.width + x) * 4;
      const delta = Math.max(...[0, 1, 2].map((channel) => (
        Math.abs(before.data[offset + channel] - after.data[offset + channel])
      )));
      if (delta >= 24) changed += 1;
      pixels += 1;
    }
  }
  return changed / pixels;
}

async function proveAnimationMoves(image, testInfo) {
  const started = Date.now();
  const before = await image.screenshot({ animations: "allow" });
  let after;
  let changedRatio = 0;
  await expect.poll(async () => {
    after = await image.screenshot({ animations: "allow" });
    changedRatio = plotDifference(before, after);
    return changedRatio;
  }, {
    message: "Decoded GIF must visibly change the plotted data, not only its heading",
    timeout: 16000,
    intervals: [200, 350, 600, 900, 1500],
  }).toBeGreaterThan(0.0008);
  await testInfo.attach("gif-plot-before", { body: before, contentType: "image/png" });
  await testInfo.attach("gif-plot-after", { body: after, contentType: "image/png" });
  await testInfo.attach("gif-motion-evidence", {
    body: Buffer.from(JSON.stringify({
      changedPlotPixelRatio: changedRatio,
      minimumRequiredRatio: 0.0008,
      elapsedMs: Date.now() - started,
      sourcePixelCrop: { x: [50, 1250], y: [175, 685], width: 1280, height: 820 },
    }, null, 2)),
    contentType: "application/json",
  });
}

test("Gallery exposes all 31 method pages", async ({ page, baseURL }) => {
  const response = await page.goto("gallery/", { waitUntil: "domcontentloaded" });
  expect(response && response.ok()).toBeTruthy();
  const content = page.getByRole("main");
  await expect(content).toBeVisible();
  const links = await content.locator("a[href]").evaluateAll((anchors) => (
    anchors.map((anchor) => new URL(anchor.href).pathname)
  ));
  for (const row of methods) {
    expect(links, `${row.method} must be discoverable in the Gallery content`)
      .toContain(new URL(`gallery/${row.slug}/`, baseURL).pathname);
    await expect(content.getByRole("link", { name: row.method, exact: true })).toBeVisible();
  }
  await assertNoHorizontalOverflow(page);
});

test("Gallery navigation opens, closes and reaches its last and first methods", async (
  { page, baseURL, isMobile }, testInfo,
) => {
  await page.goto("gallery/", { waitUntil: "domcontentloaded" });
  const navigation = page.locator(".navbar.fixed-top");
  const collapseToggle = navigation.getByRole("button", { name: "Toggle navigation", exact: true });
  const galleryToggle = navigation.getByRole("button", { name: "Gallery", exact: true });
  const menu = galleryToggle.locator("..").locator(":scope > .dropdown-menu");
  if (isMobile) {
    await activate(collapseToggle, true);
    await expect(collapseToggle).toHaveAttribute("aria-expanded", "true");
  }
  await activate(galleryToggle, isMobile);
  await expect(galleryToggle).toHaveAttribute("aria-expanded", "true");
  await expect(menu).toBeVisible();
  const last = menu.getByRole("link", { name: "XPATCH_BLOCK", exact: true });
  await last.scrollIntoViewIfNeeded();
  await expect(last).toBeInViewport();
  await testInfo.attach("gallery-menu-last-entry", {
    body: await page.screenshot(), contentType: "image/png",
  });
  await activate(galleryToggle, isMobile);
  await expect(galleryToggle).toHaveAttribute("aria-expanded", "false");
  await expect(menu).toBeHidden();
  if (isMobile) {
    await activate(collapseToggle, true);
    await expect(collapseToggle).toHaveAttribute("aria-expanded", "false");
  }

  for (const [name, slug] of [["XPATCH_BLOCK", "xpatch-block"], ["SSA", "ssa"]]) {
    if (isMobile) {
      await activate(collapseToggle, true);
      await expect(collapseToggle).toHaveAttribute("aria-expanded", "true");
    }
    await activate(galleryToggle, isMobile);
    const link = menu.getByRole("link", { name, exact: true });
    await link.scrollIntoViewIfNeeded();
    await expect(link).toBeInViewport();
    await activate(link, isMobile);
    await expect(page).toHaveURL(new URL(`gallery/${slug}/`, baseURL).href);
    await expect(page.getByRole("heading", { name: "How it works", exact: true })).toBeVisible();
  }
});

for (const row of methods) {
  test(`${row.method}: static preview, playback, stop and responsive layout`, async (
    { page, isMobile }, testInfo,
  ) => {
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const view = await visit(page, row.slug);
    await loaded(view.image, ".png");
    await expect(view.toggle).toHaveAttribute("aria-pressed", "false");
    await expect(view.toggle).toHaveAccessibleName(/play/i);
    await assertNoHorizontalOverflow(page);
    await activate(view.toggle, isMobile);
    await loaded(view.image, ".gif");
    await expect(view.toggle).toHaveAttribute("aria-pressed", "true");
    await expect(view.status).toContainText(/playing/i);
    if (representatives.has(row.method)) {
      await proveAnimationMoves(view.image, testInfo);
    }
    await activate(view.toggle, isMobile);
    await loaded(view.image, ".png");
    await expect(view.toggle).toHaveAttribute("aria-pressed", "false");
    await assertNoHorizontalOverflow(page);
    await testInfo.attach(`${row.slug}-static-controls`, {
      body: await view.figure.screenshot(), contentType: "image/png",
    });
    if (representatives.has(row.method)) {
      await testInfo.attach(`${row.slug}-viewport`, {
        body: await page.screenshot(), contentType: "image/png",
      });
    }
    expect(errors).toEqual([]);
  });
}

test("SSA control works with Tab, Enter and Space", async ({ page }) => {
  const view = await visit(page, "ssa");
  await loaded(view.image, ".png");
  await view.figure.locator("a").first().focus();
  await page.keyboard.press("Tab");
  await expect(view.toggle).toBeFocused();
  await page.keyboard.press("Enter");
  await loaded(view.image, ".gif");
  await expect(view.toggle).toHaveAttribute("aria-pressed", "true");
  await page.keyboard.press("Space");
  await loaded(view.image, ".png");
  await expect(view.toggle).toHaveAttribute("aria-pressed", "false");
});

test("Reduced motion starts static and a preference change stops playback", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const view = await visit(page, "ssa");
  await loaded(view.image, ".png");
  await expect(view.toggle).toHaveAttribute("aria-pressed", "false");
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await view.toggle.click();
  await loaded(view.image, ".gif");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await loaded(view.image, ".png");
  await expect(view.toggle).toHaveAttribute("aria-pressed", "false");
});

test("Failed GIF restores the still image and an actionable status", async ({ page }) => {
  await page.route(/\/method-animations\/ssa\.gif(?:\?.*)?$/, (route) => route.abort());
  const view = await visit(page, "ssa");
  await loaded(view.image, ".png");
  await view.toggle.click();
  await expect(view.status).toContainText(/gif/i);
  await expect(view.status).toContainText(/could not|cannot|unavailable|failed|failure|error/i);
  await loaded(view.image, ".png");
  await expect(view.toggle).toHaveAttribute("aria-pressed", "false");
  await expect(view.toggle).toBeEnabled();
});

test("Failed preview and GIF retain the explanation and permit retry", async ({ page }) => {
  const gif = /\/method-animations\/ssa\.gif(?:\?.*)?$/;
  await page.route(/\/method-animations\/ssa\.png(?:\?.*)?$/, (route) => route.abort());
  await page.route(gif, (route) => route.abort());
  const view = await visit(page, "ssa");
  await expect(view.status).toContainText(/preview|static|still|image/i);
  await expect(view.status).toContainText(/could not|cannot|unavailable|failed|failure|error/i);
  await expect(view.toggle).toBeEnabled();
  await view.toggle.click();
  await expect(view.status).toContainText(/could not|cannot|unavailable|failed|failure|error/i);
  await expect(view.toggle).toHaveAttribute("aria-pressed", "false");
  await expect(page.getByRole("heading", { name: "How it works", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Follow the four steps", exact: true })).toBeVisible();
  await page.unroute(gif);
  await view.toggle.click();
  await loaded(view.image, ".gif");
  await expect(view.toggle).toHaveAttribute("aria-pressed", "true");
});

test.describe("Without JavaScript", () => {
  test.use({ javaScriptEnabled: false });
  test("The static preview and direct GIF link remain usable", async ({ page, request }) => {
    const response = await page.goto("gallery/ssa/", { waitUntil: "domcontentloaded" });
    expect(response && response.ok()).toBeTruthy();
    const link = page.locator('a[href$="method-animations/ssa.gif"]').filter({ has: page.locator("img") });
    const image = link.locator("img");
    await image.scrollIntoViewIfNeeded();
    await loaded(image, ".png");
    await expect(page.locator(".animation-toggle")).toHaveCount(0);
    const target = await link.evaluate((element) => element.href);
    const gif = await request.get(target);
    expect(gif.ok()).toBeTruthy();
    expect(gif.headers()["content-type"]).toContain("image/gif");
  });
});
