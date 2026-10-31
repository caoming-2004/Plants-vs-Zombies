# Tasks: 第一版背景与角色画质、流畅度恢复

**Input**: Design documents from `specs/006-first-version-visual-quality/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 不创建独立测试编写任务；本清单聚焦现有素材管线、手动视觉验收、现有性能诊断入口及最终发行回归。

**Organization**: 按三个用户故事分阶段。所有故事优先级均为 P1；US1 与 US2 的素材工作可在基线完成后并行，US3 的最终综合测量等待两者集成。

## Phase 1: Setup

**Purpose**: 建立本功能的对照证据位置并保存第一版参考。

- [X] T001 [P] 建立 `docs/validation/006/baseline.md`，记录规格、目标设备/窗口/刷新率字段以及 005 当前性能样本的引用，标明样本的构建版本和测量范围。
- [X] T002 [P] 从 `7305e3d` 导出首版背景原图与构图截图至 `docs/validation/006/baseline/`，并在 `docs/validation/006/baseline-visuals.md` 记录来源提交、图片尺寸、房屋/道路/草坪/种植区位置及 SHA-256。

## Phase 2: Foundational

**Purpose**: 在视觉和性能改动开始前建立同机首版基线，避免改动后无法公平比较。

- [X] T003 在隔离目录 `.tools/feature-006-baseline/` 检出 `7305e3d` 并构建第一版基线包；若旧版采样入口不足，只在隔离副本增加不改变游戏逻辑、渲染或帧等待行为的诊断输出。
- [X] T004 在用户当前电脑、1260×720 窗口和同一刷新率下，用 `.tools/feature-006-baseline/` 的包对标准/压力场景各采样60秒，输出 `docs/validation/006/baseline-standard.json`、`docs/validation/006/baseline-pressure.json` 和 `docs/validation/006/baseline.md`；与 005 样本并列，准确注明版本、皮肤、设备、负载和测量差异。

**Checkpoint**: 首版构图、源图和同机性能基线可追溯；后续素材和帧率工作可并行开始。

## Phase 3: User Story 1 - 保留第一版构图并提升背景清晰度 (Priority: P1)

**Goal**: 保留第一版房屋、道路、草坪和种植区域的构图，交付高分辨率、离线可用的静态背景。

**Independent Test**: 在1050×600、1260×720和1920×1080查看同一关卡截图；按房屋、道路、草坪、种植区核对构图和清晰度，并检查种植/收集交互位置。

### Implementation for User Story 1

- [X] T005 [P] [US1] 联网核验候选草地素材的原作者、许可、分辨率及构图适配；仅当素材实际用于最终重绘时下载并将可分发资产录入 `assets/sources.json`，否则在 `docs/validation/006/background.md` 记录拒用原因。不得把未采用素材打入发行包。
- [X] T006 [US1] 以 `docs/validation/006/baseline/` 中首版背景为构图母版，结合已核实来源绘制至少2800×1200、7:3画幅的高清主图，保存为 `assets/skins/default/source/background-006-high-detail.png`；不得只放大低分辨率原图。
- [X] T007 [US1] 更新 `tools/generate_background.py`，从 `assets/skins/default/source/background-006-high-detail.png` 可重复生成离线运行图 `assets/skins/default/ui-background.png`，并将来源、作者、许可、派生说明、尺寸及哈希写入 `assets/sources.json`。
- [X] T008 [US1] 在 `assets/skins/default/manifest.json` 和必要的 `src/pvz_game/presentation/renderer.py` 路径中接入新背景，沿用缓存渲染和原逻辑画布；保存三种目标窗口截图及布局、清晰度、交互位置核对结果到 `docs/validation/006/background.md`。

**Checkpoint**: 高清背景离线显示，三种窗口尺寸下构图和交互区域符合规格。

## Phase 4: User Story 2 - 提升狗狗角色素材的清晰度 (Priority: P1)

**Goal**: 改善照片版和卡通版的面部/毛色细节与边缘质量，同时保持身份、动作、锚点、姿势速率和尺寸不变。

**Independent Test**: 导出 `dogs` 与 `dogs_photo` 的所有必要动作，检查脸部/毛色、透明边缘、闪烁、裁切、锚点与现有遮挡上限；在三种窗口尺寸检查预览和对局画面。

### Implementation for User Story 2

- [X] T009 [P] [US2] 修改 `tools/import_dog_assets.py::cartoonize_frame()`，移除64×64中间缩小和放大，在256×256姿势单元的原始有效分辨率内处理卡通颜色与轮廓；保留照片导入分支和用户源表不变。
- [X] T010 [US2] 用 `tools/import_dog_assets.py` 从原始动作表重建 `assets/skins/dogs/` 与 `assets/skins/dogs_photo/` 图集、manifest 和 provenance，保留每帧的源帧索引、既有角色映射、脚底/攻击锚点及动作时长。
- [X] T011 [US2] 用 `tools/preview_animations.py` 导出照片版/卡通版所有必要姿势到 `docs/validation/006/previews/`，通过 `tools/validate_assets.py` 和 `src/pvz_game/presentation/dog_validation.py` 核对帧时序、主体尺寸及≤25%遮挡；记录身份、细节、边缘、裁切和三档显示核对结果到 `docs/validation/006/dogs.md`，未达标时调整导入处理后重建。

**Checkpoint**: 两种狗狗皮肤均保有完整动作与角色识别，清晰度提升且无尺寸、遮挡和动画回归。

## Phase 5: User Story 3 - 恢复第一版的流畅动作帧率 (Priority: P1)

**Goal**: 保持60Hz玩法和显示节奏，在用户当前电脑的最终打包版中达到规格帧间指标并验证真人操作反馈。

**Independent Test**: 以 Windows 实际显示窗口在标准/压力场景各运行60秒，并手动完成至少20次种植拖放、铲除和阳光收集；对照 Phase 2 的首版数据。

### Implementation for User Story 3

- [X] T012 [P] [US3] 扩展 `src/pvz_game/presentation/performance.py::summarize_frame_intervals()`，保持原始帧序列并输出 `over_33ms_frames`、`longest_over_33ms_run` 和 P95；沿用 `SCENES` 固定负载，不在该函数中组装设备或窗口元数据。
- [X] T013 [US3] 更新 `src/pvz_game/app.py` 的真实窗口 benchmark，组装设备/显示驱动/刷新率/窗口信息，并接受 `--baseline-average-fps`；standard 通过条件为平均值≥58 FPS、≥第一版同条件均值的97%、P95≤18ms，pressure P95≤20ms，两场景连续两帧以上>33ms为0。JSON 包含实测值、基线、门槛和失败原因；保持60Hz玩法 tick、动作速度及最多5步追赶策略。
- [X] T014 [US3] 用最终高清背景与两类狗狗素材构建诊断包，在用户当前电脑用实际显示驱动对标准/压力各测60秒；standard 命令读取 `docs/validation/006/baseline-standard.json` 的平均值作为基线。保存 `docs/validation/006/packaged-standard.json`、`docs/validation/006/packaged-pressure.json` 及新旧并列说明 `docs/validation/006/performance.md`；若未达规格则据分段计时定位并优化 `src/pvz_game/app.py`、`src/pvz_game/presentation/renderer.py` 或相关渲染热点后重测。
- [ ] T015 [US3] 当前检查状态为 INCONCLUSIVE：最终诊断包真实窗口采样120秒，仅收到0次手动输入，见 `docs/validation/006/input-latency.json`。需由用户在可见窗口完成至少20次有效种植、铲除及阳光收集后重测；只有反馈P95≤100ms且无漏/重复时才能勾选。
- [X] T016 [US3] 在 `.tools/feature-006-baseline/` 与最终源码上用 `tests/replay/test_base_replay.py` 的同一确定性输入执行回放，并以 `tests/replay/fixtures/004-baseline.json` 核对事件序列；比较事件类型/tick、终态胜负、阳光、击杀数和割草机状态，将逐项结果与差异写入 `docs/validation/006/replay.md`，任何差异先定位并解释，不得静默更新基线。

**Checkpoint**: 最终素材集成包达到帧间/输入指标，且与首版的玩法、动画速度和结果一致。

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 构建离线发行包，保留最终验收证据并确认核心流程。

- [X] T017 [P] 更新 `specs/006-first-version-visual-quality/quickstart.md`，使截图、基线参数、诊断包、帧率/回放/真人输入命令与最终入口、输出字段及报告路径一致。
- [X] T018 使用 `tools/build.ps1 -ArtifactName PvzMiniGame-visual-quality-release` 构建独立命名的最终发行包，并用 `tools/verify_bundle.py` 检查包结构和资源完整性；不得使用默认 v0.2.0 名称覆盖既有发行物；将命令、构建标识及结果写入 `docs/validation/006/release.md`。
- [ ] T019 自动检查已通过重定位发行包 smoke（7种皮肤组合、照片菜单，见 `docs/validation/bundle-smoke.json`）；但用户要求的真人菜单完整流程、暂停/恢复及对局胜负后重开未执行。需在发布版窗口完成人工验收后勾选，见 `docs/validation/006/release.md`。

## Dependencies & Execution Order

### Phase Dependencies

- Setup T001–T002 可并行；Foundational T003 在证据目录准备后构建隔离首版，T004 依赖 T003 完成基线采样。
- US1、US2 和 US3 的独立素材/诊断代码可在 T004 后并行开发；US1、US2 各自的最终检查依赖该故事资源集成。
- US3 的综合打包场景测量 T014 依赖 T008、T011、T013 和 T004 的第一版基线；真人交互测量 T015 依赖 T014 产出的最终诊断包；回放对照 T016 使用 7305e3d 回放基准和最终模拟。
- Polish T018–T019 依赖 US1–US3 的交付检查；T017 可与 T018 并行。

### User Story Dependencies

- **US1 (P1)**: T005 → T006 → T007 → T008；独立于狗狗素材和帧率代码。
- **US2 (P1)**: T009 → T010 → T011；独立于背景重绘和帧率代码。
- **US3 (P1)**: T012 → T013 → T014 → T015；T016负责确定性回放对照；最终实机测量需等待US1与US2资源完成。

### Parallel Opportunities

- T001 与 T002 可并行。
- 基线完成后，T005、T009、T012 可并行启动，因为它们修改不同的来源/背景素材、狗狗导入器和性能采样文件。
- US1 和 US2 的完整资源制作可分别并行；仅综合打包测量 T014 需要两者都完成。
- T017 可与最终发行包构建 T018 并行准备。

### Parallel Example: Visual Asset Work

~~~text
Task: T005 核验背景候选素材与来源记录，编辑 assets/skins/default/source/ 和 assets/sources.json
Task: T009 提升卡通动作表处理分辨率，编辑 tools/import_dog_assets.py
Task: T012 扩充帧间统计，编辑 src/pvz_game/presentation/performance.py
~~~

## Implementation Strategy

### MVP First

可独立演示的最小视觉增量是 US1：首版构图不变的离线高清背景；完整功能交付仍须完成 US2 狗狗清晰度和 US3 实机帧率验收。

### Incremental Delivery

1. 先完成首版视觉与性能基线。
2. US1 背景和 US2 狗狗素材可并行制作、分别检查。
3. 完成 US3 实机综合测量与真实输入响应；不达标则在对应热点继续优化。
4. 构建最终离线包并验证核心流程，证据保存在 `docs/validation/006/`。

## Notes

- 所有任务均按 `- [ ] Tnnn [P?] [USn?] 描述 + 文件路径` 格式编写；[P] 仅用于可独立并行的文件工作。
- 本清单没有独立新增测试编写任务；实现阶段复用既有校验入口并按规格记录实机与视觉验收结果。
