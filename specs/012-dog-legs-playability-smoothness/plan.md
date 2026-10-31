# Implementation Plan: 完整狗狗形象、五关战役与流畅表现

**Branch**: `012-dog-legs-playability-smoothness` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/012-dog-legs-playability-smoothness/spec.md`

## Summary

在现有 Python/pygame-ce 桌面游戏架构上增量实现，不引入第二套引擎、不新增玩法框架。优先级按“先可玩”排列：先修复被窝与嗷嗷嗷的完整轮廓素材，复用现有 `Simulation`、`systems`、`Animator` 和 JSON 配置完成 5 关战役、关卡选择、本机进度保存和流畅表现；随后在同一套结构上追加星级目标与无尽模式。

本轮只做 Windows 桌面版验收，测试只保留与新规则、素材和关键表现直接相关的定向检查；不使用全量矩阵、长时间压力测试或安卓验收。目标是在尽量少的改动和验证成本下，尽快得到一个可完整游玩、可重开、可保存进度的版本。

## Technical Context

**Language/Version**: Python 3.12.15（项目现有版本；不升级运行时）

**Primary Dependencies**: pygame-ce 2.5.8；Windows 打包沿用 PyInstaller 6.x；不新增第三方依赖

**Storage**: 共用 `assets/config/balance.json`、`assets/levels/*.json`；玩家进度写入本机 `%LOCALAPPDATA%\PvzMiniGame\progress.json`，不使用数据库或网络

**Testing**: pytest 8 的定向用例、`tools/validate_assets.py`、`tools/preview_animations.py`、一次完整试玩和一次标准场景基准；不跑全量矩阵

**Target Platform**: Windows x64 桌面版；安卓不在本轮交付与验收范围

**Project Type**: 单机离线桌面游戏（单一 Python 包）

**Performance Goals**: 标准场景平均不低于 58 帧/秒、95% 帧间隔不超过 18 毫秒；新增无尽模式和表现特效不得改变既有玩法节奏

**Constraints**: 离线运行；1050×600 逻辑画布、5 行 12 列；现有狗狗、植物、僵尸角色和数值仍是唯一权威；原始狗狗图片保持不变；不新增植物/僵尸角色；不重写核心循环；验证成本必须与新功能风险匹配

**Scale/Scope**: 5 个战役关卡 + 1 个无尽模式；现有 6 种植物职责与 3 种僵尸类型；单机、单玩家、单窗口；Windows 验收

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原则 | 状态 | 计划依据 |
|---|---|---|
| I. 完整可玩的核心循环优先 | PASS | Milestone A 先交付 5 关战役、关卡选择、进度保存和现有战斗循环，确保可进入、可种植、可胜负、可重开；星级与无尽在可玩版本之后追加。 |
| II. 游戏规则与界面渲染分离 | PASS | 关卡数据、胜负、冷却、伤害和星级判定仍在域层；表现层只读取快照并做程序化动效；进度保存独立于模拟状态。 |
| III. 关键数值集中管理 | PASS | 关卡初始阳光、天空阳光间隔、可用植物、割草机行、星级阈值和无尽生成参数进入 `assets/levels/campaign.json` 及关卡 JSON；价格/伤害/冷却继续引用 `balance.json`。 |
| IV. 核心玩法修改必须验证 | PASS | 只新增/修改关卡、解锁、星级、无尽和素材边界的定向用例，另加一次完整试玩和一次基准；验证方法与预期写入 quickstart 和验证记录。 |
| V. 新增功能保持已有功能可运行 | PASS | 保留 `load()` 的 day_01 行为、现有两套狗狗外观、暂停/重开/菜单和现有测试；最后做一轮回归试玩与 Windows 包启动。 |
| 开发约束：复用结构、职责和数值边界 | PASS | 复用 `Simulation`、`systems`、`renderer`、`animation`、`skin_catalog` 和 JSON 资源；新增模块只承担关卡、进度、无尽和表现扩展，不引入第二游戏框架。 |

**Pre-Phase 0 Gate**: PASS。无宪章冲突或需要豁免的复杂抽象。

## Project Structure

### Documentation (this feature)

```text
specs/012-dog-legs-playability-smoothness/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── dog-frame-assets.md
│   ├── campaign-and-progress.md
│   └── presentation-smoothing.md
├── checklists/
│   └── requirements.md
└── tasks.md                         # 后续由 $speckit-tasks 创建
```

### Source Code (repository root)

```text
assets/
├── config/balance.json               # 现有数值；不改既有角色数值
└── levels/
    ├── campaign.json                 # 关卡顺序、无尽配置、解锁规则
    ├── day_01.json                   # 现有首关，扩展关卡字段
    ├── day_02.json
    ├── day_03.json
    ├── day_04.json
    └── day_05.json

src/pvz_game/
├── app.py                            # 主菜单/关卡选择/结果页状态；启动与保存流程
├── config.py                         # balance + campaign/level 校验；保留 load()
├── resources.py                      # 本机用户数据目录定位
├── progress.py                       # 新增：进度读写、原子保存、损坏回退
├── domain/
│   ├── campaign.py                   # 新增：关卡目录、星级判定、解锁规则
│   ├── endless.py                    # 新增：无尽波次生成与并发上限
│   ├── simulation.py                 # 关卡字段、统计、无尽模式、下一波预告
│   ├── systems.py                    # 天空阳光间隔、无尽不触发胜利
│   └── models.py                     # 必要的运行统计数据结构
└── presentation/
    ├── animation.py                  # 程序化次级动作、状态过渡
    ├── renderer.py                   # 关卡 HUD、波次预告、阳光/子弹/命中特效
    ├── scenes.py                     # 关卡选择、无尽入口、结果页按钮
    ├── input.py                      # 关卡选择点击、可用植物过滤
    └── skin_catalog.py               # 现有外观加载，不改规则

tools/import_dog_assets.py            # 完整轮廓提取；更新 atlas/manifest/provenance
tests/
├── unit/
│   ├── test_campaign_config.py       # 关卡/战役配置与数值边界
│   ├── test_campaign_progress.py     # 解锁、星级、保存、损坏回退
│   └── test_endless.py               # 无尽生成、失败、记录
└── integration/
    ├── test_animation.py             # 现有动画用例 + 狗狗完整轮廓定向检查
    └── test_campaign_flow.py         # 关卡选择/通关/重开的轻量流程
```

**Structure Decision**: 继续使用单项目结构。玩法状态留在 `domain`，表现留在 `presentation`，保存只通过 `progress.py` 读写；不为关卡/无尽另建独立工程。新增 JSON 与代码模块都从现有加载器、模拟器和渲染器接入，避免复制规则。

## Design Artifacts

- [research.md](research.md)：架构、狗狗轮廓、关卡/进度/无尽、表现流畅化和最小验证决策。
- [data-model.md](data-model.md)：关卡/战役、星级、进度、无尽、动作帧和表现状态的数据结构与不变量。
- [contracts/dog-frame-assets.md](contracts/dog-frame-assets.md)：完整轮廓提取与可见性契约。
- [contracts/campaign-and-progress.md](contracts/campaign-and-progress.md)：关卡/进度/无尽/UI 流程契约。
- [contracts/presentation-smoothing.md](contracts/presentation-smoothing.md)：表现层流畅化与不改规则契约。
- [quickstart.md](quickstart.md)：最小验证命令、试玩流程和 Windows 构建。

## Design Decisions

1. **狗狗完整轮廓提取**：在 `tools/import_dog_assets.py` 增加“整张图连通轮廓”提取路径，只用于被窝和嗷嗷嗷：以 96 alpha 阈值取 12 个连通体，按包围盒中心分成 4×3 顺序，取每个姿态的完整边界，缩放并放入 256×256 帧，四周至少保留 8 像素透明边距，脚底基线固定在 232。原始图片不改写；更新 dogs atlas、manifest、provenance，并同步 dogs_photo 中被窝/嗷嗷嗷的复用素材。其他狗狗角色继续走现有导入路径，避免无关重绘。理由：脚掌被切是等分格线与实际轮廓不一致造成的，扩大格线余量无法可靠覆盖所有姿态。
2. **关卡数据驱动**：新增 `assets/levels/campaign.json` 作为战役清单与无尽配置，`day_01`～`day_05` 各自保存波次、可用植物、初始阳光、天空阳光间隔、割草机行和星级目标。`config.load()` 保持返回 day_01 的旧行为，新增 `load_campaign()` 校验全部关卡；`Simulation` 继续接收单个 level，不把战役/菜单状态塞进模拟器。
3. **战役流程与进度**：`presentation` 只负责关卡选择、结算和星级展示；`domain.campaign` 负责“通关解锁下一关”“星级取历史最佳”“无尽解锁”等规则；`progress.py` 负责本机 JSON 的加载、原子保存和损坏回退。进度只存已解锁关卡、每关最佳星级/时间、无尽最佳波数与击杀，不保存外观选择。
4. **无尽模式**：新增 `domain.endless.EndlessDirector`，在无尽关卡中按确定性公式追加波次和出怪，逐步增加数量、快速/高耐久比例并缩短间隔，同时限制同屏僵尸数；`Simulation` 在无尽模式中跳过“清空即胜利”，只保留防线突破失败。导演由 `Simulation.step` 统一驱动，保证测试和实际运行使用同一逻辑。
5. **表现流畅化**：不提高源姿态数量，也不改 60Hz 模拟；在表现层给狗狗增加程序化的呼吸/行走起伏、攻击后坐和受击回弹，使每个显示帧都有可见变化；状态切换用短促的位置/缩放缓动，不使用整帧 alpha 混合，避免双姿态重影。阳光增加淡入淡出与呼吸光晕；子弹增加短尾迹、枪口闪光和命中特效；所有特效只读取快照和事件，暂停时随模拟 tick 冻结。
6. **关卡界面**：主菜单的“开始游戏”进入关卡选择；关卡卡片显示锁/解锁、星级和无尽入口；结算页显示星级和“下一关/重试/返回”操作。沿用现有 `button`、`rounded`、`text` 与 `BUTTONS` 风格，不引入新 UI 框架。
7. **最小验证**：只增加直接覆盖新规则的定向用例和一次完整试玩；狗狗帧用一次定向边界检查和人工对照，流畅度用一次 10 秒观察加标准基准，不做全量 pytest、长时压力、六套外观矩阵或安卓复测。
8. **兼容性**：保留现有 `load()`、`Command`、`Simulation` 构造和两套狗狗外观；现有 replay fixture 与 day_01 基线继续可运行。新增关卡字段提供默认值，旧调用和不写扩展字段的关卡仍按原规则运行；day_01 只补充不影响玩法的顺序/名称/星级字段。

## Compatibility Guardrails

- `config.load()` 继续返回 day_01，`day_01.json` 的初始阳光、天空阳光间隔、12 只僵尸的出怪与波次数值保持不变；新增字段默认值必须复现旧行为。
- `Simulation.snapshot()` 与现有事件序列保持不变；下一波预告和星级统计通过 `Simulation.wave_preview()`、`Simulation.run_stats()` 等独立只读接口提供，不写入快照，不新增模拟事件，避免破坏 `tests/replay` 基线。
- `Simulation(config, level)`、`Command(...)`、`click(...)`、`visible_plant_cards(...)`、`Renderer.draw(...)` 的新参数全部带默认值；现有测试、基准和 `--smoke-play` 继续按旧调用方式工作。
- 关卡控制器和菜单状态只存在于 `app`/`presentation`；`Simulation.phase` 仍只有 menu/playing/paused/won/lost，不把 UI 状态写进规则层。
- 表现层不新增模拟事件；命中/枪口/收集特效由既有 `hit`、`shot`、`collected` 与投射物消失推导。
- `tools/validate_assets.py` 增加战役/关卡校验，Windows 构建继续在打包前调用它；新关卡 JSON 由现有 PyInstaller assets 递归打包覆盖。

## Phased Delivery（先可玩，后增强）

### Milestone A - 可玩版本（P1）

1. 修复被窝/嗷嗷嗷素材并重新生成 atlas，完成卡片/地图/菜单可见性检查。
2. 增加 5 个关卡 JSON、`campaign.json`、`load_campaign()` 与关卡选择界面。
3. 接入初始阳光/天空阳光间隔/可用植物/割草机行/波次预告和关卡 HUD。
4. 增加 `progress.py`，实现通关解锁、进度保存和损坏回退。
5. 在表现层加入狗狗次级动作、阳光光晕/淡入淡出、子弹尾迹和命中特效。
6. 运行最小验证，交付可完整从第 1 关玩到第 5 关的 Windows 版本。

### Milestone B - 增强（P2）

1. 增加星级目标判定、结算展示和最佳星级保存。
2. 增加无尽模式入口、无尽导演、失败结算与最佳波数保存。
3. 复跑最小验证，补充无尽 10 波和星级场景。

## Focused Validation Plan

1. **狗狗帧**：运行导入工具重新生成 dogs/dogs_photo 相关 atlas，执行 `tools/validate_assets.py`；运行 `pytest tests/integration/test_animation.py -k dog_frame_bounds`；把被窝/嗷嗷嗷的源图与原图对照，检查菜单、卡片、地图、拖动和倒地姿态的脚掌/尾巴完整。
2. **关卡与进度**：运行 `pytest tests/unit/test_campaign_config.py tests/unit/test_campaign_progress.py`；实际从第 1 关玩到第 5 关，确认逐关解锁、星级结算/最佳星级、失败重试、关闭后重开进度保留；手工损坏 progress.json 后启动，确认回退且不崩溃。
3. **无尽**：通关第 5 关后进入无尽，至少推进 10 波，确认敌人持续增强、没有“清空即胜利”、失败结算和最佳记录保存；重启后记录保留。
4. **流畅表现**：在狗狗外观下录 10 秒标准对局，检查狗狗动作无超过 50 毫秒静止、无重影，阳光收集反馈同帧、子弹无跳变；运行一次标准场景基准，保持平均≥58 帧/秒、p95≤18 毫秒。
5. **回归**：用默认外观与狗狗外观各完成一局普通关卡；打开狗狗照片外观检查菜单/卡片/地图后返回，不做完整对局；检查暂停、重开、返回菜单、外观选择和 `--smoke-frames`；最后构建 Windows 目录包并启动一次。

不执行：全量 pytest、长时间压力测试、所有外观/角色组合矩阵、安卓安装与触控验收、完整星级/无尽极限测试。

## Risks and Mitigations

- **轮廓排序错位**：连通体按中心和行列排序，导入后立即生成源图/输出帧对照；发现错位只修正排序，不重画素材。
- **程序化动作与现有姿势节奏冲突**：次级动作只改显示偏移，不改变 atlas 帧时长；保留 12 姿态/秒的素材节奏，基准与 `validate_assets.py` 仍能通过。
- **进度损坏导致无法启动**：原子写入 + 读取异常回退默认进度；回退只影响进度，不影响外观和关卡资源加载。
- **无尽模式性能失控**：导演限制同屏僵尸数并放缓生成；特效使用缓存/简单绘制，不引入每帧大图重建。
- **范围膨胀**：严格按 Milestone A/B 推进，P1 先可玩；星级/无尽不阻塞 5 关战役交付。

## Complexity Tracking

无宪章违规。没有新增引擎、数据库、网络服务或第二套游戏逻辑；新增模块仅覆盖关卡目录、进度、无尽导演和表现扩展，属于现有结构的必要增量。

## Post-design Constitution Check

| 原则 | 状态 | 复核依据 |
|---|---|---|
| I | PASS | Milestone A 交付完整 5 关战役；星级/无尽不阻塞核心循环。 |
| II | PASS | 关卡/星级/无尽规则在域层，表现层只读快照；进度独立。 |
| III | PASS | 关卡参数、星级阈值和无尽参数均进入 JSON 配置；既有数值继续单一来源。 |
| IV | PASS | 定向测试 + 一次完整试玩 + 一次基准，覆盖正常、失败和回退路径。 |
| V | PASS | 现有 `load()`、两套外观、暂停/重开/菜单和 Windows 打包保留，最后回归。 |
| 开发约束 | PASS | 复用现有架构，无新依赖，无第二框架。 |
