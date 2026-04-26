#!/usr/bin/env bash
# ai4s-core README 演示素材生成脚本
# 用法: source .venv/bin/activate && ./scripts/generate-demo-assets.sh

set -e

cd "$(dirname "$0")/.."
mkdir -p demo-assets

echo "=== Generating ai4s-core demo assets ==="
echo

# 演示1: 基本工作流生成 (JSON)
echo "[1/5] Basic workflow (JSON)..."
python -m ai4s_core.cli plan "Run MD simulation of 1UBQ" --mock --json > demo-assets/demo-basic.json 2>/dev/null
echo "  Saved: demo-assets/demo-basic.json ($(python3 -c "import json; d=json.load(open('demo-assets/demo-basic.json')); print(f'{len(d[\"steps\"])} steps')"))"

# 演示2: Python 导出
echo "[2/5] Python script export..."
python -m ai4s_core.cli plan "Run MD simulation of 1UBQ" --mock --format python > demo-assets/demo-script.py 2>/dev/null
echo "  Saved: demo-assets/demo-script.py ($(wc -l < demo-assets/demo-script.py) lines)"

# 演示3: Bash 导出
echo "[3/5] Bash script export..."
python -m ai4s_core.cli plan "Run MD simulation of 1UBQ" --mock --format bash > demo-assets/demo-script.sh 2>/dev/null
echo "  Saved: demo-assets/demo-script.sh ($(wc -l < demo-assets/demo-script.sh) lines)"

# 演示4: 验证引擎（带警告的查询）
echo "[4/5] Validation engine (warning demo)..."
python -m ai4s_core.cli plan "MD simulation at 5000K with 10fs timestep" --mock --json > demo-assets/demo-validation.json 2>/dev/null
echo "  Saved: demo-assets/demo-validation.json"

# 演示5: 列出领域
echo "[5/5] List domains..."
python -m ai4s_core.cli list-domains > demo-assets/demo-domains.txt 2>/dev/null
echo "  Saved: demo-assets/demo-domains.txt"

echo
echo "=== All demo assets generated ==="
ls -la demo-assets/
