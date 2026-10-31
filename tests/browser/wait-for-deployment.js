// SPDX-License-Identifier: BSD-3-Clause
// Wait for the public Pages deployment before testing it. No browser is started
// here, and a failed public check never substitutes a local build.
const fs = require("node:fs");
const path = require("node:path");
const { createHash } = require("node:crypto");
const { isDeepStrictEqual } = require("node:util");
const { setTimeout: delay } = require("node:timers/promises");

const manifestPath = path.join(
  __dirname, "../../docs/assets/generated/method-animations/manifest.json",
);
const expectedBytes = fs.readFileSync(manifestPath);
const expectedHash = createHash("sha256").update(expectedBytes).digest("hex");
const methods = JSON.parse(expectedBytes).methods;
const deploymentURL = process.env.DETIME_BASE_URL;
if (!deploymentURL) throw new Error("DETIME_BASE_URL is required for public deployment verification.");
const baseURL = new URL(`${deploymentURL.replace(/\/+$/, "")}/`);
if (!["https:", "http:"].includes(baseURL.protocol)) {
  throw new Error("DETIME_BASE_URL must be an HTTP(S) site URL.");
}

const deadline = Date.now() + 300000;
let attempt = 0;

async function fetchCurrent(relativePath) {
  const remaining = deadline - Date.now();
  if (remaining <= 0) throw new Error("Public deployment did not become ready within five minutes.");
  const url = new URL(relativePath, baseURL);
  url.searchParams.set("deployment-check", `${expectedHash.slice(0, 12)}-${attempt}`);
  try {
    const response = await fetch(url, {
      signal: AbortSignal.timeout(Math.min(8000, remaining)),
      headers: { "Cache-Control": "no-cache", "User-Agent": "DeTime-Pages-acceptance" },
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { bytes: Buffer.from(await response.arrayBuffer()), url };
  } catch (error) {
    throw new Error(`${relativePath}: ${error.message}`);
  }
}

async function checkPublishedVersion() {
  const manifest = await fetchCurrent("assets/generated/method-animations/manifest.json");
  const remoteHash = createHash("sha256").update(manifest.bytes).digest("hex");
  if (remoteHash !== expectedHash) {
    throw new Error(`Manifest is still ${remoteHash.slice(0, 12)}; expected ${expectedHash.slice(0, 12)}.`);
  }

  const index = await fetchCurrent("gallery/");
  const links = [...index.bytes.toString("utf8").matchAll(/href=(["'])(.*?)\1/g)]
    .map((match) => new URL(match[2], index.url).pathname);
  for (const row of methods) {
    if (!links.includes(new URL(`gallery/${row.slug}/`, baseURL).pathname)) {
      throw new Error(`Gallery does not yet expose ${row.method}.`);
    }
  }

  // Bound each request to eight seconds and verify at most eight pages at once.
  for (let offset = 0; offset < methods.length; offset += 8) {
    const checks = await Promise.allSettled(methods.slice(offset, offset + 8).map(async (row) => {
      const page = await fetchCurrent(`gallery/${row.slug}/`);
      const html = page.bytes.toString("utf8");
      for (const marker of [`${row.slug}.gif`, `${row.slug}.png`, "method-animations.js"]) {
        if (!html.includes(marker)) throw new Error(`${row.method} is missing ${marker}.`);
      }
    }));
    const failure = checks.find((check) => check.status === "rejected");
    if (failure) throw failure.reason;
  }

  // A current manifest alone cannot establish that the images and numerical
  // files reached the public site. Read every artifact and check its bytes.
  const assets = methods.flatMap((row) => [
    ...["gif", "poster", "data"].map((kind) => ({
      relativePath: `assets/generated/method-animations/${row.artifacts[kind].file}`,
      artifact: row.artifacts[kind],
    })),
    { relativePath: `assets/generated/method-animations/${row.slug}.json`, row },
  ]);
  for (let offset = 0; offset < assets.length; offset += 8) {
    const checks = await Promise.allSettled(assets.slice(offset, offset + 8).map(async (asset) => {
      const { bytes } = await fetchCurrent(asset.relativePath);
      if (asset.artifact) {
        const actualHash = createHash("sha256").update(bytes).digest("hex");
        if (bytes.length !== asset.artifact.bytes || actualHash !== asset.artifact.sha256) {
          throw new Error(
            `${asset.relativePath}: expected ${asset.artifact.bytes} bytes / SHA-256 ${asset.artifact.sha256}; `
            + `received ${bytes.length} bytes / SHA-256 ${actualHash}.`,
          );
        }
      } else {
        let metadata;
        try {
          metadata = JSON.parse(bytes.toString("utf8"));
        } catch (error) {
          throw new Error(`${asset.relativePath}: invalid JSON (${error.message}).`);
        }
        if (!isDeepStrictEqual(metadata, asset.row)) {
          const actual = metadata && typeof metadata === "object" ? metadata : {};
          const keys = new Set([...Object.keys(actual), ...Object.keys(asset.row)]);
          const different = [...keys].filter((key) => !isDeepStrictEqual(actual[key], asset.row[key]));
          throw new Error(`${asset.relativePath}: metadata differs from its manifest row in ${different.join(", ")}.`);
        }
      }
    }));
    const failures = checks.filter((check) => check.status === "rejected");
    if (failures.length) throw new Error(failures.map((check) => check.reason.message).join(" | "));
  }
}

async function main() {
  let lastError;
  while (Date.now() < deadline) {
    attempt += 1;
    try {
      await checkPublishedVersion();
      console.log(
        `Public Pages version verified: manifest ${expectedHash}; ${methods.length} method pages; `
        + `${methods.length * 3} GIF/PNG/NPZ artifacts match exact SHA-256 and byte counts; `
        + `${methods.length} metadata JSON files match their manifest rows at ${baseURL}.`,
      );
      return;
    } catch (error) {
      lastError = error;
      console.log(`Deployment propagation check ${attempt}: ${error.message}`);
    }
    const remaining = deadline - Date.now();
    if (remaining > 0) await delay(Math.min(10000, remaining));
  }
  throw new Error(`Public Pages verification timed out: ${lastError?.message || "no successful response"}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
