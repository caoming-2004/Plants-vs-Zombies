# Tasks: 动画、操作与植物扩展

**Input**: `specs/002-animations-plants/` 中的 spec.md、plan.md、research.md、data-model.md、contracts/、quickstart.md。
**Prerequisites**: 设计文档及 `.specify/memory/constitution.md`。
**Tests**: 核心规则和各用户故事均有明确验证场景；按宪章要求为配置、事务、同tick战斗、输入、帧率和既有玩法安排针对性测试，不要求全项目采用TDD。
**Organization**: 按故事与真实依赖拆分。US2先提供四卡及植物职责，US1才能按规格对四张卡完成拖动验收；二者同为P1。US3依赖稳定的角色清单和四卡布局。

## Format

每项严格采用 `- [ ] T编号 [P可选] [US编号可选] 描述及文件路径`。`[P]`只标记无未完成前置且修改不同文件的任务。尚未完成的任务保持未勾选；勾选表示实现与任务所述验证完成，不表示人工验收已通过。

## Path Conventions

单个Python项目：`src/pvz_game/`、`assets/`、`tests/`、`tools/`、`docs/`。逻辑和渲染职责沿用现有domain/presentation边界；不增加音效、存档或新依赖。

## Phase 1: Setup

**Purpose**: 本项目的Python 3.12 x64环境、pygame-ce、pytest和打包入口已存在。本特性不需要安装新依赖或创建新项目结构，因此无设置任务。

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 建立所有故事共用的放置校验、植物职责配置和高密度素材尺度支持。

- [x] T001 [P] 为共享种植校验编写合法落点、非活动阶段、无效坐标、占格、冷却、余额不足和成功结果测试，保存到 `tests/unit/test_plant_placement_rules.py`。
- [x] T002 在 `src/pvz_game/domain/plant_rules.py` 实现纯种植校验，并让 `Simulation.command()` 调用同一规则；Presentation可用相同输入预览原因，预览本身不得扣费或生成实体。
- [x] T003 [P] 为四种PlantType职责及字段约束编写配置测试：producer/shooter/blocker需要正生命值，row_clearer不创建持久生命实体；价格为非负整数，冷却为正整数，职责专属字段缺失或多余时拒绝，位于 `tests/unit/test_config_and_models.py`。
- [x] T004 在 `src/pvz_game/config.py` 校验producer、shooter、blocker、row_clearer职责和专属字段，并在 `assets/config/balance.json` 添加wallnut（价格50、生命1200、冷却1800 tick）与jalapeno（价格125、冷却3000 tick）；已有两种植物/僵尸数值保持不变。
- [x] T005 [P] 在 `tests/integration/test_asset_manifest.py` 增加帧尺度用例，覆盖旧清单省略pixel_scale时按1处理、2×素材坐标范围合法以及非法尺度/越界帧拒绝。
- [x] T006 在 `src/pvz_game/presentation/skin_catalog.py` 向后兼容地载入pixel_scale=1或2的帧数据，并在 `src/pvz_game/presentation/animation.py` 将源像素帧尺寸/锚点正确换算到逻辑坐标；建立或复用 `src/pvz_game/presentation/coordinates.py` 作为窗口像素与1050×600逻辑坐标的共同转换规则。

**Checkpoint**: 共享种植预览与提交得到同一reason_code；旧皮肤仍能用pixel_scale=1载入；四类PlantType配置可区分。

## Phase 3: User Story 2 - 使用新增植物改变防线 (Priority: P1)

**Goal**: 加入能阻挡僵尸的坚果墙和种下后清除本行现存敌人的火爆辣椒，并在四卡中展示映射、职责和数值。

**Independent Test**: 通过固定输入在同排/其他行布置僵尸，放置wallnut和jalapeno；确认挡咬、死亡后恢复前进、整行单次击杀、费用/冷却、同tick生成顺序、结算一次及四张卡均能查看。

### Tests for User Story 2

- [x] T007 [P] [US2] 在 `tests/unit/test_new_plant_rules.py` 验证坚果墙受咬、耗尽释放格子、僵尸恢复前进，以及火爆辣椒成功（含空行）/占格/资源不足/冷却情况下的原子资源和冷却变化；空行成功不得创建持久植物或击杀事件。
- [x] T008 [P] [US2] 在 `tests/integration/test_jalapeno_row_clear.py` 验证同排多只存活敌人按ID清除一次、空行仅有一次成功表现事件、其他行/先前死亡/命令后才生成的敌人不受影响、失败优先于胜利且kill/result事件只发一次。

### Implementation for User Story 2

- [x] T009 [P] [US2] 在 `src/pvz_game/domain/systems.py` 为PlantType职责显式分支：blocker不产出或射击，仍可被既有同排target/bite路径攻击；只有shooter进入投射物攻击逻辑。
- [x] T010 [P] [US2] 在 `src/pvz_game/domain/simulation.py` 将row_clearer接入成功PlantAt事务：按共享校验后一次扣费/设冷却/清除选择；无论目标行是否为空均产生一次row_clear_started效果事件；只对命令执行时已存在的同排存活僵尸依ID调用统一damage/kill路径，不创建持久Plant。
- [x] T011 [US2] 为default与dogs两套清单增加wallnut/jalapeno的基础可运行角色、卡片和预览，并将dogs豌豆射手映射改为黄黄、坚果墙映射小宝、火爆辣椒映射小杜；保留被窝/嗷嗷嗷既有映射，在 `src/pvz_game/presentation/skin_catalog.py`、`assets/skins/default/manifest.json`、`assets/skins/dogs/manifest.json`、`assets/sources.json` 与 `docs/art/dog-mapping.md` 记录资源来源。基础动作会在US3提升到2×密度和24姿势/秒。
- [x] T012 [US2] 在 `src/pvz_game/presentation/scenes.py` 和 `src/pvz_game/presentation/renderer.py` 将卡片/标签改为由植物配置驱动，四卡同屏展示名称、价格、冷却及职责；保留铲子和右上HUD不重叠，更新中文帮助文字。

**Checkpoint**: 不依赖最终高清帧率升级即可验证四植物规则和四张卡；旧向日葵/豌豆射手的玩法结果不变。

## Phase 4: User Story 1 - 拖动卡片并准确种植 (Priority: P1)

**Goal**: 支持从四张卡拖到草坪，显示格子有效性和角色预览，同时保留原有点击选卡方式。

**Independent Test**: 逐一拖动四种可用植物至空格、占用格、草坪外和HUD，并覆盖冷却/阳光不足、右键/Esc、失焦/暂停/结算；完成20次预设操作后检查格子、反馈、费用、冷却及无双重命令。

### Tests for User Story 1

- [ ] T013 [P] [US1] 在 `tests/integration/test_drag_input.py` 覆盖press/move/release状态、成功和无效格、outside/HUD/留边释放、取消、拖动中失焦/暂停/结算，以及点击卡片仍选择不种植。

### Implementation for User Story 1

- [x] T014 [US1] 在 `src/pvz_game/presentation/input.py` 实现仅在表现层存在的DragState，记录植物类型、指针逻辑位置、悬停格与预览有效性；鼠标移动只更新拖动态，释放时至多产生一次既有SelectPlant/PlantAt命令。
- [x] T015 [US1] 在 `src/pvz_game/presentation/input.py` 用Phase 2共享放置校验从只读snapshot计算空格/占用/冷却/余额提示；成功释放提交既有PlantAt，失败只显示reason_code而不改变余额、格子、冷却或已有植物。
- [x] T016 [US1] 在 `src/pvz_game/presentation/renderer.py` 绘制跟随指针的半透明角色预览、吸附目标格和可/不可放置提示；图层不得遮挡价格、阳光HUD、目标格反馈或触发其下层控件。
- [x] T017 [US1] 在 `src/pvz_game/app.py` 路由MOUSEMOTION/MOUSEBUTTONUP并在右键/Esc、窗口失焦、暂停、胜负或场景切换时清除DragState；释放到草坪外不产生PlantAt，旧点击选卡再点击草坪仍可使用。
- [x] T018 [US1] 在 `tests/integration/test_playable_loop.py` 添加点击种植与拖动种植相同规则结果的端到端对照，并覆盖四卡的第一列/末列有效投放和释放后无双操作。

**Checkpoint**: 四卡均可通过点击和拖动种植，失败不会扣费，预览/拖动态在取消及阶段切换后消失。

## Phase 5: User Story 3 - 看清更细致、更流畅的角色动作 (Priority: P2)

**Goal**: 为五个角色、两种外观提供高密度源帧和至少24个不同姿势/秒；提高显示清晰度和动作平滑度。

**Independent Test**: 在default/default、dogs/default、default/dogs、dogs/dogs下检查五种角色全部适用clip；自动核验2×帧密度、独特帧率、循环时长、锚点和轮廓，再在1050×600、1260×720和1920×1080窗口查看画质、帧率与状态切换。

### Tests for User Story 3

- [x] T019 [P] [US3] 在 `tests/integration/test_asset_manifest.py` 和 `tests/integration/test_animation.py` 增加五角色动作覆盖、2×源像素密度、至少24个独特可见姿势/秒、狗狗循环≥60 tick、帧锚点与动作不反向修改玩法事件的检查。

### Implementation for User Story 3

- [x] T020 [US3] 在 `docs/art/role-animation-matrix.md` 固化default/dogs五角色的适用动作、朝向、脚底/发射/接触锚点、24姿势/秒与循环60 tick条件，并在 `docs/art/default-role-prompts.md` 记录经典风格高清重制提示及素材来源/许可。
- [ ] T021 [P] [US3] 为default的sunflower、peashooter、zombie_basic、wallnut、jalapeno制作≥2×密度且动作连贯的透明源帧，保存在 `assets/skins/default/source/`；不得复制相同姿势满足帧率。
- [x] T022 [P] [US3] 为dogs的被窝、黄黄、小宝、小杜、嗷嗷嗷红背心造型制作≥2×密度透明动作源帧，保存在 `assets/skins/dogs/source/`；朝向、身份配饰、四足行走/攻击及固定脚底线遵守已批准映射。
- [x] T023 [P] [US3] 扩展 `tools/import_classic_assets.py` 以可重复导入五角色高清帧、卡片/预览、trim/anchor及pixel_scale=2的default manifest，并写入角色来源记录。
- [x] T024 [P] [US3] 扩展 `tools/import_dog_assets.py` 以可重复导入五角色高清帧、卡片/预览、trim/anchor及pixel_scale=2的dogs manifest，保留可追溯源图与生成提示。
- [x] T025 [US3] 更新 `assets/skins/default/manifest.json`、`assets/skins/dogs/manifest.json`、`assets/sources.json` 与 `src/pvz_game/presentation/skin_catalog.py`，要求五角色卡片/预览及适用clip齐全、缺失狗狗阵营时整套回退default，不跨角色混搭。
- [x] T026 [US3] 在 `src/pvz_game/presentation/animation.py` 按60 tick/s时间轴安排至少24个不同姿势/秒的clip，重复循环仍至少60 tick；保证shot/bite/produce/row_clear_started等姿势只消费事件，不延迟或发起玩法命令。
- [ ] T027 [US3] 在 `src/pvz_game/app.py` 与 `src/pvz_game/presentation/renderer.py` 将1050×600逻辑几何映射到当前窗口像素尺寸直接绘制，缓存有界的alpha转换/目标尺寸帧并保留逻辑坐标hit-test，避免低分辨率整图二次放大。
- [x] T028 [US3] 在 `src/pvz_game/presentation/renderer.py` 展示wallnut待机/受击/死亡状态及jalapeno的row_clear_started整行火焰效果；动画结束时清理视觉事件，不重复造成伤害或击杀。
- [x] T029 [US3] 更新 `src/pvz_game/presentation/renderer.py` 的外观选择预览，让四个植物狗狗映射和普通僵尸名称/角色均可辨认，并更新卡片预览角色与场上角色一致。
- [x] T030 [US3] 扩展 `tools/validate_assets.py`、`src/pvz_game/presentation/dog_validation.py` 与 `tests/integration/test_asset_manifest.py` 检查五角色完整动作、至少24独特姿势/秒、2×密度、clip帧时长、非预期帧裁切为0、循环首尾锚点偏差≤2逻辑像素、狗狗75%高度和相邻角色逐帧无重叠。
- [ ] T031 [US3] 更新 `tools/preview_animations.py` 输出五角色default/dogs动作接触表与四外观组合预览，并对1050×600、1260×720、1920×1080窗口按视觉清单检查裁切/锚点/遮挡/闪烁/透明边缘，将每项与截图记录到 `docs/validation/visual-quality-v2.md`；未实际审核的项目标NOT_RUN。

**Checkpoint**: 新角色动作资源覆盖完整，关键动作确有24个不同姿势/秒，四种外观组合规则一致，窗口放大清晰度和目标性能有实测证据或明确NOT_RUN。

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 保护核心闭环、验证性能/输入、更新离线发行包并汇总验收证据。

- [x] T032 在 `tests/replay/test_skin_invariance.py` 扩展四种外观组合回放，逐项比较sun、Plant、Zombie、Projectile、击杀、事件顺序/tick、胜负和重开状态摘要完全一致。
- [ ] T033 更新 `tools/benchmark.py` 覆盖四卡/高密度五角色素材和新renderer；标准场景及固定压力场景（1050×600、45株植物、30只僵尸、100枚投射物、20个阳光）各连续测量60秒，记录硬件、平均FPS、P95帧间隔、姿势采样及输入事件到首个可见预览延迟；门槛为标准场景≥58FPS/P95≤25ms、压力场景≥55FPS/P95≤33ms、压力输入P95≤50ms，写入 `docs/validation/visual-performance-v2.md`；dummy不得冒充实机结果。
- [ ] T034 执行 `.venv/Scripts/python.exe -m pytest -q`、`.venv/Scripts/python.exe tools/validate_assets.py` 及 `specs/002-animations-plants/quickstart.md` 中可自动运行的验证步骤，将精确命令与实际通过/失败记录到 `docs/validation/feature-002-regression.md`。
- [ ] T035 在真实窗口完成20次预设拖放、空格/占格/余额/冷却/取消/失焦及火爆辣椒/wallnut试玩；在固定压力场景记录输入至可见预览延迟和丢失/重复操作数，并把各项次数、落点、反馈、费用和结果记录到 `docs/validation/drag-and-plants-v2.md`。
- [x] T036 对照 `specs/001-pvz-mini-game/quickstart.md` 回归阳光收集、现有两植物、铲子、割草机、暂停、胜负和重开，将结果记录到 `docs/validation/feature-002-regression.md`，失败时先修复再继续发行。
- [x] T037 更新 `README.md`、`packaging/开始游戏.txt`、`specs/002-animations-plants/quickstart.md` 与 `tools/build.ps1`，说明四张卡、拖动/点击、火爆辣椒/坚果墙和完整离线资源随包；正式构建保持PyInstaller onedir结构。
- [x] T038 使用 `tools/build.ps1` 构建最终ZIP，运行 `tools/verify_bundle.py` 将包移至中文/空格路径，验证四种外观组合启动并在 `docs/validation/bundle-002.json` 记录退出码和SHA256；实际鼠标试玩与系统断网/干净Windows环境另行如实记录。
- [x] T039 在 `docs/validation/release-report-002.md` 汇总FR-001至FR-015、SC-001至SC-007、测试、素材来源和未完成的目标Windows/人工验收；仅根据证据标PASS/FAIL/NOT_RUN。

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase1 Setup(无环境改动) → Phase2 Foundation → US2 新植物 → US1 四卡拖动 → US3 高清/动画 → Phase6 回归与发行
```

- Setup无需装依赖或新建项目；所有故事依赖Phase2共享种植校验、角色化配置、像素尺度与坐标约定。
- US2须先登记坚果墙/火爆辣椒并展示四卡；US1的验收明确要求拖动四张卡，因此US1依赖US2完成。
- US3依赖五角色ID和四卡控件几何；它将US2阶段的基础素材替换为高清24姿势/秒素材。
- T001、T003、T005分别修改独立测试文件，可并行；各自实现任务T002、T004、T006依赖对应测试/约束已明确。
- T007/T008分别修改单元测试和整行清除集成测试，可并行；T009/T010分别修改systems.py与simulation.py，可并行，均依赖Phase2且需完成T007/T008验收。
- T021/T022分别生成default/dogs源图，可并行；T023/T024分别修改两个独立导入器，可并行，且必须等各自源图完成。
- US1鼠标状态、绘制预览与app.py路由涉及不同文件但共享DragState约定；先确定T014接口，再完成T015/T016/T017；测试T018覆盖集成结果。
- T032回放、T033性能、T034整套回归共用机器资源，应顺序运行或确认无互相干扰；T038发行包依赖所有代码、资源、构建和回归修复完成。

### User Story Dependencies

- **US2 (P1)**: Phase2后可独立验证两种植物规则和基础四卡；保留旧点击种植。
- **US1 (P1)**: 依赖US2提供完整四卡，之后点选与拖放均可验证同一规则。
- **US3 (P2)**: 依赖US2的五个角色ID/职责和US1的四卡布局；高画质是既有角色和新角色的升级，不改玩法。

### Parallel Opportunities

- Foundation：T001、T003、T005；Story2：T007和T008；Story3：T021与T022、T023与T024。
- 不要并行修改同一个manifest、同一Presentation文件或共享性能测试机器。
- 对源图、导入器、manifest和Renderer按依赖逐层推进；单个文件在相邻任务间保持串行。

## Requirement Traceability

| Requirement / Outcome | Tasks |
|---|---|
| FR-001 拖动卡片并放置 | T013-T018 |
| FR-002 拖动预览、无效位置与取消 | T013-T017 |
| FR-003 放置的费用/格子/冷却事务 | T001-T002、T013-T015 |
| FR-004 保留点击并共享规则 | T001-T002、T013-T018 |
| FR-005 四张卡同时显示 | T011-T012、T029 |
| FR-006 坚果墙阻挡 | T007、T009、T012、T028、T034-T036 |
| FR-007 火爆辣椒即时整行清除 | T008、T010、T028、T034-T036 |
| FR-008 角色卡片/预览/职责与缺失回退 | T012、T025、T029-T031 |
| FR-009 黄黄/小宝/小杜映射及原映射保留 | T012、T020-T025 |
| FR-010 角色状态和24姿势/秒 | T019-T026、T030-T031、T033 |
| FR-011 高清、锚点与连续动作 | T019-T031 |
| FR-012 60FPS、输入响应及外观规则不变 | T026-T028、T032-T035 |
| FR-013 离线角色素材随包 | T020-T025、T037-T038 |
| FR-014 原有核心/铲子/割草机/暂停/胜负/重开 | T032、T034-T039 |
| FR-015 配置集中、外观不改规则 | T004、T032、T034 |
| SC-001 拖放20次/零误操作 | T013-T018、T035 |
| SC-002 墙与辣椒规则 | T007-T010、T034-T036 |
| SC-003 四卡与映射 | T011-T012、T029、T035 |
| SC-004 实机60秒FPS/动画更新/姿势/输入延迟 | T019-T027、T030-T035 |
| SC-005 四组合状态完全一致 | T032 |
| SC-006 既有功能回归 | T034、T036-T039 |
| SC-007 固定压力场景FPS与P95帧间隔 | T033-T035 |

## Implementation Strategy

### MVP First

先完成共享校验/配置，再完成US2规则和四卡Roster，随后完成US1拖放四卡全覆盖。US1依赖US2，二者共同构成可试玩P1增量；不得把拖动仅验证在旧两张卡后宣称US1完整。US3高清动作跟进，不改变规则。

### Incremental Delivery

1. Phase2通过后可验证旧规则及新role配置。
2. US2完成后可用点击方式分别试玩坚果墙和火爆辣椒，确认职责和整行清除。
3. US1完成后以四张卡完成拖动/点击、成功/失败/取消流程。
4. US3完成后验证两套五角色高清动画、帧率、性能和四种外观组合。
5. 最终发行前运行完整回归、标准设备测量、包内移动路径检查；未能执行的线下检查保持NOT_RUN。

## Notes

- 共39项：Foundation 6、US2 6、US1 6、US3 13、Polish 8；Setup无任务（无新环境/依赖）。规格含7项成功标准（SC-001至SC-007），SC-004还覆盖压力场景输入延迟。
- 已完成项依据代码、测试或构建/资源输出勾选；真实窗口、目标硬件、用户试玩和严格视觉审核仍保持未完成。
- requirements.md已与当前spec的三项用户故事和无音效范围同步；后续修改spec时须一并维护清单。

