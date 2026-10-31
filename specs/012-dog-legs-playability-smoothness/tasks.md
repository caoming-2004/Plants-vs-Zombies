# Tasks: 完整狗狗形象、五关战役与流畅表现

**Input**: Design documents from `/specs/012-dog-legs-playability-smoothness/`

**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 只保留与新规则、素材边界和关键表现直接相关的定向检查；不生成全量 pytest、外观矩阵、长时压力或安卓任务。测试任务按“先写定向检查、再实现”排列；验证任务只跑必要的命令。

**Organization**: 按规格中的 5 个用户故事分阶段。P1 的 US1/US2/US3 组成 Milestone A 可玩版本；P2 的 US4/US5 随后追加。US2 与 US3 都改 `presentation`，按顺序执行以避免同文件冲突。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可在不同文件上并行执行，且不依赖未完成任务
- **[Story]**: 所属用户故事（US1–US5）；Setup、Foundational、Polish 不带故事标签
- 每个任务都包含明确文件路径和可执行动作

## Path Conventions

单项目结构：仓库根目录下的 `src/`、`assets/`、`tools/`、`tests/`、`packaging/`。

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 准备共享数据、用户数据目录和基础关卡文件；不改变现有玩法。

- [X] T001 [P] 在 `src/pvz_game/resources.py` 增加 `user_data_dir()`，返回 `%LOCALAPPDATA%\PvzMiniGame`（Android 分支保留现有私有目录逻辑），供日志和进度文件复用
- [X] T002 [P] 新建 `assets/levels/campaign.json`：schema_version=1、5 个关卡 ID 按顺序排列、`endless.unlock_after` 为最后一关、无尽生成参数为正数；字段按 `data-model.md` 定义
- [X] T003 [P] 新建 `assets/levels/day_02.json` 与 `assets/levels/day_03.json`：rows=5、cols=12、至少 3 个波次、strength 严格递增、每波至少 1 个出怪、至少 2 个星级目标，并设置不同的敌人组合/节奏/压力条件
- [X] T004 [P] 新建 `assets/levels/day_04.json` 与 `assets/levels/day_05.json`：沿用同一关卡 schema；在 `assets/levels/day_01.json` 补 `order/name/star_goals`，但不得改变既有波次、出怪、初始阳光或天空阳光间隔

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 建立关卡/战役/进度的共享加载与校验层；完成前不要开始用户故事实现。

**⚠️ CRITICAL**: US2/US4/US5 依赖本阶段；US1 可在本阶段结束后并行开始。

- [X] T005 [P] 扩展 `src/pvz_game/config.py`：保留 `load()` 返回 day_01；新增 `load_campaign()` 与关卡校验，接受可选的 `initial_sun`、`sky_sun_interval_ticks`、`mower_rows`、`available_plants`、`star_goals`、`mode`；校验 campaign 顺序、ID 唯一、`unlock_after` 为最后一关、植物 ID 存在、波次 strength 递增、campaign 每关至少 2 个星级目标
- [X] T006 [P] 新建 `src/pvz_game/progress.py`：读写 `progress.json`（schema_version=1，字段按 `data-model.md`）；使用临时文件 + `os.replace` 原子保存；文件缺失/损坏/版本不符时回退默认进度（day_01 解锁、无尽锁定）并记录错误；提供 load/save/record_win/record_endless/is_unlocked
- [X] T007 新建 `src/pvz_game/domain/campaign.py`（不导入 pygame）：承载关卡目录、按 ID/顺序查找、下一关、解锁规则和星级判定入口；只依赖 `config.load_campaign()` 的数据结构
- [X] T008 扩展 `tools/validate_assets.py`：在现有皮肤校验之外调用 `load_campaign()` 并校验 5 关/顺序/引用/星级字段；坏关卡必须让脚本以非零退出，从而阻止 Windows 构建

**Checkpoint**: 关卡数据、加载器和进度存储可用；US1/US2/US3 可以开始。

---

## Phase 3: User Story 1 - 被窝与嗷嗷嗷完整显示腿脚 (Priority: P1) 🎯 可玩版本的前置视觉修复

**Goal**: 从原始图片按完整轮廓重新生成被窝与嗷嗷嗷的动作帧，脚掌、腿、尾巴和耳朵在菜单、卡片、拖动预览和地图中完整可见。

**Independent Test**: 逐姿态对照源图与输出帧；运行定向边界检查；在菜单、卡片、地图、拖动和倒地姿态中确认 0 帧被平切；两套狗狗外观均检查。

### Tests for User Story 1（必要且定向）

- [X] T009 [P] [US1] 更新 `tests/integration/test_animation.py` 的 `dog_frame_bounds`：对 dogs/dogs_photo 的被窝/嗷嗷嗷断言 12 个源姿态映射、可见 bbox 距帧边界至少 8 像素、底部不超过 232、无平切/相邻姿态混入；该测试应先在当前素材上失败

### Implementation for User Story 1

- [X] T010 [P] [US1] 在 `tools/import_dog_assets.py` 增加整张图连通轮廓提取函数：alpha 阈值 96、恰好 12 个主体连通体、按包围盒中心做 4×3 排序、完整 bbox、等比缩放、脚底 232、四周至少 8 像素透明边距；只用于被窝/嗷嗷嗷及 dogs_photo 对应素材，不改写原始 PNG
- [X] T011 [US1] 使用新提取路径重新生成 `assets/skins/dogs/atlas-005.png`、`assets/skins/dogs/manifest.json`、`assets/skins/dogs/provenance.json`、`assets/sources.json`，并同步 `assets/skins/dogs_photo/` 中复用被窝/嗷嗷嗷的图集与清单；其他狗狗角色保持现有素材路径
- [X] T012 [US1] 校准 `assets/skins/dogs/manifest.json` 中相关角色的 `display_scale_multiplier`/锚点与 `src/pvz_game/presentation/animation.py` 的边界适配，确保卡片、菜单、拖动预览和地图四角完整显示，站立高度差 ≤20%、脚底基线波动 ≤2 逻辑像素
- [X] T013 [US1] 运行 `tools/import_dog_assets.py`、`tools/validate_assets.py`、`pytest tests/integration/test_animation.py -k dog_frame_bounds`，用 `tools/preview_animations.py --export docs/validation/012/animations` 生成对照图，人工检查后记录到 `docs/validation/012/dog-frames.md`

**Checkpoint**: 被窝/嗷嗷嗷在两套外观和全部展示位置完整，无脚掌/尾巴平切。

---

## Phase 4: User Story 2 - 有层次的关卡推进 (Priority: P1)

**Goal**: 玩家从关卡选择进入 5 个逐步变难的关卡，看到不同敌人组合/节奏/压力条件和波次预告；通关解锁下一关并保存本机进度，失败可完整重试。

**Independent Test**: 完成 5 关配置校验；从第 1 关实际玩到第 5 关；确认逐关解锁、失败重试、重启保留进度、损坏存档回退；确认 `day_01` 的 replay/现有测试不被破坏。

### Tests for User Story 2（必要且定向）

- [X] T014 [P] [US2] 新建 `tests/unit/test_campaign_config.py`：5 关 ID/顺序、rows=5/cols=12、波次 strength 递增、每波至少 1 个出怪、可用植物/割草机行/星级目标校验；断言缺省字段仍让 `config.load()` 返回可玩的 day_01
- [X] T015 [P] [US2] 新建 `tests/unit/test_campaign_progress.py`：首次只解锁 day_01、通关解锁下一关、失败不解锁、最佳星级/时间只增不减、损坏/缺失 `progress.json` 回退默认且不崩溃；路径使用临时目录，不写真实用户目录

### Implementation for User Story 2

- [X] T016 [US2] 扩展 `src/pvz_game/domain/simulation.py`：从 level 读取初始阳光、天空阳光间隔、割草机行、可用植物和模式；新增 `wave_preview()` 只读方法；保持 `snapshot()` 与事件 schema 完全不变
- [X] T017 [US2] 扩展 `src/pvz_game/domain/systems.py` 与 `src/pvz_game/domain/simulation.py` 的命令校验：使用 level 的天空阳光间隔；未启用行初始化为 spent 割草机；拒绝不在 `available_plants` 中的植物并返回明确原因
- [X] T018 [P] [US2] 在 `src/pvz_game/presentation/scenes.py` 增加关卡选择卡片、无尽入口占位、结算页“下一关/重试/返回菜单”按钮的几何常量和 `MESSAGES` 中的不可用植物提示；保持现有 `BUTTONS` 键和坐标不变
- [X] T019 [P] [US2] 扩展 `src/pvz_game/presentation/input.py`，增加关卡选择点击、已解锁/锁定判断、可用植物过滤、下一关/重试操作；新参数全部带默认值，旧 `click(...)`/`visible_plant_cards(...)` 调用保持兼容
- [X] T020 [P] [US2] 扩展 `src/pvz_game/presentation/renderer.py`：绘制关卡选择页、当前关卡名称/压力条件、下一波预告和结果页下一关入口；不得改变现有菜单、HUD 和基准调用的默认行为
- [X] T021 [US2] 扩展 `src/pvz_game/app.py`：启动时 `load_campaign()` + 加载进度；主菜单“开始游戏”进入关卡选择；实现 `start_level(level_id)`、下一关、重试、返回菜单、通关保存、失败不推进、损坏进度提示；保留 `--smoke-frames`/`--smoke-play`/外观菜单
- [X] T022 [US2] 新建 `tests/integration/test_campaign_flow.py`：用临时进度文件验证开局只解锁 day_01、通关 day_01 后 day_02 解锁、失败/重试不推进、重启后进度保留；不启动真实窗口
- [X] T023 [US2] 运行 `pytest tests/unit/test_campaign_config.py tests/unit/test_campaign_progress.py tests/integration/test_campaign_flow.py` 与 `tools/validate_assets.py`；实际从第 1 关玩到第 5 关，检查解锁、波次预告、失败重试和重启保存，记录到 `docs/validation/012/campaign.md`

**Checkpoint**: 5 关可完整游玩，关卡选择/解锁/保存/重试正确，旧 day_01 行为保持不变。

---

## Phase 5: User Story 3 - 狗狗动作、阳光与子弹流畅呈现 (Priority: P1)

**Goal**: 狗狗待机/行走/攻击、阳光出现/浮动/收集、子弹飞行/命中呈现连续运动与同步反馈，同时保持 60Hz 模拟和现有数值不变。

**Independent Test**: 狗狗外观下录 10 秒标准对局，检查无 >50ms 静止、无重影、阳光收集同帧、子弹无跳变/命中特效对齐；暂停 2 秒恢复；运行一次标准场景基准和现有 replay/skin invariance。

### Implementation for User Story 3

- [X] T024 [P] [US3] 在 `src/pvz_game/presentation/animation.py` 增加确定性的次级动作（呼吸/行走起伏、轻微摆动、攻击后坐、受击回弹）和 ≤6 tick 的位置/缩放缓动；幅度按 `presentation-smoothing.md`（垂直 ≤3px、水平 ≤2px、缩放 0.98–1.02）；禁止整帧 alpha 双姿态混合
- [X] T025 [US3] 在 `src/pvz_game/presentation/renderer.py` 为阳光增加淡入/淡出和呼吸光晕；收集事件同帧移除阳光、更新余额并播放收集光效；视觉中心与 `sun_radius` 点击区域保持一致
- [X] T026 [US3] 在 `src/pvz_game/presentation/renderer.py` 为子弹增加最多 3 点短尾迹、`shot` 事件枪口闪光和投射物消失位置的命中特效；不新增模拟事件，不修改快照；特效/尾迹每类上限 64 个，重开/返回菜单时清空
- [ ] T027 [US3] 检查暂停/失焦冻结和 `Renderer.draw` 默认参数兼容；录 10 秒狗狗外观对局逐帧检查，运行 `pytest tests/replay/test_base_replay.py tests/integration/test_skin_invariance.py -q` 与 `tools/benchmark.py --window --scene standard --seconds 60 --output docs/validation/012/benchmark.json`，记录到 `docs/validation/012/smoothness.md`

**Checkpoint**: 狗狗/阳光/子弹表现连续，暂停正确，玩法结果与现有基线一致。

---

## Phase 6: User Story 4 - 重复挑战的星级目标 (Priority: P2)

**Goal**: 每关至少 2 个星级目标，通关时结算、显示并保存历史最佳；星级不阻塞解锁。

**Independent Test**: 以全部达成/部分达成/未达成三种情况通关同一关，核对授予与显示；重玩较低成绩不覆盖最佳；重启后保留；星级不改变解锁。

### Tests for User Story 4（必要且定向）

- [X] T028 [P] [US4] 扩展 `tests/unit/test_campaign_progress.py`：覆盖三种星级判定（mowers_used_at_most、clear_within_ticks、sun_collected_at_least）、只在胜利时授予、最佳星级取最大、低分不覆盖、星级不影响 unlocked

### Implementation for User Story 4

- [X] T029 [US4] 在 `src/pvz_game/domain/campaign.py` 实现 `evaluate_stars(level, stats)`；在 `src/pvz_game/domain/simulation.py` 增加 `run_stats()` 并在 `src/pvz_game/domain/systems.py` 统计阳光收集、割草机使用、植物损失和 elapsed_ticks；统计不写入 snapshot、不新增事件
- [X] T030 [US4] 在 `src/pvz_game/progress.py` 保存每关 `best_stars`/`best_ticks`；在 `src/pvz_game/app.py` 的胜利路径调用星级判定并写入进度，失败不解锁/不授予星级
- [X] T031 [US4] 在 `src/pvz_game/presentation/renderer.py` 与 `src/pvz_game/presentation/scenes.py` 显示关卡选择页星级、结算页目标达成情况和获得星数；保持“下一关/重试/返回”流程
- [X] T032 [US4] 运行 `pytest tests/unit/test_campaign_progress.py -q` 并实际重玩一关验证星级显示/最佳保留，记录到 `docs/validation/012/stars.md`

**Checkpoint**: 星级目标可达成、可显示、可保存，且不影响关卡解锁。

---

## Phase 7: User Story 5 - 通关后的无尽挑战 (Priority: P2)

**Goal**: 通关第 5 关后解锁无尽模式；敌人持续增强直到防线突破，失败后显示并保存本次/最佳波数与击杀。

**Independent Test**: 未通关时无尽入口锁定；通关后进入并推进至少 10 波，确认没有“清空即胜利”、同屏上限生效、失败结算与记录保存；重启保留。

### Tests for User Story 5（必要且定向）

- [X] T033 [P] [US5] 新建 `tests/unit/test_endless.py`：导演始终保留至少 2 个未来波次、数量/类型比例随波数提升、同屏僵尸不超过上限、无尽模式不触发 won、失败可结算、记录可保存

### Implementation for User Story 5

- [X] T034 [US5] 新建 `src/pvz_game/domain/endless.py`：实现确定性 `EndlessDirector`，从 `campaign.json` 读取生成参数，按波数增加数量、快速/高耐久比例并缩短间隔，限制同屏僵尸；在 `src/pvz_game/domain/simulation.py` 的 `step` 中驱动导演，并在 `mode=="endless"` 时跳过胜利判定
- [X] T035 [US5] 在 `src/pvz_game/app.py`、`src/pvz_game/progress.py`、`src/pvz_game/presentation/scenes.py`、`src/pvz_game/presentation/renderer.py` 接入无尽入口/锁定条件/结算页/最佳波数保存；只使用现有植物/僵尸/数值，不新增角色
- [ ] T036 [US5] 运行 `pytest tests/unit/test_endless.py -q`；通关第 5 关后实际进入无尽推进 10 波并失败，检查结算与重启记录，记录到 `docs/validation/012/endless.md`

**Checkpoint**: 无尽模式可解锁、可失败结算、可记录，不影响 5 关战役。

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 文档、回归、Windows 构建和最终最小验收。

- [X] T037 [P] 更新 `README.md`、`docs/development.md` 和游戏内帮助文本，说明 5 关战役、星级、无尽、进度保存位置和新的验证命令；版本号与发行说明保持同步
- [X] T038 新增 `docs/validation/012/release.md`，汇总狗狗帧、关卡/进度、星级、无尽、流畅度和基准的实际结果、未执行项与已知限制
- [ ] T039 运行必要的回归：`pytest tests/unit/test_campaign_config.py tests/unit/test_campaign_progress.py tests/unit/test_endless.py -q`、`pytest tests/integration/test_animation.py -k dog_frame_bounds -q`、`pytest tests/replay/test_base_replay.py tests/integration/test_skin_invariance.py -q`；修复回归，不跑全量 pytest
- [X] T040 运行 `packaging/windows/build.ps1 -ArtifactName PvzMiniGame-v0.7.0`，启动 `dist/windows/PvzMiniGame-v0.7.0/PvzMiniGame.exe`，完成一次关卡选择→第 1 关胜利→返回菜单流程，确认新增关卡 JSON 随包且离线可用
- [ ] T041 按 `quickstart.md` 执行最终最小验收：狗狗对照、5 关解锁/保存、损坏存档回退、无尽 10 波、10 秒流畅观察、标准基准和 Windows 包启动；只在 `docs/validation/012/release.md` 勾选实际通过的项

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001–T004 无依赖，可并行开始。
- **Foundational (Phase 2)**: 依赖 Phase 1；T005/T006 可并行，T007/T008 依赖 T005。完成前不开始用户故事实现。
- **US1 (Phase 3)**: 依赖 Foundational；只改素材/导入工具/动画测试，可与 US2 并行。
- **US2 (Phase 4)**: 依赖 Foundational；改 simulation/systems/app/renderer，是 US3/US4/US5 的基础。
- **US3 (Phase 5)**: 依赖 US2 的 T020（renderer）和 T021（app）；顺延执行，避免与 US2 同文件冲突。
- **US4 (Phase 6)**: 依赖 US2 的关卡/进度/渲染；与 US5 共享 app/renderer/progress，按 US4→US5 顺序执行。
- **US5 (Phase 7)**: 依赖 US2 的关卡/进度/渲染和 US4 的进度结构；在 US4 后执行。
- **Polish (Phase 8)**: 依赖所需用户故事完成；T037 可与 T038–T041 交错，T039–T041 顺序执行。

### User Story Dependencies

- **US1 (P1)**: 可独立交付视觉修复；不依赖 US2/US3。
- **US2 (P1)**: 依赖 Foundational；不依赖 US1，但两者都改 presentation/素材，建议先完成 US2 的数据/渲染骨架再合入 US1 的素材。
- **US3 (P1)**: 依赖 US2 的 renderer/app；不依赖 US1。
- **US4 (P2)**: 依赖 US2；不依赖 US3/US5。
- **US5 (P2)**: 依赖 US2；与 US4 共享 app/renderer/progress，不能安全并行。

### Within Each User Story

- 先写定向测试（US1/US2/US4/US5），确认在当前代码上失败，再实现。
- Setup/数据 → 域层规则 → 表现层 UI → app 接线 → 最小验证。
- 同一文件的连续任务（renderer/app）按 ID 顺序执行，不要并行编辑。

### Parallel Opportunities

- Setup T001–T004 可在不同文件并行。
- Foundational T005/T006 可并行；T007/T008 在 T005 后执行。
- US1 T009/T010 可并行编写（测试文件 vs 导入工具），T011 依赖 T010。
- US2 T014/T015 可并行；T018 可与 T016 并行；T019/T020 在 T016/T018 后可按文件并行。
- US4 T028 测试可与 T029 域层实现并行编写。
- US5 T033 测试可与 T034 域层实现并行编写。

---

## Parallel Example: US1

```text
Task: "T009 [P] [US1] 更新 tests/integration/test_animation.py 的完整轮廓断言"
Task: "T010 [P] [US1] 在 tools/import_dog_assets.py 增加整张图连通轮廓提取"
```

## Parallel Example: US2

```text
Task: "T014 [P] [US2] 新建 tests/unit/test_campaign_config.py"
Task: "T015 [P] [US2] 新建 tests/unit/test_campaign_progress.py"
Task: "T018 [P] [US2] 在 src/pvz_game/presentation/scenes.py 增加关卡选择/结果按钮"
```

## Parallel Example: US3

```text
Task: "T024 [P] [US3] 在 src/pvz_game/presentation/animation.py 增加次级动作"
Task: "T025 [US3] 在 src/pvz_game/presentation/renderer.py 增加阳光淡入/光晕"
```

## Parallel Example: US4

```text
Task: "T028 [P] [US4] 扩展 tests/unit/test_campaign_progress.py 的星级用例"
Task: "T029 [US4] 在 src/pvz_game/domain/campaign.py 实现 evaluate_stars"
```

## Parallel Example: US5

```text
Task: "T033 [P] [US5] 新建 tests/unit/test_endless.py"
Task: "T034 [US5] 新建 src/pvz_game/domain/endless.py 的 EndlessDirector"
```

---

## Implementation Strategy

### 可玩版本优先（Milestone A）

1. 完成 Phase 1–2（共享数据/加载/进度）。
2. 完成 US1（狗狗完整轮廓）与 US2（5 关、关卡选择、保存、波次预告）。
3. 完成 US3（狗狗/阳光/子弹流畅表现）。
4. 运行 US1/US2/US3 的定向测试和一次完整试玩；达到“可完整游玩、可重开、可保存”的 Milestone A 后再进入 P2。

### P2 增强

1. US4 星级目标（在 US2 的关卡/进度结构上追加）。
2. US5 无尽模式（在 US2/US4 的 app/进度/渲染上追加）。
3. Polish 回归、Windows 构建和最终最小验收。

### MVP 范围

- **可玩 MVP**：US1 + US2 + US3（Milestone A）。
- 若只能先交付一个故事，US1 可先独立交付视觉修复，但不构成“可玩版本”的完整增量。
- 不把全量 pytest、外观矩阵、长时压力或安卓流程作为本轮完成条件。

---

## Notes

- 任务中的 `[P]` 仅表示不同文件、无未完成依赖，可以并行；同一 `renderer.py`/`app.py` 的任务不要并行。
- 所有新字段、参数和接口必须保持现有 `load()`、`snapshot()`、事件序列和默认调用兼容。
- 测试只覆盖新增风险；验证必须记录实际结果，未执行或失败项不得标为通过。
- 每个 Checkpoint 后运行对应定向检查，不要等到最后才验证。