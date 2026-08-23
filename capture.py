"""Capture a screenshot of the sphinx-pyxel demo page and report Pyxel runtime status.

Opens the served page, waits for the Pyxel canvas, captures a screenshot, and
prints any console errors / page errors. Exits non-zero if no <canvas> appears
inside a .pyxel-app container (the runtime's tell that the app booted).
"""

import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001/index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "screenshot.png"
WAIT_MS = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

errors = []
console_lines = []


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1024, "height": 900})

        page.on("console", lambda m: console_lines.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))

        response = page.goto(URL, wait_until="domcontentloaded")
        print(f"HTTP {response.status if response else 'n/a'}  {URL}")

        # Give the runtime time to boot pyodide + show the start gate.
        page.wait_for_timeout(4000)

        apps = page.query_selector_all(".pyxel-app")
        print(f".pyxel-app containers: {len(apps)}")

        # The web runtime shows a "CLICK TO START" overlay and only creates the
        # canvas after a user gesture on document.body (browser autoplay policy).
        page.evaluate("document.body.click()")
        print("dispatched click on document.body")
        page.wait_for_timeout(WAIT_MS)

        canvases = page.query_selector_all("body canvas")
        print(f"canvases on body: {len(canvases)}")
        pyxel_run_play = page.query_selector_all("pyxel-run, pyxel-play")
        print(f"pyxel-run/play elements: {len(pyxel_run_play)}")
        for i, t in enumerate(pyxel_run_play):
            inner = t.inner_html()
            print(f"  [{i}] <{t.evaluate('e=>e.tagName.toLowerCase()')}> "
                  f"children={len(t.query_selector_all('*'))} innerLen={len(inner)}")

        page.screenshot(path=OUT, full_page=True)
        print(f"screenshot: {OUT}")

        print("\n--- console ---")
        for line in console_lines:
            print(line)
        print("\n--- page errors ---")
        for e in errors:
            print(e)

        browser.close()
        ok = len(canvases) > 0
        print(f"\nRESULT: {'OK' if ok else 'FAIL'} (canvas present = app booted)")
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
