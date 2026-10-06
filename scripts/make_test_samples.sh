#!/usr/bin/env bash
# OSS 一致チェックの動作確認用に、既知の OSS から一部を切り出したサンプルを作る。
# 「AI が OSS のコードをそのまま出力してしまった」状況を再現するためのもの。
# 確認が終わったらサンプルは削除し、main には入れないこと。
#
# 使い方: bash scripts/make_test_samples.sh [出力先ディレクトリ (既定: test-samples)]
set -euo pipefail

OUT="${1:-test-samples}"
mkdir -p "$OUT"

# コピーレフト系 (GPL-3.0): GNU coreutils の cat.c から 101 行 → NG (CI 失敗) になるはず
curl -sfL https://raw.githubusercontent.com/coreutils/coreutils/v9.4/src/cat.c \
  | sed -n '300,400p' > "$OUT/gpl_sample.c"

# 非コピーレフト系 (MIT): Express の router から 101 行 → 要確認 (CI は成功) になるはず
curl -sfL https://raw.githubusercontent.com/expressjs/express/4.18.2/lib/router/index.js \
  | sed -n '130,230p' > "$OUT/mit_sample.js"

# 一致なし: 自作コード → 何も検出されないはず
cat > "$OUT/original_sample.ts" <<'EOF'
export function formatTireSize(width: number, aspect: number, rim: number): string {
  return `${width}/${aspect}R${rim}`;
}
EOF

echo "作成しました:"; ls -1 "$OUT"
