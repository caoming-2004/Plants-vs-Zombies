# 012 星级目标验收

**结果：通过（规则/显示）**

- 三个目标类型：`mowers_used_at_most`、`clear_within_ticks`、`sun_collected_at_least`；仅在胜利时结算。
- `tests/unit/test_campaign_progress.py` 覆盖目标判定、只胜利授予、最佳星级取最大、低分不覆盖、星级不影响解锁；**6 passed**。
- 关卡选择页显示每关星级，结算页显示“星级 ★★/★☆”和“下一关/再玩一局/返回主菜单”。截图：`level-select-cleared.png`、`result.png`。
- 最佳星级写入 progress.json，重复通关只提升不降低。

**限制**：星级目标当前以 day_01 的“无割草机/限时”为主；day_03 的收集阳光目标由配置覆盖，尚未做逐目标人工试玩。
