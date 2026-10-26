# 004 自动化验证

运行环境：Windows 11 x64、项目 Python 3.12.15、pygame-ce 2.5.8；日期 2026-10-26。

| 命令 | 结果 |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q` | 通过，113 passed in 115.64s |
| `.venv/Scripts/python.exe tools/validate_assets.py` | 通过；default 538 referenced frames，dogs 571 referenced frames；两套所有必需动作姿势率符合 12–18/s；小杜 ignite 精确检查通过 |
| `tests/replay/test_base_replay.py` 与 `tests/replay/test_skin_invariance.py` | 通过；固定输入结果匹配 004 改动前完整模拟基准，皮肤组合不改变规则结果 |
| `tests/integration/test_jalapeno_row_clear.py` | 通过；35 源姿势、120 tick、2 秒、清行一次、对局推进、暂停/重开生命周期 |
| `tests/integration/test_asset_manifest.py` 与 `tests/integration/test_animation.py` | 通过；狗狗倍率兼容、锚点基线、相邻格轮廓、UI 容器边界 |

`tools/validate_assets.py` 同时调用 dog validation 对所有必需角色动作姿势进行最终显示倍率的相邻格轮廓检查；诊断为空。
