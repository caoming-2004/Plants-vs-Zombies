# Tasks: 狗狗视觉与阳光动效优化

**Input**: Design documents from `specs/009-dog-visual-polish/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 保留必要的规则、交互和发行检查；不跑无关压力套件或完整测试矩阵。

**Organization**: 按用户故事拆分，先建立基线和共享模型，再实现可独立观察的改动。

## Phase 1: Setup

**Purpose**: 记录可比较的当前状态；项目依赖和目录已经存在，不重复初始化。

- [x] T001 [P] 记录 `assets/skins/dogs/manifest.json` 与 `assets/skins/dogs_photo/manifest.json` 中当前可见 alpha 轮廓、角色高度和各自被窝基线到 `docs/validation/009/dog-visual-baseline.md`
- [x] T002 [P] 记录开始/换肤首次呈现时间、标准场景帧时间和静止阳光表现到 `docs/validation/009/performance-baseline.md`；首帧时间使用 60fps 录屏逐帧或运行时单调时钟测量并记下方法

## Phase 2: Foundational

**Purpose**: 为新植物效果和确定性阳光位置提供共享数据字段；故事实现依赖此阶段。

- [x] T003 [P] 在 `src/pvz_game/domain/models.py` 为 `Projectile`、`Zombie` 和 `SunPickup` 添加有限时减速与确定性阳光运动所需字段，遵守 `specs/009-dog-visual-polish/data-model.md` 的不变量
- [x] T004 [P] 在 `src/pvz_game/config.py` 和 `assets/config/balance.json` 支持 `potato_mine`、`snow_shooter` 角色字段；配置准备时间、触发范围/爆炸伤害、寒冰减速系数/时长和价格/冷却，所有时间以 tick 表示

**Checkpoint**: 配置加载和实体状态可表达新效果；没有新增依赖或平衡规则重复定义。

## Phase 3: User Story 1 - 完整、协调地展示狗狗 (Priority: P1)

**Goal**: 缩小被窝并让所有狗狗姿态完整、比例协调地显示。

**Independent Test**: 分别检查 `dogs` 与 `dogs_photo` 外观中实际包含的角色待机、最大伸展和趴卧姿态可见 alpha 轮廓；确认各自被窝较基线缩小约 20%，没有身体部位被画布裁切。胖宝宝与黄黄仅检查 `dogs` 外观。

- [x] T005 [US1] 在 `tests/integration/test_animation.py` 增加 `dogs` 与 `dogs_photo` 外观全部狗狗角色的可见轮廓边界验收，以及两种外观中被窝各自的相对缩放验收
- [x] T006 [US1] 在 `assets/skins/dogs/manifest.json` 和 `assets/skins/dogs_photo/manifest.json` 分别调整已有狗狗角色显示缩放；两种外观的被窝各自缩小约 20%，同一外观内狗狗可见高度差异控制在约 20%；新植物仍只在 `dogs` 中出现
- [x] T007 [US1] 在 `src/pvz_game/presentation/dog_validation.py` 和 `src/pvz_game/presentation/animation.py` 按 `dogs` 与 `dogs_photo` 中各动作帧的可见轮廓校准锚点与显示边界，不裁切或拉伸身体
- [x] T008 [US1] 在 `src/pvz_game/presentation/renderer.py` 调整地图角色绘制位置，令两种狗狗外观中实际出现角色的头、躯干、尾巴和四肢完整留在窗口及地图可见区域；保存两种外观并排核对图到 `docs/validation/009/dog-visual-check.png`
- [x] T009 [US1] 运行 `tests/integration/test_animation.py` 与 `tools/validate_assets.py`，将姿态覆盖、完整轮廓和尺寸结果记录到 `docs/validation/009/dog-visual-check.md`

**Checkpoint**: 经典/狗狗/狗狗照片皮肤仍能显示；狗狗姿态完整，被窝明显缩小。

## Phase 4: User Story 2 - 使用土豆雷和寒冰射手狗狗角色 (Priority: P1)

**Goal**: 胖宝宝成为可准备、触发的一次性土豆雷；黄黄成为造成伤害并减速的寒冰射手。坚果墙和豌豆射手保持不变。

**Independent Test**: 仅运行新植物规则检查，覆盖土豆雷准备期间受啃食、准备完触发和一次性范围伤害，以及黄黄命中伤害、有限时减速、重复命中刷新、到期恢复。

- [x] T010 [US2] 在 `tests/unit/test_new_plant_rules.py` 添加土豆雷准备/受啃食/单次爆炸与寒冰射手伤害/减速/刷新/恢复的定向规则检查
- [x] T011 [US2] 在 `src/pvz_game/domain/systems.py` 实现土豆雷准备计时、准备完成提示、接触触发、同车道近距伤害和一次性移除；准备期间保留现有僵尸啃食路径
- [x] T012 [US2] 在 `src/pvz_game/domain/systems.py` 实现寒冰射手投射物命中时的伤害和有限时减速，刷新时长但不累计减速强度，到期恢复移速和啃食频率
- [x] T013 [US2] 在 `src/pvz_game/presentation/renderer.py` 与 `src/pvz_game/presentation/animation.py` 为胖宝宝准备/触发状态及黄黄冰豌豆、减速状态增加清晰表现；卡片明确标识土豆雷与寒冰射手职责
- [x] T014 [US2] 运行 `tests/unit/test_new_plant_rules.py` 和 `tests/integration/test_drag_input.py`，确认狗狗外观新卡可种植、经典坚果墙和豌豆射手及种植拒绝路径未回归，并记录到 `docs/validation/009/new-plant-check.md`

**Checkpoint**: 两个新角色具有不同于坚果墙/豌豆射手的原版职责，并可在狗狗外观实际游玩。

## Phase 5: User Story 3 - 感受自然、顺滑的阳光动效 (Priority: P1)

**Goal**: 天空掉落和植物产出的阳光平滑进入草坪、轻柔浮动且位置可准确点击。

**Independent Test**: 观察两类阳光从出现到落地、收集/过期；检查移动时点击、暂停和余额只结算一次。

- [x] T015 [US3] 在 `tests/integration/test_playable_loop.py` 增加阳光行进位置命中、暂停冻结、过期和单次余额结算检查
- [x] T016 [US3] 在 `src/pvz_game/domain/simulation.py` 与 `src/pvz_game/domain/systems.py` 为天空/植物两种来源创建确定性落点轨迹并更新阳光可收集位置，保留原值、生成间隔及基于创建 tick 的寿命
- [x] T017 [US3] 在 `src/pvz_game/presentation/renderer.py` 绘制平滑下落、落地轻浮和收集反馈，并令 `src/pvz_game/presentation/input.py` 使用同一 snapshot 位置进行点击命中
- [x] T018 [US3] 运行阳光交互检查及必要的 `tests/integration/test_playable_loop.py` 用例，确认暂停/到期/收集经济规则不变；记录动效观察到 `docs/validation/009/sun-motion-check.md`

**Checkpoint**: 阳光视觉位置与点击位置一致，且游戏资源时序不变。

## Phase 6: User Story 4 - 更快进入可玩画面并保持流畅 (Priority: P2)

**Goal**: 点击开始和换肤后迅速显示目标界面，常规场景没有明显长帧卡顿。

**Independent Test**: 重复 10 次开始/换肤，用 60fps 录屏逐帧或运行时单调时钟测量从点击到首个目标画面的耗时；标准窗口运行 10 秒并查看帧间隔分布。

- [x] T019 [US4] 根据 `docs/validation/009/performance-baseline.md` 定位首次界面绘制阻塞；仅在超过 500 ms 或存在明显卡顿时，调整 `src/pvz_game/app.py`、`src/pvz_game/presentation/scenes.py` 或 `src/pvz_game/presentation/skin_catalog.py` 中经测量确认的同步加载路径
- [x] T020 [US4] 运行 `tools/benchmark.py` 10 秒标准窗口 benchmark；用带帧时间戳的 60fps 录屏或运行时单调时钟逐次记录 10 次开始/换肤的点击与首个目标画面时间，将原始结果与方法记录到 `docs/validation/009/performance-check.md`

**Checkpoint**: 界面和常规对局达到规格时间门槛；若基线已满足，则记录测量依据而不添加无收益的重构。

## Phase 7: Polish & Playable Release

**Purpose**: 只跑必要全流程回归，生成正式可玩包并清理测试产物。

- [x] T021 确认 `tests/replay/test_base_replay.py` 的可赢关卡/重开用例通过一次，构建并 smoke 启动正式包，保存简短验收报告到 `docs/validation/009/release-report.md`
- [x] T022 清除本轮产生的 staging 测试 EXE 与 ZIP，保留正式可玩包及验收证据，并在 `docs/validation/009/release-report.md` 记录清理结果

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): 无代码依赖；T001 与 T002 可并行采集不同基线。
- Foundational (Phase 2): 依赖 setup；T003 与 T004 修改不同文件，可并行。
- User Stories (Phases 3–6): 均依赖基础字段/配置。US1、US2、US3 的规则边界各自清晰，但它们共享 renderer 或 domain systems 的后续整合宜在同一工作树按序完成；推荐 US1 → US2 → US3。
- US4: 首帧优化依赖先完成视觉/角色/阳光后重新测量；若门槛已满足则保留实测记录。
- Polish (Phase 7): 依赖预期纳入版本的故事完成。

### User Story Dependencies

- **US1 (P1)**: 依赖基础阶段；可独立交付狗狗完整显示与被窝缩小。
- **US2 (P1)**: 依赖基础阶段；不依赖 US1 的视觉调整，卡片规则和素材绘制需顺序合并以避免修改同一 renderer 文件冲突。
- **US3 (P1)**: 依赖基础实体字段；与 US2 共用 `systems.py`，推荐在 US2 后实现。
- **US4 (P2)**: 依赖各主要故事结束后的窗口基准。

## Parallel Opportunities

- T001 与 T002 可并行：分别记录狗狗轮廓和性能/切换基线。
- T003 与 T004 可并行：模型字段和配置校验位于独立文件。
- 完成共享基础后，不建议在同一工作树并行编辑 US1–US3：它们会触及共同的 `renderer.py`、`animation.py` 或 `systems.py`。规则检查编写可以先于对应实现完成。

## Parallel Example: Setup and Foundational

```text
Task: T001 记录狗狗 alpha 轮廓与被窝缩放基线
Task: T002 记录开始/换肤耗时和 10 秒窗口性能基线

Task: T003 扩展运行实体字段
Task: T004 扩展 plant profile 配置和校验
```

## Implementation Strategy

### MVP First

先完成 Phase 1–2，再实现 US1 并独立检查完整狗狗画面。该步提供可演示的视觉修复；可玩版本的最终验收仍需完成其余两个 P1 故事（新植物和阳光动效）。

### Incremental Delivery

1. US1：狗狗完整显示、被窝缩小。
2. US2：加入土豆雷和寒冰射手职责，不改变已有经典植物。
3. US3：加入可点击位置同步的阳光动画。
4. US4：按数据修复首次切换阻塞并测量帧时间。
5. 运行一次必要完整流程与发行 smoke，清理临时测试 EXE/ZIP。

## Notes

- 每个任务均含 checkbox、顺序 ID 和明确文件路径；用户故事任务带有对应 `[USn]`。
- 本次验收不要求跑全量 pytest、压力矩阵或额外生成 ZIP。
- 临时测试 EXE 与 ZIP 仅清理由本轮生成的文件；正式可玩包保留。
