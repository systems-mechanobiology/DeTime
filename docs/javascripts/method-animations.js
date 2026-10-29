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
      let playing = false;

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
      status.textContent = "Static frame. Select Play animation to follow the four steps.";

      link.before(figure);
      figure.append(link, button, status);
      if (paragraph.tagName === "P" && paragraph.children.length === 1) {
        paragraph.replaceWith(figure);
      }

      function showStill() {
        playing = false;
        image.src = still;
        button.textContent = "Play animation";
        button.setAttribute("aria-pressed", "false");
        button.setAttribute("aria-label", `Play ${method} animation`);
        status.textContent = "Static frame. The GIF and source arrays are linked below.";
      }

      button.addEventListener("click", () => {
        if (playing) {
          showStill();
          return;
        }
        playing = true;
        image.src = gif;
        button.textContent = "Show still frame";
        button.setAttribute("aria-pressed", "true");
        button.setAttribute("aria-label", `Show ${method} still frame`);
        status.textContent = "Playing a looping GIF. Select Show still frame to stop the animation.";
      });

      image.addEventListener("error", () => {
        if (playing) {
          showStill();
          status.textContent = "The GIF could not load. Try again or use the direct GIF link below.";
        }
      });

      // No autoplay, including when reduced motion is requested. If that
      // preference changes during playback, return to the static view.
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
      reducedMotion.addEventListener("change", (event) => {
        if (event.matches && playing) showStill();
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhanceAnimations);
  } else {
    enhanceAnimations();
  }
})();
