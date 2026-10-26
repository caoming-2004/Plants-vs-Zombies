# Research: 动画节奏与小狗显示尺寸调整

## 现有实现调查

### 决策 R1：沿用60Hz tick驱动的clip帧采样，不引入第二套动画时钟

- **Decision**: 继续通过manifest每帧duration_ticks和animation.frame_at(clip, elapsed)选取当前帧；游戏tick保持60Hz，正常窗口循环目标刷新60FPS。
- **Rationale**: 现有Animator和渲染器以simulation snapshot tick确定角色帧；暂停时simulation tick不前进，因而自然冻结。它能保持与渲染帧率无关并避免两份时间状态。
- **Alternatives considered**: 基于wall-clock的逐帧动画、在Renderer中每个render加1。二者在帧耗时波动时会漂移，且难以保证暂停/恢复生命周期。

### 决策 R2：重新标定所有必需clip的持续tick，素材帧顺序不变

- **Decision**: 对default与dogs的skin_catalog.REQUIRED动作清单重分配duration_ticks，让RGBA逐像素去重后的姿势率为12–18/s；工具与测试共用pose_count × balance.json.tick_hz / 总duration_ticks的计算口径，接触表进行人工姿势有效性复核。
- **Rationale**: 当前工具与集成测试使用旧的“至少24 unique poses/s”门槛；实测清单存在约24–60 pose/s的区间，需要一起改动，否则素材不能通过自校验。
- **Alternatives considered**: 降低pygame刷新率或限制游戏逻辑tick。它们会改变操作反馈/规则节奏并引入不稳定，不符合规格。

### 决策 R3：一次性动作播放速度与循环动作共用同一节奏标准

- **Decision**: 对hit、die、attack/bite、plant、ignite等单次动作使用同一姿势速率；Animator为hit事件增加presentation侧clip播放状态，而不是仅用现有8 tick灰色闪光代替动作。
- **Rationale**: 用户已明确所有动作都需12–18姿势/s；一次性clip完整播放且不影响规则结算。角色状态由动画事件触发和结束后恢复，避免拖慢Simulation。
- **Alternatives considered**: 只调整idle/walk循环，或让受击clip继续不播放。都违反对所有动作的澄清。

### 决策 R4：小杜清行以35个源姿势完整播放2秒

- **Decision**: ignite clip只包含素材provenance映射的35个源姿势，按序播放；总duration精确为120 tick，平均速率17.5个源姿势/s。
- **Rationale**: 用户明确选择完整源姿势而非裁剪选关键帧。现有manifest clip可能包括额外生成的中间姿势，必须辨别源帧出处，不可把69个姿势全部压在2秒内并违反12–18/s。
- **Alternatives considered**: 保持1.5秒并只展示最多27姿势；2秒中展示所有生成姿势（将超过频率范围）；延迟整行玩法结算（违反视觉/规则分离）。

### 决策 R5：使用同一个角色缩放入口并保持底部锚点

- **Decision**: 小宝、小杜倍率的唯一权威值放在dogs manifest各自role元数据中；animation.py只提供读取接口，所有展示路径共用该倍率，草坪尺寸在当前基准上增加至少15%，并以稳定anchor定位。
- **Rationale**: 目前多个绘制调用点直接传DOG_SCALE或硬编码卡片倍率，单改Actor调用会造成同一角色在预览和游戏里的比例不一致。既有dog_validation可用于动作帧轮廓和相邻角色约束。
- **Alternatives considered**: 对原始图片裁切或仅扩大卡片。可能损失动作内容或不能解决草坪主体偏小问题。

### 决策 R6：扩大后沿用素材回退和发行流程

- **Decision**: 保持皮肤选择和缺失素材回退逻辑，manifest schema v1兼容；运行时继续离线读取随包资源；复用既有pytest、资产校验、preview、benchmark和PyInstaller脚本。
- **Rationale**: 迭代必须保持旧版可运行、兼容default皮肤和单文件解压发行方式。
- **Alternatives considered**: 引入新图形动画库或网络运行时加载素材。无必要且会增加发行复杂度。

## 代码与素材证据

- src/pvz_game/presentation/animation.py：frame_at基于manifest tick采样；Animator消费hit/shot/bite/action_started/died/row_clear_started事件；清行视觉寿命取ignite clip总tick。
- src/pvz_game/presentation/renderer.py：有草坪角色、卡片、预览、拖动ghost的不同绘制路径；放大必须覆盖这些路径。
- src/pvz_game/presentation/skin_catalog.py：REQUIRED是两套外观的完整动作集合；保留schema v1和锚点/帧验证。
- tools/validate_assets.py与tests/integration/test_animation.py：当前有>=24姿势/s硬门槛，必须改为12–18范围并覆盖一次性clip。
- tests/replay/test_skin_invariance.py：可以复用以证明表现倍率/帧时长不写入模拟状态。
- tools/build.ps1和tools/verify_bundle.py：既有发行验证入口，保持随包素材和打包启动行为。

## 未决设计

无需求级未决项。展示缩放最终数值须在实现时通过每个姿势边界与UI可视区校验确定；以“比当前角色草坪高度至少+15%、全身可见、无遮挡”为强制准则，不将未验证的裸比例作为规格事实。
