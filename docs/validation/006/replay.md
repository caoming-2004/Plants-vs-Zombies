# 006 确定性回放对照

复用 `tests/replay/test_base_replay.py::test_feature_replay_matches_pre_change_gameplay_baseline`，将当前代码每tick的输入策略与 `tests/replay/fixtures/004-baseline.json` 比较。测试运行结果：通过；事件序列、所有60 tick检查点快照及最终字段均逐项相等。

| 对照项 | 第一版 fixture | 当前实现 | 结果 |
|---|---|---|---|
| 事件 kind/tick/id/完整负载 | `events` | 完全相等 | PASS |
| 每60 tick及终态快照 | `snapshots` | 完全相等 | PASS |
| 胜负/终态 | `final_phase=won` | `won` | PASS |
| 终态 tick | `12011` | `12011` | PASS |
| 剩余阳光 | `450` | `450` | PASS |
| 击杀数 | `12` | `12` | PASS |
| 割草机行、位置、状态 | 5行均ready，x=72 | 完全相等 | PASS |

复现命令：`$env:PYTHONPATH='src'; .\\.venv\\Scripts\\python.exe -m pytest tests/replay/test_base_replay.py -q`。全量开发测试中同一回放也通过；未修改 fixture。
