# 012 五关战役与进度验收

**结果：通过（配置/进度/试玩）**

- `assets/levels/campaign.json` 包含 day_01～day_05，day_05 通关后解锁无尽模式。
- `day_01` 保持原有 12 只僵尸、波次和初始数值，只补充 order/name/star_goals；day_02～05 每关 15/18/21/24 只僵尸、3 个递增波次和 2 个星级目标。
- 压力差异：day_02/03/04 使用更长的天空阳光间隔，day_05 使用 3 行割草机限制。
- `pytest tests/unit/test_campaign_config.py tests/unit/test_campaign_progress.py tests/integration/test_campaign_flow.py -q`：**10 passed**。
- 脚本化试玩（复用项目 replay 策略的采集/种植逻辑）依次通关 day_01～day_05；结果：全部 won，击杀 12/15/18/21/24。
- 关卡选择、锁定/解锁、下一关/重试、返回菜单和结算星级通过 headless UI 截图检查（`level-select.png`、`result.png`、`app-level-flow.png`）。
- 进度文件路径：`%LOCALAPPDATA%\PvzMiniGame\progress.json`；缺失/损坏回退由 progress 用例覆盖。

**限制**：完整 5 关试玩是脚本化模拟，不是人工逐关长时间试玩；仍需在真实窗口中人工确认手感。
