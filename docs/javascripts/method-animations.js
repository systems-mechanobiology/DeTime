/* SPDX-License-Identifier: BSD-3-Clause */
/* Progressive enhancement: Markdown image links remain usable on GitHub. */
(() => {
  "use strict";

  function enhanceAnimations() {
    document.querySelectorAll('a[href$=".gif"] > img').forEach((image) => {
      if (!image.src.includes("/method-animations/") || image.dataset.animationReady) return;
      const link = image.parentElement;
      const paragraph = link.parentElement;
      const still = image.src;
      const gif = link.href;
      const method = image.alt.split(":")[0];
      const figure = document.createElement("figure");
      const button = document.createElement("button");
      const status = document.createElement("span");
      const fallback = document.createElement("p");
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
      let playing = false;
      let gifFailed = false;
      let posterFailed = false;

      image.dataset.animationReady = "true";
      image.loading = "lazy";
      image.decoding = "async";
      image.width = 1280;
      image.height = 820;
      figure.className = "method-animation";
      button.type = "button";
      button.className = "animation-toggle";
      button.textContent = "Play animation";
      button.setAttribute("aria-pressed", "false");
      button.setAttribute("aria-label", `Play ${method} animation`);
      status.className = "animation-status";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      status.textContent = reducedMotion.matches
        ? "Reduced motion is enabled. Static frame; playback starts only when you select Play animation."
        : "Static frame. Select Play animation to follow the four steps.";
      fallback.className = "animation-fallback";
      fallback.hidden = true;
      fallback.textContent = "The image preview is unavailable. Read the four steps below or use the direct image links.";
      link.setAttribute("aria-label", `Open ${method} GIF directly`);

      link.before(figure);
      figure.append(link, fallback, button, status);
      if (paragraph.tagName === "P" && paragraph.children.length === 1) {
        paragraph.replaceWith(figure);
      }

      function showStill(message) {
        playing = false;
        link.hidden = posterFailed;
        fallback.hidden = !posterFailed;
        image.src = still;
        button.textContent = "Play animation";
        button.setAttribute("aria-pressed", "false");
        button.setAttribute("aria-label", `Play ${method} animation`);
        status.textContent = message || (posterFailed
          ? "The static preview could not load. Try Play animation or use the direct image links below."
          : "Static frame. The GIF and source arrays are linked below.");
      }

      button.addEventListener("click", () => {
        if (playing) {
          showStill();
          return;
        }
        playing = true;
        gifFailed = false;
        link.hidden = false;
        fallback.hidden = true;
        image.src = gif;
        button.textContent = "Show still frame";
        button.setAttribute("aria-pressed", "true");
        button.setAttribute("aria-label", `Show ${method} still frame`);
        status.textContent = "Loading the GIF. Select Show still frame to cancel playback.";
      });

      image.addEventListener("load", () => {
        if (playing && image.src === gif) {
          status.textContent = "Playing a looping GIF. Select Show still frame to stop the animation.";
        } else if (image.src === still) {
          posterFailed = false;
          link.hidden = false;
          fallback.hidden = true;
        }
      });

      function handleImageError() {
        if (playing && image.src === gif) {
          gifFailed = true;
          showStill("The GIF could not load. Showing the static preview when available; try again or use the direct GIF link below.");
        } else if (image.src === still) {
          posterFailed = true;
          link.hidden = true;
          fallback.hidden = false;
          status.textContent = gifFailed
            ? "The GIF and static preview could not load. Read the four steps below or retry with the direct image links."
            : "The static preview could not load. Try Play animation or use the direct image links below.";
        }
      }
      image.addEventListener("error", handleImageError);
      // A cached image can fail before enhancement attaches its error listener.
      if (image.complete && image.naturalWidth === 0) handleImageError();

      // No autoplay, including when reduced motion is requested. If that
      // preference changes during playback, return to the static view.
      reducedMotion.addEventListener("change", (event) => {
        if (event.matches && playing) {
          showStill("Reduced motion is enabled. Playback stopped; select Play animation to start it explicitly.");
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhanceAnimations);
  } else {
    enhanceAnimations();
  }
})();
