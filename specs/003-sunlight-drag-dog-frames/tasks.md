# Tasks: 阳光界面、拖铲操作与小狗动作素材

**Input**: `specs/003-sunlight-drag-dog-frames/` 中的 `spec.md`、`plan.md`、`research.md`、`data-model.md`、`contracts/` 和 `quickstart.md`。
**Prerequisites**: 已有 Python 3.12/pygame-ce 项目环境；无需创建新项目或增加依赖。
**Tests**: 本特性会改变输入/界面交互；按项目宪章增加针对性自动测试，并以真实窗口检查视觉与鼠标手感。
**Organization**: 按三项用户故事分阶段。US1/US2共享`scenes.py`、`renderer.py`和部分输入流程，按US1后US2顺序修改；US3需要用户上传素材，素材 intake task 是该故事的阻塞门。

## Format

每项严格采用 `- [ ] T编号 [P可选] [US编号可选] 描述及文件路径`。`[P]`只用于可并行且修改不同文件的任务。任务勾选表示实现及任务所述验证完成。

## Phase 1: Setup

**Purpose**: 项目结构、依赖、测试框架和Windows发行环境已经存在；无新增Setup工作。

无任务。

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 现有共享逻辑坐标、Domain命令、皮肤manifest和拖放入口已提供本功能所需基础；无需改造全局玩法模型或运行时依赖。

无任务。US3的用户图像依赖在US3阶段单独检查，不阻塞US1/US2。

## Phase 3: User Story 1 - 在左上角查看阳光余额 (Priority: P1)

**Goal**: 把余额面板移到左上角，使数值与草坪可收集阳光区分且在窗口缩放/对局状态切换中可见。

**Independent Test**: 启动对局，收集阳光、种植、暂停并恢复；在1050×600、1260×720和1920×1080逻辑呈现尺寸检查余额位置、准确性、卡片边界和阳光拾取。

### Tests for User Story 1

- [ ] T001 [P] [US1] 在 `tests/integration/test_playable_loop.py` 验证左上角HUD命中区域优先级、余额面板阻止穿透点击、面板之外草坪阳光仍可收集，并覆盖资源更新和暂停/恢复快照显示。

### Implementation for User Story 1

- [ ] T002 [US1] 在 `src/pvz_game/presentation/scenes.py` 将共享 `HUD_SUN_RECT` 移至左上角，并在 `src/pvz_game/presentation/input.py` 统一使用该矩形进行HUD点击优先级和穿透屏蔽。
- [ ] T003 [US1] 在 `src/pvz_game/presentation/renderer.py` 将阳光图标、余额和标签绘制到新面板，拖动预览遮挡检查共用新矩形，余额直接读取snapshot；确认新矩形与从x=162开始的首张植物卡、暂停控件及草坪拾取位置不重叠。
- [ ] T004 [US1] 在真实窗口检查1050×600、1260×720和1920×1080尺寸的余额裁切/遮挡/拾取表现，并将尺寸、截图和结果记录到 `docs/validation/sunlight-hud-003.md`。

**Checkpoint**: 左上角余额实时准确；原草坪阳光可点击收集；四卡、暂停和窗口坐标输入不被影响。

## Phase 4: User Story 2 - 顺手拖放植物与铲除植物 (Priority: P1)

**Goal**: 四张植物卡与铲子均可拖放，预览/反馈清楚；原点击选卡、点击铲除保留，结果由既有Domain命令权威结算。

**Independent Test**: 对四种植物测试空格、占格、草坪外、冷却、阳光不足及取消；对铲子测试有植物、空格、草坪外和取消；用点击流程重复有效种植与铲除并核对相同规则结果。

### Tests for User Story 2

- [ ] T005 [P] [US2] 在 `tests/integration/test_drag_input.py` 覆盖植物卡与铲子按下/移动/释放状态、四卡有效拖放、占格/草坪外/HUD、阳光不足/冷却、点击兼容、取消/失焦/暂停/结算清理和释放后最多一次操作；使用 `tests/conftest.py` 现有fixture。

### Implementation for User Story 2

- [ ] T006 [US2] 在 `src/pvz_game/presentation/input.py` 将 `DragState` 扩展为植物/铲子两类工具；用当前snapshot只读计算植物费用/冷却/占格原因与铲子目标植物状态，只有有效草坪释放才生成既有操作命令。
- [ ] T007 [US2] 在 `src/pvz_game/app.py` 将植物卡和铲子的鼠标按下、移动、释放路由到DragState；点击来源控件仍选择工具，拖动释放按序提交 `SelectPlant`+`PlantAt` 或 `SelectShovel`+`ShovelAt`，并在右键/Esc、失焦、暂停、结算及场景切换时取消。
- [ ] T008 [US2] 在 `src/pvz_game/presentation/renderer.py` 绘制铲子拖动光标、植物目标格高亮和可/不可铲除反馈；更新 `src/pvz_game/presentation/scenes.py` 中的操作提示，确保HUD或按钮上的释放不会穿透。
- [ ] T009 [US2] 在真实Windows窗口执行至少20次植物拖放及20次铲子拖放的有效/无效/取消场景，检查零丢失/重复操作，并将次数、反馈、结果和限制记录到 `docs/validation/drag-and-shovel-003.md`。

**Checkpoint**: 点击与拖放操作都遵循同一规则；有效操作只结算一次；无效或取消操作不误种、不误删、不扣错资源。

## Phase 5: User Story 3 - 使用小宝和小杜的60帧形象 (Priority: P1)

**Goal**: 小宝继续对应坚果墙，小杜继续对应火爆辣椒；小狗卡片、预览和场上角色使用用户上传帧且状态/方向/定位连续。

**Independent Test**: 对每个角色核对完整60帧来源与动作分组、导入清单、卡片/预览/对局映射、动作循环、锚点、帧率验证及default/dogs规则一致性。

**素材前置门**: 用户已上传小杜与小宝各60帧PNG；T010已解锁。先验证透明通道、10×6布局、逐帧差异及动作顺序，再生成源帧追溯记录。

### User asset intake gate

- [ ] T010 [P] [US3] 检查已上传素材，将每只狗原始60帧图保存在 `assets/skins/dogs/source/`，记录尺寸、透明通道、帧序、可见动作分组和SHA-256到 `docs/validation/dog-source-intake.md`。

### Tests for User Story 3

- [ ] T011 [US3] 根据T010检查出的实际输入格式，在 `tests/integration/test_asset_manifest.py` 增加导入fixture，验证小宝/小杜各60个用户源帧、角色/帧序映射、锚点字段、缺帧失败和来源摘要关联；不为未知版式预造测试数据。

### Implementation for User Story 3

- [ ] T012 [US3] 扩展 `tools/import_dog_assets.py` 以支持T010确认的图片编排；保留用户源帧并映射小宝的 `wallnut` idle/hit/die 与小杜的 `jalapeno` plant/ignite/hit/die，不重复帧填数或混用另一角色素材。
- [ ] T013 [US3] 运行导入器生成/更新 `assets/skins/dogs/atlas.png`、`assets/skins/dogs/manifest.json`、`assets/skins/dogs/provenance.json` 和 `assets/sources.json`；确认所有60帧按源角色可追溯，既有其他角色资源与skin schema v1可继续加载。
- [ ] T014 [US3] 在 `tests/integration/test_animation.py` 和 `tests/replay/test_skin_invariance.py` 验证小宝/小杜必需clip、继承自 `specs/002-animations-plants/spec.md` FR-010 的≥24独特姿势/秒和循环≥60 tick、帧序/锚点连续、阵营级损坏回退及外观不改变玩法；运行 `tools/validate_assets.py` 并将实际结果写入 `docs/validation/dog-animation-003.md`。
- [ ] T015 [US3] 使用 `tools/preview_animations.py` 生成小宝/小杜动作接触表，人工检查卡片、选肤预览、动作切换、帧边缘和脚底定位，将截图及PASS/FAIL/NOT_RUN记录到 `docs/validation/dog-animation-003.md`。

**Checkpoint**: 收到合格素材后，完整dogs外观中小宝/小杜角色和适用动作来自用户素材并通过既有清单/动画门槛；否则如实保持US3阻塞且不发布冒充素材。

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 完成响应测量、既有玩法回归、Windows onedir打包和交付记录。

- [ ] T016 扩展 `src/pvz_game/app.py` 的可选测量路径和 `tools/benchmark.py`，在Windows 60Hz设备、1260×720真实窗口的普通对局中采集至少200个拖动中的实际鼠标移动样本；从程序取出事件计时到首次显示对应预览的画面，计算P95并记录设备、刷新率、尺寸、样本数和结果到 `docs/validation/drag-and-shovel-003.md`；dummy结果不得冒充实机结果。
- [ ] T017 更新 `README.md` 与 `packaging/开始游戏.txt`，说明左上角阳光、植物卡/铲子拖放、旧点击方式及拖动取消操作。
- [ ] T018 执行 `.venv/Scripts/python.exe -m pytest -q`、`.venv/Scripts/python.exe tools/validate_assets.py` 和 `specs/003-sunlight-drag-dog-frames/quickstart.md` 中适用步骤，将自动结果/人工NOT_RUN如实记录到 `docs/validation/feature-003-regression.md`。
- [ ] T019 在US1/US2自动回归通过且US3素材门通过后，运行 `tools/build.ps1` 和 `.venv/Scripts/python.exe tools/verify_bundle.py`，确认新HUD、拖放和用户狗素材随Windows x64 onedir ZIP发布；记录哈希及检查限制到 `docs/validation/release-report-003.md`。

## Traceability

| Requirement / Outcome | Tasks |
|---|---|
| FR-001—FR-002 阳光左上显示与状态同步 | T001-T004、T018 |
| FR-003—FR-006 植物拖放、预览和原子校验 | T005-T009、T018 |
| FR-004—FR-005 铲子拖放与无效释放保护 | T005-T009、T018 |
| FR-007 保留点击种植/铲除 | T005、T007、T009、T018 |
| FR-008—FR-010 小宝/小杜映射、60帧来源和回退 | T010-T015、T018-T019 |
| FR-011 外观不改变玩法 | T014、T018 |
| FR-012 既有核心功能/发行包可运行 | T009、T017-T019 |
| SC-001 HUD窗口布局 | T001-T004 |
| SC-002 植物拖放20次零错误 | T005-T009 |
| SC-003 铲子拖放20次零错误 | T005-T009 |
| SC-004 响应P95≤50ms、无丢失/重复 | T005-T009、T016 |
| SC-005 源帧追溯及动作检查 | T010-T015 |
| SC-006 核心循环、重开与规则不变 | T009、T014、T018-T019 |

## Dependencies & Execution Order

### Phase Dependencies

```text
已有项目架构 → US1阳光HUD → US2植物/铲子拖放 → US3用户素材接入（等待上传） → 回归/测量 → Windows发行包
```

- Phase 1/2无环境或全局基础工作；现有架构可直接实现三个故事。
- US1先调整共享HUD几何和renderer；US2随后复用/修改同一`renderer.py`、`scenes.py`与Presentation输入管线，避免并行冲突。
- US3只需等T010素材输入检查后开展；素材未到不阻塞US1/US2，但最终完整功能发行包依赖US3素材通过既有validator。
- T001、T005测试文件不同，测试编写可并行；US1/US2实现任务涉及共享Renderer/Scene/Input文件，应按编号串行。
- T011依赖T010检查出输入格式；T012实现依赖T011的导入行为契约；T013导入依赖T012完成；T014/T015依赖已生成的清单/预览。
- T016/T018/T019必须在对应代码与素材稳定后执行；完整发行包T019依赖US1、US2、US3全部验收完成。

### User Story Dependencies

- **US1 (P1)**：无用户故事依赖；可先独立交付HUD调整。
- **US2 (P1)**：玩法逻辑命令已存在，无规则层依赖；由于共享UI文件，建议US1后实现。
- **US3 (P1)**：依赖用户上传每角色60帧素材；不依赖US1/US2代码，可在输入到位后并行准备，但必须在最终发行前通过资产检查。

### Parallel Opportunities

- T001与T005修改不同的集成测试文件，可并行编写。
- 已接收用户素材后，源帧整理/哈希记录（T010）可与输入/交互实现（US1/US2）并行；测试运行和全局构建需串行。
- 不要并行修改`renderer.py`、`scenes.py`、`input.py`、同一dogs manifest/来源记录，或同时执行压力/全量构建验证。

## Parallel Execution Examples

### User Story 1

US1只有一个自动测试文件且几何/绘制有先后依赖；没有安全的US1内部实现并行对。可先与US2的独立测试任务并行编写：

```text
Task: T001 HUD interaction and snapshot tests in tests/integration/test_playable_loop.py
Task: T005 plant/shovel drag state tests in tests/integration/test_drag_input.py
```

### User Story 2

T005测试可与T001并行；完成测试后，T006定义输入接口，T007使用该接口路由事件，T008基于工具态绘制反馈，应串行推进。T009需要真实窗口，不能与全局构建/另一个窗口基准同时运行。

### User Story 3

收到素材后，T010源图检查/摘要可与US1/US2界面任务并行，因为不触碰同一文件；T011素材fixture、T012导入器、T013生成清单和T014资产验证必须依赖顺序执行。两张60帧图片已接收并完成T010 intake。
## Implementation Strategy

### Playable MVP

1. 完成US1左上角阳光显示。
2. 完成US2植物卡与铲子拖放，并保持点击方式和完整核心循环。
3. 这构成可试玩的操作MVP；只有用户素材实际上传并完成US3映射/验证后，才算本Feature完整交付或制作最终发布ZIP。

### Incremental Delivery

1. US1完成后检查HUD和资源同步。
2. US2完成后在真实鼠标窗口试玩种植/铲除和失败取消路径。
3. US3素材门通过后再构建用户指定狗狗角色版本。
4. 最后执行回归、输入响应测量、Windows打包和移动路径smoke；未做实机/人工项目如实写NOT_RUN。

## Notes

- 共19项：US1 4项、US2 5项、US3 6项、Polish 4项；Setup/Foundational因现有工程条件充足而无任务。
- 测试任务是宪章IV和成功标准所必需，不代表采用全项目TDD。
- 唯一外部输入门是用户上传小宝/小杜各自60帧图片；没有该文件时，素材故事和完整最终发行保持阻塞，不能用生成图替代。








