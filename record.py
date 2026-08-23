"""Record a video of the sphinx-pyxel demo page running the Pyxel app.

Playwright records the page into a webm. Pyxel's web runtime gates on a user
gesture, so we dispatch a click on document.body to start the app, then let it
run for RECORD_MS. The webm is dropped in videos/ and the path is printed.

Google Slides does not accept webm directly; convert to mp4 with ffmpeg if
available (printed at the end), otherwise upload the webm to Drive first.
"""

import os
import shutil
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001/index.html"
RECORD_MS = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
OUT_DIR = "videos"

os.makedirs(OUT_DIR, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1024, "height": 900},
            record_video_dir=OUT_DIR,
            record_video_size={"width": 1024, "height": 900},
        )
        page = context.new_page()

        page.goto(URL, wait_until="domcontentloaded")
        # Let pyodide + pyxel load and show the "CLICK TO START" gate.
        page.wait_for_timeout(4000)
        # Start the app (runtime listens for click on document.body).
        page.evaluate("document.body.click()")
        # Record the app running.
        page.wait_for_timeout(RECORD_MS)

        context.close()
        browser.close()

    # Playwright writes the video with a random name; find the newest webm.
    webm = max(
        (os.path.join(OUT_DIR, f) for f in os.listdir(OUT_DIR) if f.endswith(".webm")),
        key=os.path.getmtime,
    )
    final_webm = os.path.join(OUT_DIR, "sphinx_pyxel_demo.webm")
    shutil.move(webm, final_webm)
    print(f"webm: {final_webm}")

    # Try to convert to mp4 for Google Slides.
    if shutil.which("ffmpeg"):
        mp4 = os.path.join(OUT_DIR, "sphinx_pyxel_demo.mp4")
        code = os.system(f'ffmpeg -y -i "{final_webm}" -vf "fps=30" "{mp4}" >/dev/null 2>&1')
        if code == 0 and os.path.isfile(mp4):
            print(f"mp4: {mp4}")
            print("Upload the mp4 to Google Slides: Insert > Video > Google Drive")
            return
    print("ffmpeg not found or conversion failed.")
    print("Install ffmpeg (brew install ffmpeg) to get an mp4, or upload the webm to Drive.")


if __name__ == "__main__":
    main()
