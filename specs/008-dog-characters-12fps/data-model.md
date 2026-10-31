# Data Model

## Plant type

字段：唯一 `id`、显示名称、价格、生命值、冷却 tick、职责、职责专属参数。新增 `pangbaobao` 为 blocker，`huanghuang` 为 shooter；数值与现有植物同源配置，选择/种植/伤害仍由 Simulation 判定。

## Appearance role

字段：skin id、游戏角色 id、可见名称、原图来源及哈希、卡片/预览帧、动作状态、锚点和显示倍率。被窝与嗷嗷嗷沿用现有角色 id；胖宝宝与黄黄分别关联新增植物 id。狗狗外观包含新增角色，经典外观不提供其卡片。

## Animation clip

字段：角色、状态、姿态序列、每姿态持续 tick、循环标记、来源姿态索引。循环植物动作目标为 12±1 个不同姿态/秒；非循环动作保持现有玩法事件时长。

## Session lifecycle

沿用 menu → playing → won/lost → restart；新增植物计入现有阳光、冷却、格子、胜负和重置流程，不增加独立会话状态。
