#!/usr/bin/env python3
"""junit.xml을 파싱해서 GitHub Actions Job Summary 마크다운을 생성합니다."""
import sys
import os
import xml.etree.ElementTree as ET

junit_path = sys.argv[1] if len(sys.argv) > 1 else "tests/reports/junit.xml"
summary_file = os.environ.get("GITHUB_STEP_SUMMARY")

try:
    tree = ET.parse(junit_path)
    root = tree.getroot()
except Exception as e:
    print(f"junit.xml 파싱 실패: {e}", file=sys.stderr)
    sys.exit(0)

suites = root.findall("testsuite") or [root]

lines = []
lines.append("## 테스트 결과\n")

total = errors = failures = skipped = passed = 0

for suite in suites:
    for tc in suite.findall("testcase"):
        total += 1
        name = tc.get("name", "")
        classname = tc.get("classname", "")

        if tc.find("skipped") is not None:
            icon = "⏭"
            skipped += 1
        elif tc.find("failure") is not None:
            icon = "❌"
            failures += 1
        elif tc.find("error") is not None:
            icon = "❌"
            errors += 1
        else:
            icon = "✅"
            passed += 1

        lines.append(f"| {icon} | `{classname}::{name}` |")

header = [
    f"| 결과 | 테스트 |",
    f"|------|--------|",
]

summary_lines = [
    f"**총 {total}개** — ✅ {passed} 통과 / ❌ {failures + errors} 실패 / ⏭ {skipped} 스킵\n",
    "",
] + header + lines

output = "\n".join(summary_lines)

if summary_file:
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(output + "\n")
else:
    print(output)
