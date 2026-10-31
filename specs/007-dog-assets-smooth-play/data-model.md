# Data Model

## Dog role

字段：`role`、`name`、来源图及哈希、`clips`、`display_scale_multiplier`、`anchor`。角色键唯一；三图与三名一一对应。站立高度比≤1.15，所有动作有效像素必须完整显示。

## Visual asset

字段：skin id（`dogs`/`dogs_photo`）、atlas、帧矩形、trim offset、透明边界、来源记录。现有导入工具生成，`Skin.surface` 缓存读取。缺失或格式错误时显式失败。

## Session transition

现有状态：menu → playing → won/lost → restart。开始和重开命令沿用当前状态机；只观察点击反馈及首个可操作画面耗时。

## Temporary test artifact

字段：生成时间、用途、路径、是否属于本轮、清理状态。只清理本轮明确生成的临时 EXE/ZIP。
