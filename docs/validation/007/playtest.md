# 可玩性验证

- 必要回归：`tests/integration/test_animation.py`、`test_asset_manifest.py`、`test_skin_selection.py`、`test_playable_loop.py`、`tests/replay/test_base_replay.py`，共 54 项通过。
- 现有确定性回放覆盖开始、资源收集、种植、敌人推进、胜利与失败、重新开始；本轮未更改游戏规则。
- `tools/validate_assets.py` 通过，检查默认、卡通和照片三套图集。
- 正式目录 `dist/PvzMiniGame-v0.3.1/` 构建完成；从该目录独立运行 EXE 的烟测退出码 0，并生成 `bundle-play.png`。
- 真实窗口展示和开始按钮事件注入已验证；未进行真人从开始到胜负的一整局手动试玩。该项按未验证记录。
