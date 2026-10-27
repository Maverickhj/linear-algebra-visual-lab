"""Optional Chromium checks: real pages, interactions, and offline resources.

Install Playwright separately; no browser tooling is required to read the lab.
Uses CHROMIUM_PATH, system Chromium, or Playwright's installed browser.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
import tempfile
from threading import Thread

from playwright.sync_api import Error, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
UNIT = "visualizations/vector-addition/"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def check_no_overflow(page):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "page overflows"


def main():
    errors = []
    external = []
    missing = []
    handler = partial(QuietHandler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server, sync_playwright() as p:
        Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_port}"
        executable = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium")
        browser = p.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])
        try:
            context = browser.new_context(viewport={"width": 1280, "height": 1000})
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("response", lambda response: missing.append(response.url) if response.status >= 400 else None)

            def local_only(route):
                if route.request.url.startswith(origin + "/"):
                    route.continue_()
                else:
                    external.append(route.request.url)
                    route.abort()

            page.route("http**://**/*", local_only)
            page.goto(origin + "/", wait_until="networkidle")
            assert page.locator(".unit").count() == 1
            check_no_overflow(page)
            page.set_viewport_size({"width": 390, "height": 1000})
            check_no_overflow(page)
            page.set_viewport_size({"width": 1280, "height": 1000})
            page.get_by_role("link", name="打开交互实验 →").click()
            page.wait_for_selector("#diagram svg")
            assert page.locator("#sum-value").inner_text() == "(3, 3)"
            assert page.locator('[data-vector="sum"]').get_attribute("x2") == "428"
            check_no_overflow(page)

            # Browser keyboard operates a range input; number input stays in sync.
            page.locator("#ax").focus()
            page.keyboard.press("ArrowRight")
            assert page.locator("#ax-number").input_value() == "2.5"
            assert page.locator("#sum-value").inner_text() == "(3.5, 3)"
            page.locator("#by-number").fill("-3")
            assert page.locator("#by").input_value() == "-3"
            assert page.locator("#sum-value").inner_text() == "(3.5, -2)"
            assert page.locator('[data-vector="sum"]').get_attribute("y2") == "372"

            # All invalid inputs preserve the last valid model and show a message.
            for value in ("99", "0.1", ""):
                page.locator("#ax-number").fill(value)
                assert page.locator("#sum-value").inner_text() == "(3.5, -2)"
                assert page.locator("#ax-number").get_attribute("aria-invalid") == "true"
                assert "最后一次有效" in page.locator("#status").inner_text()
            page.get_by_role("button", name="恢复默认").click()
            assert page.locator("#sum-value").inner_text() == "(3, 3)"
            assert page.locator("#status").inner_text() == ""
            assert page.locator('[aria-invalid="true"]').count() == 0

            page.get_by_role("button", name="相互抵消").click()
            assert page.locator("#sum-value").inner_text() == "(0, 0)"
            assert page.locator('[data-vector="sum"]').count() == 0
            assert page.locator('[data-zero="sum"]').count() == 1
            page.get_by_role("button", name="含零向量").click()
            assert page.locator("#sum-value").inner_text() == "(1, 2)"
            assert page.locator('[data-vector="a"]').count() == 0
            assert page.locator('[data-zero="a"]').count() == 1

            page.get_by_role("button", name="恢复默认").click()
            for width in (1280, 390):
                page.set_viewport_size({"width": width, "height": 1000})
                page.get_by_text("连接到分量公式", exact=True).click()
                assert page.locator("math").is_visible()
                assert page.locator("math").evaluate("el => el.getBoundingClientRect().height > 10")
                check_no_overflow(page)
                if os.environ.get("LAB_SCREENSHOTS"):
                    target = Path(os.environ["LAB_SCREENSHOTS"])
                    target.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(target / f"vector-addition-{width}.png"), full_page=True)
                page.get_by_text("连接到分量公式", exact=True).click()
            page.get_by_role("link", name="独立查看", exact=True).click()
            assert page.locator("svg").count() == 1
            assert "(3, 3)" in page.locator("title").text_content()
            context.close()

            # Attempt actual file:// with the browser offline. Managed browsers
            # may prohibit local file navigation; report that specific limitation.
            offline = browser.new_context(offline=True, viewport={"width": 390, "height": 1000})
            isolated = offline.new_page()
            isolated.on("pageerror", lambda error: errors.append(str(error)))
            file_status = "PASS: offline file:// catalog and interaction"
            try:
                isolated.goto((ROOT / "index.html").as_uri())
            except Error as error:
                if "ERR_BLOCKED_BY_ADMINISTRATOR" not in str(error):
                    raise
                file_status = "SKIP: file:// is blocked by this environment's browser policy; local HTTP checks still run."
            else:
                check_no_overflow(isolated)
                isolated.get_by_role("link", name="打开交互实验 →").click()
                isolated.wait_for_selector("#diagram svg")
                isolated.get_by_role("button", name="相互抵消").click()
                assert isolated.locator("#sum-value").inner_text() == "(0, 0)"
                check_no_overflow(isolated)
            offline.close()

            # A copied Unit is served on its own, with no access to repo assets
            # or external network. This does not claim to replace file:// QA.
            with tempfile.TemporaryDirectory() as directory:
                copy = Path(directory) / "standalone"
                shutil.copytree(ROOT / UNIT, copy)
                copy_handler = partial(QuietHandler, directory=str(copy))
                with ThreadingHTTPServer(("127.0.0.1", 0), copy_handler) as copy_server:
                    Thread(target=copy_server.serve_forever, daemon=True).start()
                    copy_origin = f"http://127.0.0.1:{copy_server.server_port}"
                    copy_context = browser.new_context(viewport={"width": 390, "height": 1000})
                    isolated = copy_context.new_page()
                    isolated.on("pageerror", lambda error: errors.append(str(error)))
                    isolated.on("response", lambda response: missing.append(response.url) if response.status >= 400 else None)

                    def copied_only(route):
                        if route.request.url.startswith(copy_origin + "/"):
                            route.continue_()
                        else:
                            external.append(route.request.url)
                            route.abort()

                    isolated.route("http**://**/*", copied_only)
                    isolated.goto(copy_origin + "/interactive.html", wait_until="networkidle")
                    isolated.wait_for_selector("#diagram svg")
                    assert isolated.evaluate("VectorAdditionView.svg(VectorAddition.compute(VectorAddition.defaults)) + '\\n'") == (copy / "figure.svg").read_text(encoding="utf-8")
                    isolated.locator("#ay-number").fill("-3")
                    assert isolated.locator("#sum-value").inner_text() == "(3, -1)"
                    check_no_overflow(isolated)
                    copy_context.close()
                    copy_server.shutdown()
        finally:
            browser.close()
            server.shutdown()
    assert not errors, errors
    assert not missing, missing
    assert not external, external
    print("PASS: HTTP catalog, keyboard, sliders, numeric input, SVG values, invalid input, reset, zero vectors, native MathML, desktop/390px, copied Unit, identical static/interactive SVG; no external requests, JS or resource errors.")
    print(file_status)


if __name__ == "__main__":
    main()
