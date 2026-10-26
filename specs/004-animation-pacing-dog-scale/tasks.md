# Tasks: 动画节奏与小狗显示尺寸调整

**Input**: Design documents from specs/004-animation-pacing-dog-scale/

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/animation-presentation.md

**Tests**: 本Feature规格为每个用户故事定义了可重复独立测试；任务包含针对行为验收的现有集成/回放测试更新。

**Organization**: 任务按spec.md中的US1、US2、US3组织。实现沿用Python 3.12、pygame-ce和当前domain/presentation分层。

## Format: [ID] [P?] [Story] Description

- [P]表示文件与依赖允许并行。
- 用户故事任务使用[US1]、[US2]、[US3]标记。
- 每条任务均包含要修改/生成的具体文件路径；验证任务也写明记录文件路径。

## Phase 1: Setup

**Purpose**: 固化改动前的可比较基线；项目和依赖已存在，不重复初始化。

- [X] T001 在实现改动前记录default/dogs各必需clip的RGBA唯一姿势数、总duration_ticks、姿势速率、小宝/小杜可见高度，以及固定关卡确定性输入的模拟事件/tick、位置、伤害、阳光、击杀和胜负基准到 docs/validation/animations/004-baseline.md 与 tests/replay/fixtures/004-baseline.json

## Phase 2: Foundational

**Purpose**: 为姿势播放和角色缩放提供唯一的presentation配置入口，阻止各故事重复定义显示参数。

- [X] T002 在 src/pvz_game/presentation/animation.py 定义允许的姿势速率范围、按tick_hz分配clip帧duration_ticks的共享接口和读取manifest角色倍率的统一接口；姿势速率从 assets/config/balance.json 的 tick_hz 读取频率，不另存60Hz副本；不得在Python代码中存储小宝/小杜倍率值，缺省字段读作1.0且不改domain状态

**Checkpoint**: 共享显示参数入口明确后再开始US1-US3；无需改Simulation或domain规则。

## Phase 3: User Story 1 - 让植物和僵尸动作节奏自然 (Priority: P1) MVP

**Goal**: default与dogs的所有循环/一次性动作以12–18个可辨认姿势/秒展示，hit clip能够播放，游戏规则时序与皮肤无关。

**Independent Test**: 对两种皮肤全部REQUIRED clip按RGBA逐像素去重后计算姿势数×balance.json.tick_hz/总tick，均处于12–18并通过接触表动作有效性复核；暂停恢复动作连续；同一输入回放的模拟trace与T001保存的改前基准一致。

### Tests for User Story 1

- [X] T003 [P] [US1] 在 tests/integration/test_animation.py 将旧的至少24姿势/秒断言改为RGBA逐像素唯一姿势率12–18，并覆盖所有循环/一次性clip、hit事件播放、暂停tick冻结及动作结束回归
- [X] T004 [P] [US1] 在 tests/replay/test_base_replay.py 和 tests/replay/test_skin_invariance.py 加载 tests/replay/fixtures/004-baseline.json，比对相同固定关卡输入下事件及tick、位置/推进、攻击/伤害、阳光、击杀和胜负，并继续验证default/dogs一致

### Implementation for User Story 1

- [X] T005 [P] [US1] 在 tools/validate_assets.py 从 assets/config/balance.json 读取tick_hz并使用RGBA逐像素去重姿势率验证两套皮肤所有REQUIRED clip均为12–18姿势/秒，同时保留循环周期、锚点和不重叠检查
- [X] T006 [P] [US1] 在 tools/import_classic_assets.py 从 assets/config/balance.json 读取tick_hz并按12–18姿势/秒生成default动作帧duration_ticks，重新生成 assets/skins/default/manifest.json，保留帧序和所有既有动作
- [X] T007 [P] [US1] 在 tools/import_dog_assets.py 从 assets/config/balance.json 读取tick_hz并按12–18姿势/秒生成dogs动作帧duration_ticks，重新生成 assets/skins/dogs/manifest.json，并保留可追溯源帧顺序
- [X] T008 [US1] 在 src/pvz_game/presentation/animation.py 为既有hit事件添加只存在于Animator的定时hit clip播放与回归逻辑，保持攻击/伤害/死亡规则时点不变

**Checkpoint**: 运行tests/integration/test_animation.py、tests/replay/test_skin_invariance.py及tools/validate_assets.py，确认姿势速率门槛与规则回放结果。

## Phase 4: User Story 2 - 看清小杜的整行爆炸动作 (Priority: P1)

**Goal**: 火爆辣椒清行视觉持续2.0±0.1秒，按序播放35个源姿势，整行规则只结算一次且对局持续推进。

**Independent Test**: 在tests/integration/test_jalapeno_row_clear.py中验证有效种植只产生一次清行事件，特效在约120 tick结束，暂停时不前进、session重开时不残留；运行时手动计时应为1.9–2.1秒。

### Tests for User Story 2

- [X] T009 [US2] 在 tests/integration/test_jalapeno_row_clear.py 覆盖特效目标120 tick/35源姿势完整顺序、单次清行结算、游戏规则继续推进、暂停冻结与重开清理

### Implementation for User Story 2

- [X] T010 [P] [US2] 在 tools/import_dog_assets.py 根据素材provenance选取恰好35个小杜ignite源姿势并按序写入 assets/skins/dogs/manifest.json，duration_ticks总和精确设为120且clip不含生成中间帧
- [X] T011 [US2] 在 src/pvz_game/presentation/animation.py 让Animator清行特效按35姿势clip完整播放并在clip结束后移除；不延迟Simulation的清行、波次和胜负处理
- [X] T012 [US2] 在 tests/integration/test_jalapeno_row_clear.py 与 tools/validate_assets.py 核对dogs/jalapeno/ignite恰为35个源姿势、17.5姿势/秒且120 tick，并记录结果到 docs/validation/animations/004-jalapeno.md

**Checkpoint**: 清行时长、源姿势顺序与规则结算次数均有自动验证；普通手动试玩能看到完整点燃/喷火/消退。

## Phase 5: User Story 3 - 完整显示并放大小宝和小杜 (Priority: P1)

**Goal**: 小宝与小杜在草坪、植物卡、选肤预览、拖动预览及一次性展示中至少较现状放大15%，脚底稳定且主体完整。

**Independent Test**: 在所有必需动作姿势及所有显示上下文测量可见边界；草坪高度至少+15%、锚点变化≤2逻辑像素、无UI裁切/草坪越界/相邻主体遮挡；default玩法结果不变。

### Tests for User Story 3

- [X] T013 [US3] 在 tests/integration/test_asset_manifest.py 与 tests/integration/test_animation.py 增加小宝/小杜最终角色倍率的全身边界、至少15%尺寸增幅、脚底≤2逻辑像素偏差、卡片/预览容器不裁切及相邻角色主体不重叠验证

### Implementation for User Story 3

- [X] T014 [US3] 只在 assets/skins/dogs/manifest.json 的wallnut（小宝）与jalapeno（小杜）role元数据写入display_scale_multiplier；tools/import_dog_assets.py输出相同字段，旧manifest缺省倍率按1.0兼容，Python代码不得定义副本
- [X] T015 [US3] 在 src/pvz_game/presentation/animation.py 与 src/pvz_game/presentation/renderer.py 使用共享角色倍率和同一锚点绘制路径覆盖草坪、死亡/清行、卡片、选肤预览和拖动ghost，并依据各容器边界完整fit角色
- [X] T016 [US3] 在 src/pvz_game/presentation/dog_validation.py 用最终角色倍率检查小宝/小杜所有必需姿势脚底基线、画布边界及相邻角色主体重叠

**Checkpoint**: 两只狗狗各动作在卡片/预览/草坪均完整可见，尺寸验收通过，输入同回放仍产生一致玩法结果。

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 运行综合检查，确认核心循环与发行包仍可用。

- [X] T017 [P] 运行 .venv/Scripts/python.exe -m pytest -q 和 .venv/Scripts/python.exe tools/validate_assets.py，并将命令及结果写入 docs/validation/animations/004-automated.md
- [X] T018 [P] 导出default/dogs完整动作预览并运行最坏场景基准，将预览与结果记录到 docs/validation/animations/004-preview-performance.md
- [X] T019 完成quickstart.md中核心循环、暂停/恢复、重开与default/dogs试玩步骤，并运行 tools/build.ps1、tools/verify_bundle.py 及两种皮肤发行冒烟启动；将通过/失败证据写入 docs/validation/animations/004-release.md

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001先记录旧版姿势/尺寸及确定性玩法回放基准，供SC-002和SC-004作修改前对照。
- **Foundational (Phase 2)**: T002依赖T001确定现有小狗显示基准；阻塞后续各故事。
- **US1 (Phase 3)**: T003、T004先定义行为门槛并读取T001基准；实现T005–T008随后完成。T006与T007操作独立导入器/manifest，可并行；T005不与它们共享文件，可并行。
- **US2 (Phase 4)**: 依赖US1完成统一节奏与素材导入规则；T009先于实现；T010与T011修改不同文件，可并行。
- **US3 (Phase 5)**: 依赖共同缩放入口及US2的Animator改动完成；T013先写验证，再做T014；T015依赖T014，T016依赖T015定义的最终缩放入口。
- **Polish (Phase 6)**: 依赖三故事实现；T017/T018可并行。T019须在全套自动检查及场景预览后完成发行验证。

### User Story Dependencies

- **US1 (P1)**: T002后可开始；先完成后续故事依赖的全局动作节奏和hit clip表现。
- **US2 (P1)**: 依赖US1的manifest节奏标定与Animator基础，再用35个源姿势满足特定2秒爆炸验收。
- **US3 (P1)**: 依赖共享角色缩放入口；由于同样触及Animator/Renderer，建议US2合并后顺序修改与集成。

### Parallel Opportunities

- T003与T004操作不同测试文件，可并行。
- US1实现的T005、T006、T007操作不同文件，可并行；T008需在T002后实现且避免与T002同文件并行。
- US2中的T010（dog素材导入）与T011（Animator）可并行。
- Polish中的T017与T018可并行；T019需等待两者完成。
- 同一manifest或Python模块的任务必须串行执行，避免生成覆盖或合并冲突。

## Parallel Example: User Story 1

    Task: T003 更新tests/integration/test_animation.py的12–18姿势/s和hit表现测试
    Task: T004 对比tests/replay/fixtures/004-baseline.json中的玩法回放基准

    Task: T006 重标定default importer及assets/skins/default/manifest.json
    Task: T007 重标定dog importer及assets/skins/dogs/manifest.json

## Implementation Strategy

### MVP First (User Story 1 Only)

1. 在改动前记录姿势速率、小狗尺寸和确定性玩法回放基准（T001）。
2. 建立共用presentation配置（T002）。
3. 完成US1的帧速率、hit clip与回放不变性任务（T003–T008）。
4. 停在US1 checkpoint，让用户先试玩循环动作、攻击、受击和僵尸移动；确认模拟节奏和60Hz规则保持不变。

### Incremental Delivery

1. 完成US1，验证两套皮肤全动作节奏和既有核心循环。
2. 增加US2，独立验收小杜2秒35姿势清行表现。
3. 增加US3，独立验收小宝/小杜尺寸与各显示上下文。
4. 完成综合回归、窗口试玩与发行包检查。

## Notes

- 每条任务都使用checkbox、连续ID和具体项目文件路径；[P]仅标记无文件冲突且无前置依赖的工作。
- 所有验证均围绕既有动画/资源/回放/打包结构；本Feature不修改domain规则。
- 若pose rate校验、循环最短周期与素材姿势数不可同时满足，补充/重新选择素材姿势并调整导入时长，不能放宽规格门槛或静默豁免。
