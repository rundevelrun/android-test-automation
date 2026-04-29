#!/usr/bin/env python3
"""junit.xml을 파싱해서 GitHub Actions Job Summary 마크다운을 생성합니다."""
import sys
import os
import xml.etree.ElementTree as ET

junit_path = sys.argv[1] if len(sys.argv) > 1 else "tests/reports/junit.xml"
summary_file = os.environ.get("GITHUB_STEP_SUMMARY")

TC_LABELS = {
    "test_cases.test_tc01_login":         "TC-01 로그인 플로우",
    "test_cases.test_tc02_search_filter": "TC-02 상품 검색/필터",
    "test_cases.test_tc03_cart":          "TC-03 상품 상세 및 장바구니",
    "test_cases.test_tc04_e2e_order":     "TC-04 E2E 주문 완료",
    "test_cases.test_tc05_native_webview":"TC-05 Native↔WebView 전환",
    "test_cases.test_tc06_network":       "TC-06 네트워크 예외 처리",
    "test_cases.test_tc07_error_cases":   "TC-07 에러 케이스",
}

TEST_NAMES = {
    # TC-01
    "test_login_page_loads":                          "로그인 페이지의 핵심 요소가 노출된다",
    "test_valid_login_navigates_to_products":         "정상 계정으로 로그인하면 상품 목록으로 이동한다",
    "test_wrong_password_shows_error":                "잘못된 비밀번호 입력 시 에러 메시지가 노출된다",
    "test_wrong_email_shows_error":                   "존재하지 않는 이메일 입력 시 에러 메시지가 노출된다",
    "test_empty_email_shows_validation_error":        "이메일 미입력 시 에러 메시지가 노출된다",
    "test_empty_password_shows_validation_error":     "비밀번호 미입력 시 에러 메시지가 노출된다",
    "test_error_clears_on_valid_login":               "에러 후 올바른 계정 입력 시 에러가 사라지고 이동한다",
    # TC-02
    "test_all_products_shown_by_default":             "기본 상태에서 전체 상품이 노출된다",
    "test_search_by_keyword_returns_matching_products":"키워드 검색 시 해당 키워드 상품만 노출된다",
    "test_search_no_result_shows_empty_state":        "결과 없는 검색어 입력 시 no-result 메시지가 노출된다",
    "test_filter_electronics":                        "전자기기 필터 선택 시 전자기기 상품만 노출된다",
    "test_filter_fashion":                            "패션 필터 선택 시 패션 상품만 노출된다",
    "test_filter_food":                               "식품 필터 선택 시 식품 상품만 노출된다",
    "test_filter_all_resets_to_full_list":            "전체 필터 선택 시 전체 목록으로 복귀한다",
    "test_search_within_filter":                      "필터 + 검색 교집합 결과가 노출된다",
    # TC-03
    "test_product_detail_shows_correct_info":         "상품 상세 페이지에서 이름과 가격이 노출된다",
    "test_qty_increase":                              "+ 버튼 클릭 시 수량이 1 증가한다",
    "test_qty_decrease_not_below_one":                "수량 1에서 - 버튼 클릭해도 0 이하로 내려가지 않는다",
    "test_total_price_updates_with_qty":              "수량 변경 시 합계 금액이 정확히 업데이트된다",
    "test_add_to_cart_shows_toast":                   "장바구니 담기 클릭 시 토스트 메시지가 노출된다",
    "test_cart_badge_increments_after_add":           "장바구니 담기 후 네이티브 툴바 배지 숫자가 증가한다",
    "test_remove_item_from_cart":                     "장바구니에서 상품 삭제 시 빈 장바구니 상태가 된다",
    # TC-04
    "test_full_order_flow":                           "로그인 → 상품 선택 → 장바구니 → 주문 전체 플로우가 정상 동작한다",
    "test_order_number_is_unique_per_order":          "주문마다 고유한 주문번호가 생성된다",
    "test_order_complete_shows_correct_items":        "주문 완료 페이지에서 주문한 상품 정보가 정확히 표시된다",
    "test_multiple_items_order":                      "여러 상품을 장바구니에 담고 한 번에 주문할 수 있다",
    # TC-05
    "test_webview_context_is_available":              "앱 실행 후 WebView context가 감지된다",
    "test_native_context_switch":                     "Native context로 전환 후 툴바 타이틀을 읽을 수 있다",
    "test_buy_now_triggers_native_dialog":            "바로 구매 버튼 클릭 시 네이티브 AlertDialog가 노출된다",
    "test_dialog_confirm_navigates_to_cart":          "다이얼로그 확인 클릭 시 장바구니 페이지로 이동한다",
    "test_dialog_cancel_stays_on_detail":             "다이얼로그 취소 클릭 시 상세 페이지에 머무른다",
    "test_cart_badge_updates_in_native_after_webview_action": "WebView 장바구니 담기 후 네이티브 배지가 업데이트된다",
    "test_toolbar_title_updates_on_page_navigation":  "WebView 페이지 전환 시 네이티브 툴바 타이틀이 갱신된다",
    # TC-06
    "test_offline_page_shows_retry_button":           "오프라인 상태에서 재시도 버튼이 노출된다",
    "test_offline_status_shows_on_page":              "오프라인 상태에서 네트워크 상태 텍스트가 '오프라인'을 포함한다",
    "test_retry_when_offline_shows_still_disconnected":"오프라인 재시도 클릭 시 연결 안됨 메시지가 유지된다",
    "test_retry_after_network_recovery_navigates_to_products": "네트워크 복구 후 재시도 클릭 시 상품 목록으로 이동한다",
    "test_login_works_after_network_recovery":        "네트워크 복구 후 로그인이 정상 동작한다",
    # TC-07
    "test_warning_appears_after_3_failures":          "3회 실패 시 계정 잠김 경고 문구가 노출된다",
    "test_account_locked_after_5_failures":           "5회 연속 실패 시 계정 잠금 배너가 노출된다",
    "test_login_button_disabled_during_lockout":      "잠금 상태에서 로그인 버튼이 비활성화된다",
    "test_lockout_timer_visible":                     "잠금 배너에 남은 시간 타이머가 노출된다",
    "test_invalid_email_format_shows_error":          "잘못된 이메일 형식 입력 시 형식 오류 메시지가 노출된다",
    "test_soldout_badge_visible_on_list":             "품절 상품에 '품절' 배지가 노출된다",
    "test_low_stock_badge_visible_on_list":           "재고 부족 상품에 '재고 N개' 배지가 노출된다",
    "test_soldout_product_click_shows_native_dialog": "품절 상품 클릭 시 재입고 안내 네이티브 다이얼로그가 노출된다",
    "test_soldout_product_detail_buttons_disabled":   "품절 상품 상세에서 장바구니·구매 버튼이 비활성화된다",
    "test_soldout_overlay_visible_on_detail":         "품절 상품 상세에서 SOLD OUT 오버레이가 노출된다",
    "test_restock_box_visible_on_soldout_detail":     "품절 상품 상세에서 재입고 알림 신청 박스가 노출된다",
    "test_low_stock_status_shown_on_detail":          "재고 부족 상품 상세에서 재고 수량 경고 텍스트가 노출된다",
    "test_qty_cannot_exceed_10":                      "+ 버튼을 11번 눌러도 수량은 10을 초과하지 않는다",
    "test_qty_limit_warning_shown_at_max":            "수량 10에서 + 버튼 클릭 시 최대 수량 경고 문구가 노출된다",
    "test_cart_limit_warning_when_cart_already_full": "장바구니 10개 담긴 상태에서 추가 시 한도 경고가 노출된다",
    "test_invalid_coupon_shows_error":                "존재하지 않는 쿠폰 코드 입력 시 오류 메시지가 노출된다",
    "test_valid_coupon_applies_discount":             "유효한 쿠폰(SAVE10) 입력 시 할인이 적용된다",
    "test_fail_test_coupon_triggers_payment_error":   "FAIL_TEST 쿠폰 적용 후 주문 시 결제 실패 배너가 노출된다",
    "test_payment_error_does_not_navigate_away":      "결제 실패 시 장바구니 페이지에 그대로 머문다",
    "test_session_banner_shown_when_not_logged_in":   "로그인 없이 products 진입 시 세션 만료 배너가 노출된다",
    "test_no_session_banner_when_logged_in":          "정상 로그인 후 products 진입 시 세션 만료 배너가 노출되지 않는다",
}

try:
    tree = ET.parse(junit_path)
    root = tree.getroot()
except Exception as e:
    print(f"junit.xml 파싱 실패: {e}", file=sys.stderr)
    sys.exit(0)

suites = root.findall("testsuite") or [root]

# 테스트케이스 수집 및 TC별 그룹핑
groups = {}
total = failures = skipped = passed = 0

for suite in suites:
    for tc in suite.findall("testcase"):
        total += 1
        classname = tc.get("classname", "")
        name = tc.get("name", "")
        time_sec = float(tc.get("time", "0"))

        if tc.find("skipped") is not None:
            icon, status = "⏭", "skip"
            skipped += 1
        elif tc.find("failure") is not None or tc.find("error") is not None:
            icon, status = "❌", "fail"
            failures += 1
            el = tc.find("failure") or tc.find("error")
            msg = (el.get("message") or "").split("\n")[0][:80] if el is not None else ""
        else:
            icon, status = "✅", "pass"
            passed += 1

        # classname 예: test_cases.test_tc01_login.TestLogin
        module = ".".join(classname.split(".")[:2])
        tc_label = TC_LABELS.get(module, module)

        if tc_label not in groups:
            groups[tc_label] = []

        desc = TEST_NAMES.get(name, name)
        fail_msg = ""
        if status == "fail":
            el = tc.find("failure") or tc.find("error")
            fail_msg = (el.get("message") or "").split("\n")[0][:100] if el is not None else ""

        groups[tc_label].append((icon, desc, f"{time_sec:.1f}s", fail_msg))

lines = []
lines.append("## 🧪 테스트 결과\n")

# 요약 배지
pass_rate = int(passed / total * 100) if total else 0
lines.append(f"| 항목 | 수 |")
lines.append(f"|------|----|")
lines.append(f"| 전체 | **{total}** |")
lines.append(f"| ✅ 통과 | **{passed}** |")
lines.append(f"| ❌ 실패 | **{failures}** |")
lines.append(f"| ⏭ 스킵 | **{skipped}** |")
lines.append(f"| 통과율 | **{pass_rate}%** |")
lines.append("")

# TC별 상세
for tc_label, cases in groups.items():
    tc_passed = sum(1 for c in cases if c[0] == "✅")
    tc_total = len(cases)
    lines.append(f"### {tc_label} ({tc_passed}/{tc_total})\n")
    lines.append("| 결과 | 테스트 항목 | 소요 시간 |")
    lines.append("|------|------------|----------|")
    for icon, desc, t, fail_msg in cases:
        row = f"| {icon} | {desc} | {t} |"
        lines.append(row)
        if fail_msg:
            lines.append(f"| | ⚠️ `{fail_msg}` | |")
    lines.append("")

output = "\n".join(lines)

if summary_file:
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(output + "\n")
else:
    print(output)
