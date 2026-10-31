# Method animation browser acceptance

These tests exercise the built MkDocs site in real Chromium, at a 1440 × 1000
desktop viewport and a 390 × 844 mobile viewport with touch emulation. Mobile
emulation covers responsive rendering and touch controls; it does not claim
physical-device or Safari testing.

The manifest supplies all 31 method pages. Every page must load a static PNG,
play a decoded GIF on request, return to the still image, and avoid horizontal
page overflow. Additional checks cover all 31 links in the Gallery content,
opening and closing navigation, reaching the first and last menu items,
Tab/Enter/Space, changing reduced-motion preferences, failed image requests, retry, and
the static experience with JavaScript disabled.

SSA, MVMD, and NBEATS_INTERPRETABLE must show a measurable change between two
browser screenshots inside the plotted data area. Animated headings and
progress bars are excluded from that comparison. Screenshots and the measured
pixel difference are attached to the HTML report; each method also has a
desktop and mobile screenshot of its static preview and controls.

The docs CI job installs the pinned dependencies and Chromium, then runs these
tests after the strict MkDocs build. Its `de-time-browser-acceptance` artifact
contains the HTML/JSON report, screenshots, and failure traces.

The Pages workflow repeats the checks against its deployment URL after
publishing. It first waits up to five minutes for the exact manifest SHA-256,
complete Gallery index, and all 31 animation pages to appear publicly; each
HTTP request has an eight-second deadline. A failed public check fails that
workflow even if the deployment step itself completed. The separate
`de-time-public-browser-acceptance` artifact contains the public-site evidence.

For a checkout with a freshly built `site/` directory:

```sh
cd tests/browser
npm ci
npx playwright install --with-deps chromium
npm test
```

To check the publicly deployed site with the same tests:

```sh
DETIME_BASE_URL=https://systems-mechanobiology.github.io/DeTime/ npm test
```

Supplying `DETIME_BASE_URL` disables the local web server. The test result then
describes that remote site, without falling back to checkout HTML.
