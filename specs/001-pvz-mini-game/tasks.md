# Tasks: 植物大战僵尸基础小游戏与小狗换肤

**Input**: `specs/001-pvz-mini-game/` 中的 spec.md、plan.md、research.md、data-model.md、contracts/、quickstart.md。
**Prerequisites**: 上述设计文档及 `.specify/memory/constitution.md`。
**Tests**: FR-017、SC-001至SC-009及宪章要求核心规则验证；安排针对性的规则、集成、回放和实机测试，不要求所有代码采用TDD。
**Organization**: 按用户故事与依赖拆分；路径均相对仓库根目录。此文件仅生成待办，不代表实现完成。

## Format: `[ID] [P?] [Story] Description`

每项为 `- [ ] T编号 [P可选] [US编号可选] 描述及具体路径`。
[P]只表示完成前置后可与指定独立任务并行，不代表无依赖；同文件修改必须串行。
US1为可玩与双击启动；US2为原版界面及动作；US3为小狗换肤。基础与收尾任务不带故事标签。

## Path Conventions

一个Python包位于src/pvz_game/；资源位于assets/；开发工具位于tools/；打包位于packaging/；
测试位于tests/；美术与验收证据位于docs/。不引入后端、数据库或通用插件框架。

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 建立独立Windows x64 Python3.12环境及项目入口，不修改系统默认解释器。

- [X] T001 在 pyproject.toml 声明Python3.12、src包发现和pygame-ce 2.x，开发依赖pytest 8.x、PyInstaller 6.x；创建 .venv 并验证64位解释器，禁止混装pygame与pygame-ce。
- [X] T002 创建 src/pvz_game/__init__.py、src/pvz_game/__main__.py、src/pvz_game/domain/__init__.py、src/pvz_game/presentation/__init__.py 及 tests/conftest.py，使包入口与测试发现可用。
- [X] T003 [P] 配置 .gitignore 忽略 .venv/、构建输出、缓存与运行日志，保留源资源及打包配置；不得忽略最终需追溯的素材来源记录。
- [X] T004 在 requirements.lock.txt 锁定经Windows/Python3.12安装验证的精确依赖，记录解释器/架构，并在 docs/development.md 写明独立环境创建及可重复安装方式。

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 建立配置、状态、命令、事件与资源边界；完成本阶段后才能集成用户故事。

- [X] T005 在 src/pvz_game/config.py 实现配置加载校验，在 assets/config/balance.json 统一数值与单位，逐字落实“schema_version=1；initial_sun>=0；tick_hz=60；plant_types、zombie_types使用唯一字符串ID；金额/生命/伤害为整数；生命及行动周期>0，价格>=0，速度>0”；错误返回可理解诊断。
- [X] T006 在 src/pvz_game/config.py 及 assets/config/balance.json 落实PlantType约束“id、price、hp、cooldown_ticks、role（producer/shooter）；producer的production_interval_ticks>0、sun_value>0；shooter的attack_interval_ticks>0、projectile_speed>0、damage>0；数值只在此引用”及ZombieType约束“id、hp>0、speed>0、bite_damage>0、bite_interval_ticks>0、contact_distance>0”；采用data-model.md首轮数值，不声称是原版测量值。
- [X] T007 在 src/pvz_game/config.py 将关卡结构校验改为“id=day_01；rows=5；cols=12；sun_schedule、spawn_schedule；生成项含tick>=0、row为0..4、有效type_id；按tick和原始序号稳定排序；至少一个僵尸，必须有限”，并拒绝超出12列范围的配置。
- [X] T008 [P] 在 src/pvz_game/domain/models.py 定义标准库模型，落实“实体ID为同一局内唯一递增正整数；重新开始建立新局，禁止复用旧事件”及“phase=menu/playing/paused/won/lost；tick>=0；sun>=0”；包含level_id、next_spawn_index、卡片ready_tick、实体集合、selection、事件序号，导出只读快照。
- [X] T009 在 src/pvz_game/domain/models.py 定义运行实体，逐字落实“row 0..4，col 0..11；plant_id可空；每格最多一个存活植物；单位移除时原子清空占用”，“hp 0..type.hp、action=idle/producing/attacking/dying、next_action_tick”，“target_plant_id可空、action=walking/biting/dying、next_bite_tick；target必须存活且同排，消失后恢复walking”；实体包含data-model.md中全部位置、类型和生命字段。
- [X] T010 在 src/pvz_game/domain/models.py 补全Projectile、SunPickup、LawnMower、Selection与AppearanceSelection，逐字落实“damage>0、active；按上一位置到当前位置的线段命中最近存活敌人一次，不穿透”，“value>0、expires_tick、collected；只能收集一次；铲除向日葵不删除已经生成的阳光”，“row唯一且0..4、state=ready/sweeping/spent、previous_x、x；每局正好5台；ready→sweeping→spent，不可逆，重开新建”，“none/plant/shovel三选一；plant必须有有效type_id；切换自动取消旧选择”及“默认default；只可在menu修改，重开保留，会话退出不保存”。
- [X] T011 在 src/pvz_game/domain/commands.py 定义 contracts/simulation.md 的全部命令、session_id/tick/顺序号、accepted及reason_code，并定义唯一(session_id,event_seq)事件；命令不接受任何皮肤数值。
- [X] T012 [P] 在 src/pvz_game/resources.py 实现以模块__file__为基准的只读资源定位、中文缺失提示和本地日志；日志目录LOCALAPPDATA/PvzMiniGame/logs，最近3份各最多1MB，日志不可写仍显示错误，不记录用户名/完整用户路径。
- [X] T013 在 tests/unit/test_config_and_models.py 验证T005至T011的无效配置、重复ID、边界、空引用、唯一占格与不可变快照，确认domain不导入pygame；不增加镜像实现的无意义测试。

**Checkpoint**: 配置与数据约束通过，资源路径不依赖工作目录，模拟层不依赖画面。

## Phase 3: User Story 1 - 双击启动并完成一局游戏 (Priority: P1) MVP

**Goal**: 获取可运行的压缩发行包，完成阳光、种植、战斗、铲子、割草机、暂停、胜负与重开；扩展后须完整显示五行十二列，阳光HUD无遮挡。
**Independent Test**: 从发行目录双击启动，完成一次胜利与失败，铲除不退款、每行救场仅一次，重开恢复状态；并检查十二列同屏、末列可操作及右上阳光可见。本阶段可使用明确标识的内部占位美术，不代表US2或完整产品视觉验收通过。

### Tests for User Story 1

- [X] T014 [P] [US1] 在 tests/unit/test_economy_and_planting.py 编写资源增减、单次收集、过期、冷却、占格、无效行列、快速连点与铲子事务测试，包含expires_tick前一tick可收集、到期当tick及后一tick拒绝且不入账、暂停恢复仍按模拟时间判断，以及铲除不退款、不重置冷却和已产阳光保留；先确认规则未实现时测试失败。
- [X] T015 [P] [US1] 在 tests/unit/test_combat_and_lifecycle.py 编写同排命中/啃咬、连续碰撞、死亡停用、割草机单次/跨行/后续突破、同tick死亡与结算、暂停、重开及旧局命令拒绝测试，补充投射物出生tick不移动/不命中、下tick开始更新、先命中致死则不啃咬、同距离按目标ID及多投射物竞争测试，先确认失败再实现。

### Implementation for User Story 1

- [X] T016 [US1] 在 src/pvz_game/domain/simulation.py 实现step(commands)、稳定命令顺序、只读快照和唯一事件；非playing不推进tick，遵循 contracts/simulation.md 六步处理顺序，失败优先于胜利且结算仅一次。
- [X] T017 [US1] 在 src/pvz_game/domain/systems.py 实现有限波次、自然阳光、向日葵产出、点击收集/过期，以及种植的原子扣费/生成/占格/冷却更新；失败状态全不变；CollectSun按tick < expires_tick判断有效，到期返回sun_expired不入账，即使对象尚未清理也不得收集；速度按像素/秒除60换算。
- [X] T018 [US1] 在 src/pvz_game/domain/systems.py 实现同排前方攻击、最近目标线段命中、僵尸移动/接触啃咬及目标丢失后继续前进；死亡立即失去逻辑作用，已发投射物继续飞行；Projectile记录born_tick，出生tick不移动/不命中；按 contracts/simulation.md 先已有投射物移动命中、再植物产出/射击、后存活僵尸啃咬的顺序执行，稳定ID决定平局顺序。
- [X] T019 [US1] 在 src/pvz_game/domain/systems.py 实现铲除与五行割草机，清扫使用上一位置至当前位置的连续碰撞，只消耗本行一次；无可用救场时越界失败，清扫离场不清除以后生成的敌人。
- [X] T020 [US1] 在 src/pvz_game/domain/simulation.py 实现选择、取消、暂停/恢复、重开、返回菜单和胜负阶段；重开重建实体/资源/冷却/波次/割草机与事件序列，保留会话外观、清除操作选择。
- [X] T021 [P] [US1] 在 src/pvz_game/presentation/input.py 实现逻辑画布坐标反变换、留边过滤、UI→阳光→草坪单次命中顺序、右键/Esc取消和阶段输入拦截；命令只读当前快照，不自行裁决资源或伤害。
- [X] T022 [P] [US1] 在 src/pvz_game/presentation/scenes.py 实现中文菜单、说明、卡片价格/冷却、铲子、暂停遮罩、胜负与重开/返回/退出入口，以及reason_code中文反馈；成功种植取消选择，铲除后保持铲子选择。
- [X] T023 [US1] 在 src/pvz_game/presentation/renderer.py 实现单位、阳光、豌豆、割草机与UI绘制，在 assets/skins/prototype/manifest.json 提供标注内部占位的可用资源，并在 assets/fonts/ 放入可分发中文字体、assets/sources.json 记录来源；占位不得标为原版合格。
- [X] T024 [US1] 在 src/pvz_game/app.py、src/pvz_game/__main__.py 集成pygame事件循环、初始原型960×720窗口、等比缩放、60Hz模拟与独立渲染；单帧最多追赶5步、极长阻塞丢弃积压，暂停清空累积时间但继续处理退出事件。十二列版本窗口由T030调整。
- [X] T025 [US1] 在 tests/integration/test_playable_loop.py 与 tests/replay/test_base_replay.py 验证完整对局、输入优先级、阶段屏蔽、30/60FPS下同tick结果与至少一套实际可胜关卡操作；运行T014/T015修复失败并将可胜策略记入 docs/validation/us1.md。
- [X] T026 [US1] 在 packaging/launcher.py、packaging/pvz_game.spec 与 tools/build.ps1 实现Windows x64 Python3.12 onedir构建，先诊断版再windowed；收集包、依赖、资源、字体，运行核心测试后输出 dist/PvzMiniGame/，校验错误提供中文提示。
- [ ] T027 [US1] 在 packaging/开始游戏.txt 写完整解压/保留资源/整体移动/鼠标操作说明，通过 tools/build.ps1 打包当前US1中间原型到 dist/PvzMiniGame-windows-x64.zip；在 docs/validation/us1.md 记录双击、断网、中文空格路径与移动目录的实际测试，并明确该包不含后续T029至T033的十二列地图修订，不作为十二列功能或最终发行验收产物；最终包须在T058之后重新构建和验证。

**Checkpoint**: US1可独立演示；US2和US3仍是首版必需内容，不能在此宣称全部完成。

### US1 规格修订：十二列地图与阳光可读性

- [X] T028 [P] [US1] 在 tests/unit/test_config_and_models.py 与 tests/integration/test_playable_loop.py 验证 day_01 必须为 rows=5、cols=12，合法列为0..11、列12拒绝，草坪末端x=969位于1050逻辑画布内，且完整地图不依赖滚动或裁切。
- [X] T029 [US1] 在 assets/levels/day_01.json 与 assets/config/balance.json 将关卡/布局数据同步为五行十二列、画布1050×600、grid_x=105、grid_y=160、cell_width=72、cell_height=76、spawn_x=1010，并校验所有草坪格及出怪位置均在画布边界内；配置结构校验由T007同步支持。
- [X] T030 [US1] 在 src/pvz_game/app.py 与 src/pvz_game/presentation/input.py 将战斗初始窗口调整为1260×720、逻辑画布调整为1050×600；设置1050×600逻辑像素客户区为最小窗口尺寸并阻止缩至其下，保留更大窗口的等比例居中缩放/留边拒绝，验证鼠标坐标能正确反映射到第一列与第十二列。
- [X] T031 [US1] 在 src/pvz_game/presentation/renderer.py、src/pvz_game/presentation/prototype_renderer.py 与 src/pvz_game/presentation/scenes.py 扩展战斗画布和草坪边界，令五行十二列同屏且格子保持72×76逻辑尺寸；窗口客户区不得缩至1050×600逻辑像素以下，不滚动、不裁格。
- [X] T032 [US1] 在 tests/integration/test_playable_loop.py 与 tests/unit/test_config_and_models.py 覆盖1260×720、1920×1080及最低支持客户区1050×600的12列显示/输入映射、末列放置、场外点击拒绝；确认窗口无法缩小到最低尺寸以下并运行完整US1规则回归。
- [X] T033 [US1] 在 src/pvz_game/presentation/renderer.py、src/pvz_game/presentation/input.py 与 src/pvz_game/presentation/scenes.py 将阳光HUD固定在战斗画面右上区域并在全部世界图像之后绘制，设置HUD命中区域优先于拾取物/草坪；调整关卡文字、暂停按钮与场上对象区域使其互不遮挡。

## Phase 4: User Story 2 - 原版界面及动作 (Priority: P2)

**Goal**: 用经核验的PC初代经典版视觉和动作替换原型，保留可玩闭环。
**Independent Test**: 不启用小狗皮肤，逐项对照扩展战斗画布上的界面和三角色全部适用动作，并验证右上阳光HUD无遮挡、铲子、割草机及发射/接触同步。

### Tests for User Story 2

- [X] T034 [P] [US2] 在 tests/integration/test_asset_manifest.py 编写默认清单非法rect、越界图集、零时长、缺动作、锚点/裁切不合法与缺基础资源测试，按data-model.md约束先确认验证器尚未实现时失败。

### Implementation for User Story 2

- [X] T035 [P] [US2] 在 docs/art/reference-board.md 收集并核验PC初代经典版菜单/草坪/卡槽/三角色/铲子/割草机/阳光/豌豆参考，逐状态记录来源、视频时间段、比例、方向、节奏和关键动作对照项，制作前固定 contracts/assets-and-release.md 中布局2像素、角色宽高5%、周期5%且至少1tick、接缝锚点1像素及事件同步1tick的测量基准和维护者造型审核方式；资料不足明确列缺项，不擅自以近似风格通过。
- [X] T036 [US2] 在 src/pvz_game/presentation/skin_catalog.py 实现清单读取，逐字落实“schema_version=1、skin_id、display_name、完整角色映射、卡片/预览、图集、clips及source_refs”，“每帧rect宽高>0、duration_ticks>=1，图集内边界合法”，“每帧必须记录source_size与trim_offset；source_size宽高>0，裁切偏移不得超出原始画布”，“anchor、muzzle和contact使用每帧未裁切逻辑画布坐标；不能以图片尺寸推导碰撞盒”及clip的loop、帧序列、动作周期相位。
- [X] T037 [US2] 在 tools/validate_assets.py 接入清单校验，验证source_refs及 assets/sources.json 的“来源URL/本地来源、角色、动作、版本、参考时间段及制作说明”；默认资源缺失中文错误中止开局，校验失败返回非零退出码。
- [X] T038 [US2] 在 assets/skins/default/manifest.json、assets/skins/default/atlas.png 制作或整理符合参考的三角色完整动作，覆盖 sunflower idle/produce/hit/die、peashooter idle/attack/hit/die、zombie_basic walk/bite/hit/die；附带卡片/预览，受击允许原版闪烁表达，不以静态占位冒充动作。
- [X] T039 [US2] 在 assets/skins/default/ui-atlas.png 和 assets/skins/default/manifest.json 完成参考对应的菜单、草坪、卡槽、铲子及割草机待命/清扫/离场、阳光和豌豆资源，并在 assets/sources.json 登记可追溯来源。
- [X] T040 [US2] 在 src/pvz_game/presentation/animation.py 通过模拟action/state/phase驱动图集帧与锚点，落实“视觉事件只驱动表现，不生成伤害或资源”；受击叠加不重置攻击，逻辑死亡后独立表现播完销毁；模拟producing/attacking/walking/biting/dying显式映射到清单produce/attack/walk/bite/die。
- [X] T041 [US2] 在 src/pvz_game/presentation/renderer.py、src/pvz_game/presentation/scenes.py 接入完整默认资源，发射点/接触点跟随锚点，脚底与比例固定；保留中文与仅两张卡片的明确范围差异，不依赖prototype资源发布。
- [X] T042 [US2] 在 tools/preview_animations.py 实现逐角色逐状态、状态过渡和循环预览及截图导出，支持观察至少3循环、发射/接触相位和死亡移除，不修改游戏数值。
- [ ] T043 [US2] 在 docs/validation/default-visuals.md 按 contracts/assets-and-release.md 视觉验收尺度逐项记录参考/实际帧、测量值、维护者造型审核结论及全部适用过渡证据，运行T028及US1回归；记录每个缺项与实际结果，默认素材和视觉未通过前不得勾选本项。

**Checkpoint**: 默认模式可独立验收；自动资源校验不能代替原版一致性审核。

### US2 规格修订：扩展画布视觉与阳光HUD

- [X] T044 [P] [US2] 在 docs/art/reference-board.md 与 specs/001-pvz-mini-game/contracts/assets-and-release.md 更新扩展战斗画布的参考映射和验收尺度，固定1050×600坐标、五行十二列与原版参考的对应区域，标注新增横向地图及HUD差异，禁止将未测参考项标为通过。
- [X] T045 [US2] 在 tests/integration/test_playable_loop.py 与 docs/validation/default-visuals.md 验证并记录扩展画布下阳光HUD的前景层级、最密集单位/场上阳光遮挡用例与输入命中顺序；右上图标和余额必须完整可见，HUD点击不得触发阳光拾取或草坪操作。

## Phase 5: User Story 3 - 小狗换肤 (Priority: P3)

**Goal**: 两方独立选择经用户确认的具名小狗皮肤，保留完整动作和完全一致的玩法结果。
**Independent Test**: 默认、只换植物、只换僵尸、双方换肤均可胜利/失败/重开；检查狗狗角色高度至少75%、相邻最宽轮廓不重叠、重复动作循环至少60 tick并以至少30Hz采样；缺皮肤回退默认，至少3组固定操作回放数值与结果完全一致。

### Tests for User Story 3

- [X] T046 [P] [US3] 在 tests/integration/test_skin_selection.py 编写menu独立选肤、战斗中拒绝改肤、卡片/预览同步、重开保留、退出不保存及缺动作/损坏图集回退测试；确认缺功能时失败。
- [X] T047 [P] [US3] 在 tests/replay/test_skin_invariance.py 编写至少3组固定关卡/输入的四种外观组合回放，对比不含外观字段的快照摘要和玩法事件，验证价格、生命、伤害、冷却、移动、碰撞与胜负均相同。

### Implementation for User Story 3

- [X] T048 [P] [US3] 在 docs/art/dog-mapping.md 根据可追溯照片/视频核验具名小狗身份，提出向日葵/豌豆射手/普通僵尸三角色候选、外观参考及待机/产出/攻击/行走/啃咬/受击/死亡的适用动作方案；逐字落实“确认前状态proposed”，不得凭标签推断长相。
- [X] T049 [US3] 向用户展示 docs/art/dog-mapping.md 中具体可审阅的三角色映射、参考和动作适配，获取并记录确认日期与内容；本项完成前不得开始T050正式皮肤制作，等待期间可推进其他无依赖任务。
- [X] T050 [US3] 在 assets/skins/dogs/atlas.png 与 assets/skins/dogs/manifest.json 制作已确认小狗三角色的全部适用动作、卡片和预览，遵守T036定义的帧/锚点清单契约及contracts/assets-and-release.md，并在 assets/sources.json 登记来源；头/躯干/肢体有真实连贯动作，不用静态图抖动或任意犬种替代。
- [X] T051 [US3] 在 src/pvz_game/presentation/skin_catalog.py 实现两方完整皮肤预检与“默认外观缺必需资源则中文错误并中止开局；小狗外观不完整则整套所选阵营回退default并提示，不逐帧混搭”；未选阵营保持原选择，不将皮肤数据传入模拟。
- [X] T052 [US3] 在 src/pvz_game/presentation/scenes.py 和 src/pvz_game/app.py 接入植物方/僵尸方独立default/dogs选择、名称/预览、不可用提示与重开保留；仅menu允许改肤，铲子和割草机不换小狗皮肤。
- [X] T053 [US3] 在 src/pvz_game/presentation/renderer.py、src/pvz_game/presentation/animation.py 接入小狗动画，保持与默认模式相同的模拟动作相位、逻辑碰撞和发射时机，通过朝向/姿态/标识区分职责与阵营，并保证卡片/预览/场上角色一致。
- [ ] T054 [US3] 在 docs/validation/dog-visuals.md 按 contracts/assets-and-release.md 连续性/事件同步尺度记录每个小狗动作至少3循环、锚点偏差和全部适用过渡审核、身份映射一致性、缺资源回退与四种组合胜负/重开结果；运行T038/T039及US1/US2回归，记录证据而非以默认回退替代完整小狗内容。

**Checkpoint**: 三个故事都已实现并分别验收；正式发行仍需完成跨系统与人员验证。

### US3 规格修订：狗狗尺寸与流畅动画

- [X] T055 [P] [US3] 在 tests/integration/test_animation.py 与 tests/integration/test_asset_manifest.py 验证 assets/skins/dogs/manifest.json 中idle、walk、produce、attack、bite各重复循环总时长至少60 tick；一次性hit/die不要求60 tick，缺少动作或不足时长的清单必须报告对应角色/动作。
- [X] T056 [US3] 在 assets/skins/dogs/manifest.json、tools/validate_assets.py 与 tests/integration/test_asset_manifest.py 校验小狗重复循环时长至少60 tick及动画帧边界/锚点；为每个角色记录参考高度和各帧非透明像素遮罩，以统一等比例缩放使高度不低于默认角色75%，逐一比较三种角色全部两两组合（含同角色配对）在同一行相邻列格子中心处的所有动作帧对，依据trim_offset与脚底锚点还原后非透明像素不得相交，并报告冲突角色、动作及帧编号。
- [X] T057 [US3] 在 src/pvz_game/presentation/animation.py、src/pvz_game/presentation/renderer.py 与 tools/preview_animations.py 实现/验证小狗循环在固定60 tick模拟中平滑呈现，动画采样至少30Hz且绘制目标60FPS；覆盖待机/行走/产出/攻击/啃咬循环及状态切换，不改变伤害、产出、移动、碰撞或一次性受击/死亡时长。

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 可重复构建、稳定性、性能及完整发行验收。

- [X] T058 在 tools/build.ps1 完善最终构建流程：运行规则/集成/回放/完整资源检查，拒绝prototype或缺小狗资源的正式发行，按 packaging/pvz_game.spec 收集完整字体/默认/小狗资产，复制 packaging/开始游戏.txt 并压缩为 dist/PvzMiniGame-windows-x64.zip。
- [ ] T059 [P] 在 tools/benchmark.py 建立1050×600画布下45植物/30僵尸/100投射物/20阳光的60秒压力场景，测量平均FPS≥55、95%帧≤33ms、狗狗动画采样≥30Hz、绘制目标60FPS与主菜单启动目标10秒内，在 docs/validation/performance.md 记录机器配置、首次/冷启动和实测数据；不足则定位优化并回归，负载不是玩家单位上限。
- [ ] T060 [P] 在 docs/validation/stability.md 记录30分钟持续运行、暂停/继续与重新开始各10次的操作及结果，覆盖阳光/冷却/割草机冻结、窗口恢复无时间突进、角色无消失和操作无失效。
- [ ] T061 在 docs/validation/windows-release.md 记录Windows10及11 x64标准用户、断网、无Python环境下从最终ZIP完整解压/双击/中文空格路径/整体移动的结果，并检查损坏或缺资源中文提示；记录系统与包摘要，不以开发机或dummy渲染代替实机。
- [ ] T062 在 docs/validation/beginner-playtest.md 记录3名未参与开发的电脑新手仅依随包说明、各3分钟内完成开局/收集/种植的结果；未具备参与者则记NOT_RUN且保留任务未完成，不虚构人员测试通过。
- [ ] T063 在 docs/validation/release-report.md 汇总SC-001至SC-009、FR-001至FR-022、四外观组合与素材来源/小狗确认的证据索引，标注PASS/FAIL/NOT_RUN；更新 specs/001-pvz-mini-game/quickstart.md 与 README.md 的实际启动/开发/打包及SC-009验证方式，交付前逐项记录地图同屏、阳光HUD无遮挡、狗狗75%尺寸/不重叠、重复循环≥60 tick和规则回放一致性，未验证部分明确报告。

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase1 环境 → Phase2 基础 → US1可玩/原型包 → US2默认视觉 → US3小狗换肤 → Phase6最终发行
                                  └→ 小狗参考研究可提前准备，正式制作仍受T049确认约束
```

- Phase1：T001→T002→T004；T003可在T002期间独立执行。
- Phase2：T005→T006→T007；T008→T009→T010→T011；T012独立；T013依赖T005至T011。全部完成后开始故事集成。
- US1：T014/T015规则测试已完成；T028测试可与T007结构校验并行准备，T029关卡/布局数据依赖T007结构校验；T030窗口输入和T031绘制在逻辑画布常量就绪后可并行，T032验证依赖T030/T031，T033 HUD整合依赖布局与图层准备。T027仅覆盖US1中间原型包，不验证十二列地图；最终包在T058之后重新构建并由T061验证。
- US2：T034至T043已有资产与动画基础；T044参考坐标更新可与T028至T033并行准备；T045依赖T033及窗口/HUD重排完成，T043最终视觉审核依赖T044/T045并运行相应回归。
- US3：T046/T047/T048可并行；T049确认既有映射后T050正式制作；T055循环清单测试与T056尺寸/逐帧轮廓校验可并行，T053动画播放集成依赖T050至T052及US1画布完成，T054最终造型/动作验收依赖T053及T056。映射确认前不得制作或替换正式角色素材。
- 收尾：T058构建依赖US1至US3实现任务；T059压力测试与T060稳定性检查可并行但必须使用最终构建，性能测量独占机器；T061/T062依赖T058可分别执行；T063发布报告依赖所有适用验收及T059至T062证据。任何修复改变代码/资源则重跑相关检查并重构建，避免验证旧包。

### User Story Dependencies

US1是最小可玩增量。US2依赖US1运行时，US3依赖US1规则与US2动画/皮肤基础；三者并非互不依赖，
“独立测试”指各自有清楚验收范围，不声称可以绕过基础代码独立开发或省略前置。

### Parallel Opportunities & Examples

- 环境：T003与T002不同文件；基础：T008与T005、T012可并行。
- US1：T028配置边界测试可与T007配置结构校验并行准备；T029数据更新依赖T007。T030窗口输入与T031绘制调整在逻辑画布常量确定后可并行，T032端到端窗口验证依赖两者，T033 HUD层级依赖布局/绘制结构就绪。
- US2：T034清单回归与T044参考坐标文档可并行；HUD视觉验证T045应在T033之后执行。
- US3：T046回归测试、T047皮肤不变性回放和T048素材参考审核可并行；T050正式素材制作依赖T049确认；T055循环时长测试与T056逐帧透明轮廓/尺寸检查可并行。
- 收尾：T059压力测试和T060稳定性报告使用不同记录，可并行；性能测试独占测量机器，避免互相污染数据。

## Requirement Traceability

| 要求 | 任务 |
|---|---|
| FR-001 压缩包/双击/离线 | T012、T026、T027、T058、T061 |
| FR-002 界面入口与操作 | T020至T024、T033 |
| FR-003 关卡与波次 | T007、T016、T017、T025、T028至T032 |
| FR-004 两植物一僵尸 | T006、T009、T017、T018 |
| FR-005 阳光与冷却 | T005、T006、T014、T017 |
| FR-006 校验与取消 | T014、T017、T020、T021 |
| FR-007 战斗 | T015、T018、T025 |
| FR-008 结算与重开 | T015、T016、T020、T025 |
| FR-009 原版视觉 | T035、T038、T039、T041、T043、T044 |
| FR-010 全动作 | T034、T036、T038、T040至T043、T050、T053 |
| FR-011 双方选肤 | T046、T051至T054 |
| FR-012 小狗身份与确认 | T048至T050 |
| FR-013 连续动作 | T040、T042、T050、T053至T057 |
| FR-014 规则不变与回退 | T046、T047、T051、T053 |
| FR-015 资源随包及来源 | T012、T023、T031、T037至T039、T048、T050、T058 |
| FR-016 扩展不破坏已有 | T005至T011、T025、T043、T054、T063 |
| FR-017 验证 | T013至T015、T025、T034、T043、T045至T047、T054至T063 |
| FR-018 铲子 | T014、T019、T021、T022、T025 |
| FR-019 割草机 | T007、T010、T015、T019、T025、T039、T043 |
| FR-020 右上阳光HUD无遮挡 | T033、T045、T063 |
| FR-021 小狗最小尺寸与相邻不重叠 | T056、T057、T063 |
| FR-022 小狗循环时长与流畅度 | T055、T057、T059、T063 |
| SC-001 | T061 |
| SC-002 | T062 |
| SC-003 | T054 |
| SC-004 | T043、T054 |
| SC-005 | T047、T054 |
| SC-006 | T035、T043、T049、T054 |
| SC-007 | T060 |
| SC-008 | T014、T015、T025、T054 |
| SC-009 | T028至T033、T044、T045、T055至T057、T059、T063 |

## Implementation Strategy

### MVP First

完成Phase1、Phase2与US1，获取完整可玩的内部原型包；先验证基本循环，再投入原版与小狗动画。
US1的内部占位只用于增量演示，完整首版仍必须包含US2/US3及最终验收。

### Incremental Delivery

每阶段保留已有测试与可运行入口；素材不齐时推进规则/工具/参考整理，不虚构素材或视觉通过。
在小狗映射确认点只等待受影响美术工作，遵循用户已约定流程。
Windows目标系统或试玩者不可用时按NOT_RUN报告，不勾选对应任务、不宣称完成全部首版。

## Notes

总计63项：环境4、基础9、US1共20、US2共12、US3共12、收尾6；并行任务数量按[P]标记统计。
执行后以实际验证证据勾选完成项。所有勾选均为开发任务进度，不替代需求质量清单或产品验收证据。

## US1执行记录（2026-10-25）

本轮按用户限定范围仅实施基础和US1；T001至T026曾完成并通过当时范围的验证。后续规格将关卡扩展为十二列后，发现代码仍校验九列；当前已重新完成T007及T028至T033，覆盖地图数据、显示、输入和HUD。T027中间原型包的整体移动和干净断网环境验证仍待试玩补充，保持未勾选。自动化30项历史结果见 docs/validation/us1.md，不代表本次规格修订验证。

## US2/US3执行记录（2026-10-25）

本轮按用户要求推进到US3功能实现。用户已确认被窝金围巾、嗷嗷嗷绿背心与红背心三角色映射，
确认原话和生成素材见docs/art/dog-mapping.md及generation-prompts.md。
默认角色图集/UI图集、动作控制、两方独立选择、预检回退、预览工具与回放已实现。
新增测试与原有回归合计50项通过；默认与小狗资源清单通过校验。

T043和T054保持未完成：原版严格布局/时序对照以及维护者对具名造型与完整动作过渡的最终审核仍待完成。T037资源校验和T046选肤回归测试按当前勾选状态已完成。
其中默认植物死亡采用衍生淡出，默认界面仍有本小游戏布局适配，不得声称已通过原版≤2px/周期≤5%的全部标准。
T027仍保留其干净环境/人工试玩验收缺项，且仅对应US1中间原型包。T054及T056以后未作为本轮完成任务；T055已补充狗狗循环时长回归，新版构建加强资源校验不代表全部最终发行验收完成。
实现与验收的区别详见docs/validation/default-visuals.md、dog-visuals.md。

## 尺寸、动画与发行收尾（2026-10-26）

T045、T056、T057、T058已完成。T056通过逐帧alpha遮罩验证；T057覆盖60 tick循环、动作预览与玩法不变性回归；T058完整构建并通过最终ZIP四种皮肤组合headless smoke。T059的源代码60秒压力场景达到指标，但计划要求最终发行包测量，仍须在包内运行并确认；T060至T062的持续运行、目标Windows实机和新手试玩仍未执行。T063发布报告已有初稿，待这些最终验收状态/证据齐备后完成。