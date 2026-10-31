# Tasks: 高清背景、狗狗素材与运行流畅度

**Input**: `specs/005-hd-background-dogs-performance/spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/appearance-and-performance.md`, `quickstart.md`  
**Prerequisites**: 现有 Python/pygame 游戏与三张已保留的用户动作表  
**Tests**: 规格明确要求画质、遮挡、动画、玩法与实机性能验收，因此列出相应验证任务。  
**Organization**: US1 背景、US2 狗狗双外观、US3 真实运行流畅度；每个故事可独立验收。

## Format: `[ID] [P?] [Story] Description`

- **[P]** 表示修改不同文件且不依赖同阶段尚未完成任务，可并行执行。
- **[US1]–[US3]** 对应 `spec.md` 中三个用户故事。
- 文件路径均以仓库根目录为基准。

## Phase 1: Setup

**Purpose**: 先建立可用于旧版和新版的实机采样入口，保留新素材与原画面基线。

- [X] T001 在 `src/pvz_game/app.py` 与 `tools/benchmark.py` 增加仅用于采样的真实窗口性能入口，固定标准场景为5向日葵、5豌豆射手、5僵尸、10投射物、3阳光、5割草机，压力场景为45植物、30僵尸、100投射物、20阳光、5割草机；两场景均输出60秒帧间序列、平均FPS、P95及连续>50ms帧数，保留既有dummy基准入口，不改玩法或画面素材。
- [X] T002 [P] 在 `docs/validation/dog-source-intake-005.md` 核对三张原件的 SHA-256、1619×971 尺寸、10×6 顺序与身份映射，检查 60 帧非空、红黄杂点、帧间串色及小杜火焰主体，记录需清理的具体帧。
- [X] T003 在 `docs/validation/005/baseline.md` 记录现有背景的三个目标窗口截图、逻辑网格位置和 `default`/`dogs` 固定输入回放结果，供视觉和玩法回归比较。

**Checkpoint**: 同一性能入口可测旧版和新版；原画面和用户源表已记录。

---

## Phase 2: Foundational

**Purpose**: 为三个故事提供统一验收输入与资源边界。

- [ ] T004 在 `tools/build.ps1` 打包含T001采样入口但尚未更换背景/狗狗素材的基线版，并在 `docs/validation/005/baseline.md` 记录用户当前电脑真实窗口标准与固定压力场景各60秒数据、设备、驱动、窗口、截图及构建标识；不得把SDL dummy结果作为实机基线。
- [X] T005 [P] 在 `tests/replay/fixtures/005-baseline.json` 保存固定输入的模拟事件、tick、资源、击杀与胜负基准，供背景、皮肤和性能改动后逐项比对。
- [X] T006 在 `assets/sources.json` 登记三张原始用户动作表的名称、角色、路径、SHA-256 和照片/卡通派生关系；原件保持不变且运行时不需网络。

**Checkpoint**: 后续工作可独立比较真实画面、玩法和素材来源。

---

## Phase 3: User Story 1 - 清晰且可辨认的草坪背景 (Priority: P1) 🎯 MVP

**Goal**: 在不改变房屋、道路、种植格和输入坐标的情况下提升草坪实际细节及窗口画质。

**Independent Test**: 在三种窗口尺寸打开只有背景改动的版本，对照旧截图检查清晰度、网格、角色对比及离线显示，完成种植和收集操作。

### Tests for User Story 1

- [X] T007 [US1] 在 `tests/integration/test_background_layout.py` 验证 1050×600 逻辑网格的原点、格宽高和背景可视区域在替换后不变，缩放窗口后的输入命中位置仍对应原格。

### Implementation for User Story 1

- [X] T008 [P] [US1] 在 `assets/skins/default/source/` 保存可核查授权的高细节背景原件或组成素材，并在 `assets/sources.json` 记录作者、链接、许可、必要署名、SHA-256 与改编方式；不采用许可不明的游戏截图。
- [X] T009 [US1] 在 `assets/skins/default/ui-background.jpg` 制作保留原房屋、道路、12×5 草坪布局的高清本地背景，并在 `assets/skins/default/manifest.json` 指向该资源；检查真实细节，不能仅插值放大旧 JPEG。
- [X] T010 [US1] 在 `src/pvz_game/presentation/renderer.py` 调整背景装配与缓存，使新图在逻辑画布及三种窗口尺寸下不变形，并保留现有交互网格绘制和角色对比度。
- [X] T011 [US1] 在 `docs/validation/005/background.md` 附1050×600、1260×720、1920×1080同场景新旧截图，按原始像素尺寸逐项记录房屋边缘、草坪格线、道路纹理、角色对比度通过/失败，以及许可、离线启动、种植/收集命中和 `tests/integration/test_background_layout.py` 的实际结果。

**Checkpoint**: US1 可独立展示高清背景，输入和玩法坐标不变。

---

## Phase 4: User Story 2 - 用新照片更新狗狗并减少遮挡 (Priority: P1)

**Goal**: 照片版和卡通版都包含小杜、小宝、好孩子的完整动作；好孩子取代黄黄；缩放后角色完整且邻格主体遮挡不超过 25%。

**Independent Test**: 在菜单逐一选择两种狗狗植物外观，查看所有角色及动作、卡片、拖动和草坪；以最大姿态测试相邻格/行，并重放相同输入核对玩法不变。

### Tests for User Story 2

- [X] T012 [US2] 在 `tests/integration/test_asset_manifest.py` 增加 `dogs_photo` 完整性、三张60帧源表顺序、好孩子→peashooter映射、被窝源文件必须为 `assets/skins/dogs/source/beiwo-sheet.png`、嗷嗷嗷复用及缺失资源整套回退的验证。
- [X] T013 [P] [US2] 在 `tests/integration/test_animation.py` 与 `tests/integration/test_skin_selection.py` 覆盖照片/卡通双外观完整 clip、12–18 姿势/秒、小杜 35 姿势 2 秒清行、菜单选择及规则回放一致性。

### Implementation for User Story 2

- [X] T014 [US2] 在 `tools/import_dog_assets.py` 扩展既有 10×6 导入流程，对 `xiaodu-user-20261026.png`、`xiaobao-user-20261026.png`、`haohazi-user-20261026.png` 按身份和动作分段清理杂点/串色、稳定脚底锚点并保留 `source_frames`，从同一源表分别构建照片版所需 clip。
- [X] T015 [US2] 在 `assets/skins/dogs/source/` 制作三只狗的新卡通动作素材并记录与原始照片动作表的对应关系；在 `tools/import_dog_assets.py` 为1448×1086、4列×3行的已有 `beiwo-sheet.png` 单独导入12个灰白毛源姿势并映射 idle、produce、hit、die，保留原表金色围巾和原件；嗷嗷嗷保持原卡通造型。
- [X] T016 [US2] 在 `tools/import_dog_assets.py` 生成更新后的 `assets/skins/dogs/manifest.json`、图集和 `assets/skins/dogs/provenance.json`，将好孩子替换黄黄为豌豆射手，并让照片/卡通两版所有 `REQUIRED` 动作完整可见。
- [X] T017 [US2] 在 `assets/skins/dogs_photo/manifest.json` 与图集创建完整照片皮肤，三只用户狗取新照片动作，`sunflower` 复用 `beiwo-sheet.png` 灰白毛卡通源、`zombie_basic` 复用原卡通源；生成器在 `tools/import_dog_assets.py` 保持可重复构建。
- [X] T018 [US2] 在 `src/pvz_game/presentation/skin_catalog.py`、`src/pvz_game/presentation/input.py`、`src/pvz_game/presentation/scenes.py`、`src/pvz_game/presentation/renderer.py` 和 `src/pvz_game/app.py` 接入进入游戏前的第三种植物外观选择、预览、命令行选择与完整皮肤回退，保留僵尸经典/狗狗选择。
- [X] T019 [US2] 在 `assets/skins/dogs/manifest.json`、`assets/skins/dogs_photo/manifest.json` 设置各角色唯一显示倍率，并在 `src/pvz_game/presentation/animation.py` 与 `src/pvz_game/presentation/renderer.py` 复用现有锚点/倍率路径，覆盖草坪、卡片、拖动、死亡与菜单预览。
- [X] T020 [US2] 在 `src/pvz_game/presentation/dog_validation.py` 对两种狗狗皮肤所有必需姿态生成透明度≥96的主体掩码，排除独立火焰/光效，以相邻格/行掩码交集像素数÷较小掩码面积计算最坏遮挡率≤25%；另检查头部可辨、脚底和裁切，以结果调整T019倍率，不改玩法坐标。
- [X] T021 [US2] 在 `docs/validation/005/dogs.md` 保存两版所有角色和动作预览、身份核对、遮挡率、来源映射与 default/dogs/dogs_photo 玩法重放结果。

**Checkpoint**: 两种狗狗外观都可完整游玩，照片与卡通身份清晰，动作和规则保持一致。

---

## Phase 5: User Story 3 - 对局运行流畅 (Priority: P1)

**Goal**: 当前电脑的打包游戏满足真实窗口帧率、帧间稳定性与输入反馈目标。

**Independent Test**: 在当前电脑对新打包版标准和固定压力场景各测 60 秒，并完成 20 次真实拖放、铲除和收集操作；与 T001 旧版数据配对比较。

### Tests for User Story 3

- [X] T022 [US3] 在 `tests/integration/test_playable_loop.py` 和 `tests/replay/test_skin_invariance.py` 验证优化前后 60Hz 规则事件、角色推进、资源、胜负及小杜清行时序一致；性能指标仍以实机证据判定。

### Implementation for User Story 3

- [X] T023 [US3] 在 `src/pvz_game/app.py` 和 `tools/benchmark.py` 对真实窗口打包版的事件处理、Simulation、Renderer、窗口缩放和 flip 分段计时，定位用户所见慢帧并记录到 `docs/validation/005/performance.md`。
- [X] T024 [US3] 在 `src/pvz_game/app.py`、`src/pvz_game/presentation/renderer.py` 与 `src/pvz_game/presentation/skin_catalog.py` 依据 T023 结果优化实际瓶颈，优先复用画布缩放结果、角色帧表面和静态 UI 缓存；不得减少 60Hz 玩法 tick 或丢弃必要动画姿势。
- [ ] T025 [US3] 在 `tools/benchmark.py` 与 `src/pvz_game/app.py` 加入至少 20 次真实拖放、铲除和阳光收集操作的可见反馈测量及结果核对，输出 P95 延迟与漏处理/重复处理数。
- [ ] T026 [US3] 在 `docs/validation/005/performance.md` 记录当前电脑新打包版标准/压力场景各 60 秒平均 FPS、P95 帧间隔、最长连续 >50ms 帧数及 20 次操作 P95 延迟，与旧版同条件基线并列；未达到指标时继续定位并修复。

**Checkpoint**: 有真实显示窗口、打包版的可复测证据，且达到 SC-003/SC-004。

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 综合回归并交付可玩的离线发行包。

- [X] T027 [P] 在 `docs/validation/005/automated.md` 记录 `.venv/Scripts/python.exe -m pytest -q` 与 `.venv/Scripts/python.exe tools/validate_assets.py` 的命令和实际结果，并修复影响本功能的失败。
- [ ] T028 在 `docs/validation/005/release.md` 记录 `tools/build.ps1`、`tools/verify_bundle.py`、经典/卡通/照片三种外观离线启动、完整核心循环、暂停/重开和不同窗口试玩的实际结果，失败不得标为通过。
- [X] T029 在 `README.md`、`docs/art/dog-mapping.md` 与 `assets/sources.json` 更新好孩子、`beiwo-sheet.png` 灰白毛被窝、双外观选择、背景许可与离线资源说明，删除旧“黄黄豌豆射手”当前映射描述。

## Dependencies & Execution Order

### Phase Dependencies

- Setup T001先建立共用性能采样入口，T002–T003保存用户源表和旧画面；Foundational T004在素材替换前打包采样入口并采集旧版实机基线，T005–T006建立玩法与来源对照。
- US1、US2、US3 均可在 Phase 2 后独立开始。US3 的最终打包版验收 T026 要在 US1/US2 纳入发行包后复测，避免性能结论遗漏新增素材成本。
- Polish T027–T029 在三个故事完成后进行。

### User Story Dependencies

- **US1 (P1)**: T007–T011；不依赖狗狗素材或性能优化，可先交付背景增量。
- **US2 (P1)**: T012–T021；不依赖背景替换，需先完成素材导入，再接入菜单和尺寸验证。
- **US3 (P1)**: T022–T026；T023 可基于旧版测量，T024 依赖瓶颈结果，T026 必须用集成后的新打包版。

### Parallel Opportunities

- T002 的素材检查可与 T001 的采样入口开发并行；T003可在T001完成后记录旧画面。T005与T004文件独立。
- T008 的授权/素材核对可与 T007 的布局验证并行。
- T013 的动画/选肤验证可与 T012 的清单验证并行；T015 的卡通素材制作可在 T014 确定原始动作分段后启动。
- 各故事在基础阶段完成后可由不同人员推进，但本任务并未要求启动多个代理。

### Parallel Example: User Story 1

```text
Task: T007 在 tests/integration/test_background_layout.py 固定网格和窗口输入验收
Task: T008 在 assets/skins/default/source/ 与 assets/sources.json 核对可用背景素材授权
```

## Implementation Strategy

### MVP First

1. 完成基线和共享验收工具。
2. 完成 US1，独立交付清晰且位置不变的背景。
3. 完成 US2 双外观和 US3 实机性能，再统一打包验收。

### Incremental Delivery

每个故事达到自己的 Checkpoint 后保存证据；最终性能在所有新资源集成的打包版上重测。`[ ]` 仅在任务有实际文件和验证结果后改为 `[X]`。
