import os
import time
import pytest
import logging
from appium import webdriver
from capabilities import APPIUM_SERVER, CAPABILITIES, WEBVIEW_CONTEXT_PREFIX, NATIVE_CONTEXT

logger = logging.getLogger(__name__)

# node_id → driver 매핑 (훅에서 드라이버 접근용)
_driver_store: dict = {}


def pytest_configure(config):
    os.makedirs("reports/screenshots", exist_ok=True)


# ── pytest-html에 스크린샷 컬럼 추가 ──
def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Screenshot</th>")


def pytest_html_results_table_row(report, cells):
    screenshot_html = getattr(report, "screenshot_html", "")
    cells.insert(2, f"<td>{screenshot_html}</td>")


# ── 테스트 실패 시 스크린샷 캡처 ──
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = _driver_store.get(item.nodeid)
        if driver is None:
            return

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_name = item.nodeid.replace("/", "_").replace("::", "__").replace(" ", "_")
        filename = f"reports/screenshots/{safe_name}_{timestamp}.png"

        try:
            # 스크린샷은 네이티브 context에서만 전체 화면 캡처 가능
            current_ctx = driver.current_context
            driver.switch_to.context(NATIVE_CONTEXT)
            driver.save_screenshot(filename)
            driver.switch_to.context(current_ctx)

            rel_path = os.path.relpath(filename, "reports")
            report.screenshot_html = (
                f'<a href="{rel_path}" target="_blank">'
                f'<img src="{rel_path}" style="max-width:160px;max-height:100px;" />'
                f"</a>"
            )
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
            report.screenshot_html = f'<span style="color:gray">캡처 실패: {e}</span>'


@pytest.fixture(scope="function")
def driver(request):
    _driver = webdriver.Remote(APPIUM_SERVER, desired_capabilities=CAPABILITIES)
    _driver.implicitly_wait(10)

    _driver_store[request.node.nodeid] = _driver
    logger.info("Driver started")

    yield _driver

    _driver_store.pop(request.node.nodeid, None)
    _driver.quit()
    logger.info("Driver quit")


@pytest.fixture(scope="function")
def webview_driver(driver):
    switch_to_webview(driver)
    yield driver
    switch_to_native(driver)


def switch_to_webview(driver, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        contexts = driver.contexts
        webview_ctx = next(
            (c for c in contexts if c.startswith(WEBVIEW_CONTEXT_PREFIX)),
            None,
        )
        if webview_ctx:
            driver.switch_to.context(webview_ctx)
            logger.info(f"Switched to context: {webview_ctx}")
            return
        time.sleep(0.5)
    raise TimeoutError(
        f"WebView context not found within {timeout}s. Available: {driver.contexts}"
    )


def switch_to_native(driver):
    driver.switch_to.context(NATIVE_CONTEXT)
    logger.info("Switched to NATIVE_APP context")
