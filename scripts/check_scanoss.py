#!/usr/bin/env python3
"""SCANOSS のスキャン結果 (JSON) を読み、OSS コードとの一致を報告する。

- 一致したコードはすべて一覧表示する
- コピーレフト系 License (GPL / AGPL / LGPL など) との一致があれば exit 1 で失敗させる

使い方: python scripts/check_scanoss.py results.json
"""
import json
import os
import sys

# この接頭辞で始まる License を「要対応 (CI 失敗)」とする
COPYLEFT_PREFIXES = ("GPL-", "AGPL-", "LGPL-", "SSPL-", "EUPL-", "OSL-")


def is_copyleft(license_name: str) -> bool:
    return license_name.upper().startswith(COPYLEFT_PREFIXES)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_scanoss.py <results.json>", file=sys.stderr)
        return 2

    with open(sys.argv[1], encoding="utf-8") as f:
        results = json.load(f)

    rows = []
    has_copyleft = False
    for path, matches in sorted(results.items()):
        for m in matches:
            if m.get("id") == "none":
                continue
            licenses = [lic["name"] for lic in m.get("licenses", [])]
            copyleft = any(is_copyleft(name) for name in licenses)
            has_copyleft |= copyleft
            rows.append({
                "status": "NG" if copyleft else "要確認",
                "file": path,
                "type": m.get("id"),  # file = ファイル丸ごと / snippet = 一部
                "lines": m.get("lines"),
                "matched": m.get("matched"),
                "component": m.get("component"),
                "url": m.get("url"),
                "licenses": ", ".join(licenses) or "(不明)",
            })

    if not rows:
        report = "✅ 既知の OSS コードとの一致は見つかりませんでした。\n"
    else:
        report = "| 判定 | ファイル | 種別 | 行 | 一致率 | 一致した OSS | License |\n"
        report += "|---|---|---|---|---|---|---|\n"
        for r in rows:
            report += (
                f"| {r['status']} | `{r['file']}` | {r['type']} | {r['lines']} | {r['matched']} "
                f"| [{r['component']}]({r['url']}) | {r['licenses']} |\n"
            )
        if has_copyleft:
            report = "❌ コピーレフト系 License のコードとの一致があります。\n\n" + report
        else:
            report = "⚠️ OSS コードとの一致があります（コピーレフト系ではありません）。表示義務などを確認してください。\n\n" + report

    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## OSS コード一致チェック (SCANOSS)\n\n" + report)

    return 1 if has_copyleft else 0


if __name__ == "__main__":
    sys.exit(main())
