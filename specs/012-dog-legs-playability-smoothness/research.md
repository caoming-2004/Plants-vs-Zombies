# Research: 完整狗狗形象、五关战役与流畅表现

**Feature**: `012-dog-legs-playability-smoothness` | **Date**: 2026-10-31

本文件记录 Phase 0 的技术决策。所有待澄清问题已在规格澄清阶段解决；以下决定用于指导实现，不引入新框架或新依赖。

## 1. 架构与兼容性

- **Decision**: 继续使用现有 Python 3.12 + pygame-ce 2.5.8 单项目结构，复用 `Simulation`、`systems`、`renderer`、`Animator`、`skin_catalog` 和 JSON 资源；不新增引擎、数据库或运行时依赖。
- **Rationale**: 现有核心循环、固定 60Hz 模拟、快照和重放测试已经稳定；本次主要是内容与表现增量，重写架构会拖慢“先得到可玩版本”的目标。
- **Alternatives considered**: 引入 Godot/Unity 或第二套渲染层（成本高、破坏现有验证）；把战役状态放进 `Simulation.phase`（污染规则层）。

## 2. 快照、事件与旧测试兼容

- **Decision**: 保持 `Simulation.snapshot()` 和现有事件 schema 不变。关卡预告通过新增只读方法 `Simulation.wave_preview()` 获取；星级所需统计通过 `Simulation.run_stats()` 获取；不新增模拟事件。表现层用现有 `hit`、`shot`、`collected` 和投射物消失推导命中/枪口特效。
- **Rationale**: `tests/replay/test_base_replay.py` 对比完整快照和事件列表；新增顶层字段或事件会破坏 day_01 基线，增加不必要的重放维护。把预告/统计作为单独读取面也符合规则与渲染分离。
- **Alternatives considered**: 在快照里加 `wave_preview`/`stats` 并更新基线（会扩大回归面）；新增 `projectile_hit` 事件（会改变事件序列，收益不抵成本）。

## 3. 狗狗完整轮廓提取

- **Decision**: 在 `tools/import_dog_assets.py` 增加整张图连通轮廓提取，仅用于被窝和嗷嗷嗷（含 dogs_photo 的复用路径）：以 alpha 96 取 12 个主体连通体，按包围盒中心做 4×3 行/列排序，取完整包围盒，等比缩放到 256×256 帧内并保留至少 8 像素透明边距，脚底固定在 232。源图不改写；重新生成 atlas、manifest、provenance。其他狗狗角色继续使用现有路径。
- **Rationale**: 源图姿态会越过 4×3 等分格线，当前 8 像素 overscan 后仍会把脚掌切平；完整连通体可以保留越线肢体，12 个主体也足以稳定排序。只改目标角色可避免无关角色外观漂移。
- **Alternatives considered**: 扩大等分格线余量（相邻姿态会串入，且不能保证覆盖）；人工逐帧蒙版（成本高）；重新生成狗狗美术（用户要求复用现有素材）。

## 4. 关卡数据与加载

- **Decision**: 新增 `assets/levels/campaign.json`（关卡顺序、无尽配置、解锁规则）和 `day_02`～`day_05.json`；`day_01.json` 增加可选字段但保持现有关卡数值/波次。保留 `config.load()` 返回 day_01 的旧行为；新增 `config.load_campaign()` 做全量校验。`Simulation` 继续接收单个 level。
- **Rationale**: 现有测试、基准和 `--smoke-play` 都依赖 `load()`；新增加载器可以在不破坏旧入口的情况下提供战役。JSON 与当前 `balance.json` 的资源模式一致，便于调整波次/星级/压力条件。
- **Alternatives considered**: 把 5 关注册为 Python 常量（不利于数值调整）；只扩展现有 day_01（无法满足多关卡与进度）。

## 5. 进度保存

- **Decision**: 新增 `src/pvz_game/progress.py`，把进度写到 `%LOCALAPPDATA%\PvzMiniGame\progress.json`（复用 `resources.error_logger` 的用户数据目录约定），采用临时文件 + `os.replace` 原子写入；读取失败/损坏/版本不匹配时回退默认进度并记录错误。只保存解锁关卡、每关最佳星级/时间、无尽最佳波数/击杀。
- **Rationale**: 单机离线游戏只需要一个小型本地文件；SQLite/注册表属于过度设计。原子写入和回退覆盖规格的失败路径；外观选择按已确认范围不保存。
- **Alternatives considered**: 存到 `assets/`（安装目录可能只读）；使用 SQLite（无必要依赖）；云存档（超出范围）。

## 6. 关卡界面与状态

- **Decision**: 在 `app.py` 维护 `menu_view`（主菜单/关卡选择/外观/帮助）和当前关卡；`Simulation.phase` 仍只表示 menu/playing/paused/won/lost。`renderer` 增加关卡选择、星级和无尽入口绘制；`input.click` 增加可选 view/levels 参数，默认参数保持现有行为。主菜单“开始游戏”进入关卡选择，旧的 `Command("Start")` 仍可用于直接开始当前关/测试。
- **Rationale**: 菜单是界面状态，不是游戏规则；放进 Simulation 会让快照和重放包含 UI 噪声。默认参数和旧命令可避免破坏现有测试。
- **Alternatives considered**: 给 Simulation 增加 `level_select` phase（污染规则层）；新建独立 UI 框架（成本不匹配）。

## 7. 无尽模式导演

- **Decision**: 新增 `domain/endless.py` 的 `EndlessDirector`，在无尽关卡中按确定性公式追加波次/出怪；`Simulation` 在 `step` 中驱动导演，模式为 `endless` 时跳过“清空即胜利”，只按防线突破判定失败；导演限制同屏僵尸数并逐步提高数量/类型比例/节奏。配置写入 `campaign.json` 的 `endless` 段。
- **Rationale**: 域内导演保证测试、试玩和重开使用同一规则；确定性生成避免随机性破坏可复现性。有限长表最终会结束，不适合无尽。
- **Alternatives considered**: 预生成很长的固定表（有终点、不可持续）；随机生成（不可复现、难以测试）；把导演放在 app 层（规则分散）。

## 8. 星级目标

- **Decision**: 星级目标写在每个关卡 JSON 的 `star_goals`，首批采用三种可统计类型：`mowers_used`（最大次数）、`clear_ticks`（最大完成 tick）、`sun_collected`（最小收集量）。`Simulation` 只维护 `run_stats()` 统计；`domain.campaign.evaluate_stars()` 在通关时判定；进度只保留历史最佳星级。
- **Rationale**: 三种类型都可从现有事件/状态推导，不增加新模拟机制；数据驱动便于每关给出不同目标。星级不影响解锁，符合规格。
- **Alternatives considered**: 硬编码每关判定（数值散落，违反集中管理）；新增复杂成就系统（超出“快速可玩”范围）。

## 9. 流畅表现

- **Decision**: 保持 60Hz 模拟与约 12 个源姿态/秒的素材节奏；在表现层按渲染帧叠加程序化次级动作（狗狗呼吸/行走起伏、攻击后坐、受击回弹），让每帧都有可见变化且不产生 alpha 混合重影。阳光增加淡入淡出和呼吸光晕；子弹增加短尾迹和命中特效；枪口闪光由现有 `shot` 事件驱动，命中特效由投射物消失/命中事件在表现层推导。所有效果只依赖快照和事件，不改变模拟。
- **Rationale**: 直接提高源姿势帧数需要新素材或 alpha 插值（会重影）；程序化次级动作成本低、无新依赖，能改善低速移动和 12 姿态节奏的观感。尾迹/光晕让阳光和子弹的连续运动更容易被眼睛追踪。
- **Alternatives considered**: 提高图集姿态数到 30+/秒（需要生成/重绘，且可能引入重影）；整帧交叉淡化（明显重影）；高分辨率内部画布（渲染成本高，收益有限）。

## 10. 验证范围

- **Decision**: 只保留定向测试和一次完整试玩：狗狗轮廓一项、战役配置/进度/无尽各一项、现有重放与动画关键用例、标准场景基准；不跑全量 pytest、外观矩阵、长时压力测试或安卓验收。
- **Rationale**: 用户要求快速得到可玩版本。新风险集中在素材边界、关卡/解锁/保存、无尽生成和表现帧率，定向检查足以覆盖这些路径；全量矩阵的成本远高于收益。
- **Alternatives considered**: 全量回归 + 六套外观矩阵 + 安卓实机（超出本轮范围与时间预算）。

## 11. 平台与打包

- **Decision**: 只做 Windows 桌面版验收；PyInstaller spec 已递归打包整个 `assets/`，新增关卡 JSON 无需改打包树。构建前通过 `tools/validate_assets.py` 增加战役/关卡校验，保证坏关卡阻止构建。
- **Rationale**: 用户已确认仅 Windows；现有打包脚本和资源树可以直接复用。
- **Alternatives considered**: 追加安卓打包/验收（已明确移出范围）。

## 开放问题

无未决澄清项。剩余为 tasks 阶段的实现细节，不改变架构或验收策略。
