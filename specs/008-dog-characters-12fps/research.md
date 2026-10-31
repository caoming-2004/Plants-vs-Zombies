# Research Decisions

- **Decision**: 沿用 `balance.json` 植物类型和现有 `blocker`/`shooter` 职责。**Rationale**: Simulation 已按配置建立植物索引，既有种植规则由同一权威路径处理。**Alternative**: 新建一套角色规则会重复扣费与战斗判定。
- **Decision**: 新植物的可见性由狗狗外观输入/卡片控制，玩法数值仍归 domain。**Rationale**: 当前外观选择不属于 Simulation 状态；把外观写入规则层会扩大改动。**Alternative**: 新建外观相关游戏规则状态会拖慢首个可玩版本。
- **Decision**: 动画姿态节奏与主显示帧率分开处理。**Rationale**: 项目 `tick_hz=60`，每秒 12 个姿态对应约 5 tick/姿态；改主循环会改变游戏速度。
- **Decision**: 素材布局以实际图片检查为准。**Rationale**: 四张 RGBA 图片均为 1672×941，但尺寸本身不能证明帧网格、动作顺序或完整透明边界。先检查再确定导入参数。
- **Decision**: 精简验证为受影响规则/素材测试、一次真实窗口核心流程和正式包烟测。**Rationale**: 满足快速可玩目标及宪章的正常/边界/失败路径验证。
