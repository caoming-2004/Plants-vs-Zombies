# Research: 狗狗外观与玩法体验优化

## Context

本功能基于现有离线 Windows/Pygame 游戏，不引入技术栈迁移。已经检查的关键路径为：

- `src/pvz_game/domain/simulation.py`：拥有植物、僵尸、阳光、胜负和确定性快照；从 `day_01.json` 读取平坦 `spawn_schedule`。
- `src/pvz_game/domain/systems.py`：按固定 tick 出怪、移动与攻击；被窝当前由 `add_sun(..., start=(x,y-34))` 生成向下运动的阳光。
- `src/pvz_game/presentation/input.py`：`DragState` 已保存连续 pointer，但 hover 和释放使用 `cell_at`；该格被占用时 `placement_reason` 拒绝。
- `src/pvz_game/presentation/renderer.py`：拖动预览当前显示在 hover cell 中心，外观页目前只列出向日葵、豌豆射手、坚果墙、辣椒和普通僵尸。
- `src/pvz_game/presentation/animation.py`：由 `Animator` 根据角色状态选帧；已有 alpha-visible frame fitting 和缩放缓存，可复用。
- `src/pvz_game/presentation/skin_catalog.py`：全局选择 plant/zombie skin；`dogs` manifest 已包含 `pangbaobao` 和 `huanghuang` 对应图集角色。
- `src/pvz_game/app.py` 在外观菜单首帧后已后台预载 dogs 和 dogs_photo 图集；新增角色预览复用该路径，未就绪时显示占位，不同步解码图集。
- `assets/config/balance.json` 与 `assets/levels/day_01.json`：单一权威玩法数值和 12 条单类型出怪表。

## Decisions

### 1. 保持单项目、固定步进和渲染边界

**Decision**: 扩展现有 `Simulation`、`systems.advance`、`Animator`、`Renderer` 和 JSON 配置；模拟继续使用 60 Hz tick，图像和交互只通过已有 snapshot/event/command 边界连接。

**Rationale**: 本次没有网络、持久化或多平台需求。当前模型已经支持多 `type_id`，单关配置可表达更多敌人与波次，不需要引擎迁移或新依赖。

**Alternatives considered**: 引入新游戏引擎或单独波次服务；拒绝，因为会扩大打包/维护成本且不帮助快速交付桌面可玩版本。

### 2. 图像修正使用现有图集、alpha 边界和角色元数据

**Decision**: 调整两种狗皮肤的 `sunflower`/`zombie_basic` 角色缩放，使用 alpha-visible bounds 检查最大姿态；朝左的僵尸仅在表现层镜像动作帧，并修正透明裁切偏移和锚点，镜像结果使用缓存。

**Rationale**: 模拟中的嗷嗷嗷已向左移动；翻转画面而不改变实体运动可以修正朝向而不影响战斗。完整 alpha 轮廓比原始透明画布尺寸更能代表玩家看到的身体。

**Alternatives considered**: 重新生成整套角色素材；拒绝，因为用户已有动作图集且生成素材会扩大工作量、产生帧间不一致风险。仅调窗口裁剪；拒绝，因为无法修正大体型且可能裁掉其他动作。

### 3. 阳光弧跳的权威位置留在模拟快照

**Decision**: 给被窝产生的阳光提供明确的身体起点和弧跳高度/时长；按 tick 确定性计算当前位置，收集命中仍使用 snapshot 坐标。仅更改 plant source 的轨迹，天空阳光不变。

**Rationale**: 当前 `SunPickup` 已持有 start/target/duration，扩展少量运动数据即可；不把实际位置只做成 Renderer 动画，避免可见图像与点击命中错位，也保留 replay 可重复性。

**Alternatives considered**: 只在 Renderer 上画一段视觉动画，实体瞬移到落点；拒绝，因为阳光视觉位置与交互位置会分离。改动面值或寿命；拒绝，因为这不是本功能要求且影响经济平衡。

### 4. 拖动跟手与放置判定分开

**Decision**: pointer 在整个 drag 中保持连续坐标；候选网格只用于 hover 背景和有效性预览。释放时以草坪范围内几何最近格为唯一候选，等距时采用稳定固定规则；最近格无效就拒绝，不尝试第二近空格。

**Rationale**: 视觉预览跟手改善直接可见，复用现有网格与 `placement_reason` 可保留游戏规则权威。拒绝 occupied candidate 是用户已确认的预期，避免误种到别处。

**Alternatives considered**: 拖动预览吸附到格子中心；拒绝，因为与连续移动要求冲突。找最近空格自动放置；拒绝，因为会偏离玩家瞄准位置。

### 5. 增加两种配置驱动敌人与分段波次

**Decision**: 用 `zombie_fast` 和 `zombie_tough` 扩展 `zombie_types`，保留 `zombie_basic`。快速型速度高、生命较低；耐久型生命较高、速度较低。`day_01.json` 将出怪条目加 wave ID，并配置至少三个带提示时间的阶段；后续阶段以更丰富组合或数量升级。基础速度、生命、伤害、啃食间隔集中于 balance JSON，具体出怪 tick 和行集中于关卡 JSON。

**Rationale**: 现有关卡单一敌人类型和递增平坦时间表是重复感的直接来源。两种可理解的对策差异（压制快速敌人、持续伤害耐久敌人）能给现有植物创造策略选择，且不依赖新关卡系统。

**Alternatives considered**: 新增多个模式/地图；用户选择先扩展现有关卡，故不实施。仅调快普通僵尸并改间隔；拒绝，因为不会形成可辨认的敌人特性。导入额外大型动画图集；拒绝，当前素材无此必要；复用 `zombie_basic` 动作并添加轻量速度/耐久标记。

### 6. 外观菜单扩展只增加角色预览状态

**Decision**: 在角色预览列表中加入胖宝宝与黄黄两个可点选角色项，菜单仅记住当前焦点角色；全局 `dogs` 皮肤选择保持现状，两个游戏单位继续绑定各自 ID 和职责。预览图片使用现有后台图集预载，未加载完成时显示占位，不阻塞菜单或输入。

**Rationale**: `dogs` atlas 已包含两个角色，`visible_plant_cards` 已在狗狗外观中提供两张独立功能卡；只需让玩家在外观页找到、预览并选中它们，不需要构造重复的单位或 per-role 替换机制。

**Alternatives considered**: 把胖宝宝/黄黄做成其他植物的可替换 skin；与用户确认的独立角色选项冲突。同步载入 dog atlas 后再显示菜单；会重引入先前消除的换肤界面卡顿。

### 7. 最小化验证与桌面发行

**Decision**: 对应每类高风险改动运行已有相关测试文件中的少数新/相关用例，复测可赢、可输和重开各一次；只做一次 10 秒标准画面测量和一次正式目录包 smoke。直接执行 PyInstaller 构建，复制随包说明与许可，不生成 ZIP，并删除本轮 build staging。

**Rationale**: 规则变化需要自动化验证，图像/拖放/性能需要少量可重复集成或人工检查；全量测试、压力场景和多配置包矩阵对首个可玩版本没有相称收益。

**Alternatives considered**: 运行完整 pytest 与压力矩阵；按用户明确的快速验收要求不采用。直接删除历史发行物；拒绝，因为只清理由本轮产生的 staging，保护已有交付。

## Open Questions

无产品范围问题。快速型/耐久型的具体平衡数值及三个波次的 tick/行分配，在实现配置中先设小规模可玩初值，再由可赢回放与一次试玩检查；不为此增加独立测试套件或关卡系统。
