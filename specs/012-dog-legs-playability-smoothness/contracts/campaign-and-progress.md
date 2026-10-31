# Contract: 战役、进度与无尽模式

**Feature**: `012-dog-legs-playability-smoothness` | **Date**: 2026-10-31

## 范围

定义关卡数据、战役流程、星级、进度保存和无尽模式的边界；不改变现有伤害、费用、冷却、攻击、胜负和 `Command` 语义。

## 资源契约

### CampaignManifest

`assets/levels/campaign.json` 必须包含：

- `schema_version=1`
- `stages`: 至少 5 个关卡 ID，顺序即解锁顺序，ID 唯一且对应同名 `assets/levels/<id>.json`
- `endless`: 无尽参数（`unlock_after`、初始阳光、天空阳光间隔、可用植物、割草机行、首批波次、间隔、数量/类型增长、同屏上限）

校验失败必须阻止游戏启动和 Windows 构建。`unlock_after` 必须是 `stages` 最后一关。

### LevelDefinition

每个关卡 JSON 必须包含：

- `id`（与文件名、campaign 项一致）、`order`（1..N）、`name`、`mode`（`campaign`/`endless`）
- `rows=5`、`cols=12`
- `initial_sun`、`sky_sun_interval_ticks`（可选；缺省沿用 `balance.json`）
- `mower_rows`（可选；缺省为全部行；显式给出时为 0..4 子集）
- `available_plants`（可选；缺省为 `balance.json` 的全部植物；显式给出时非空且为现有植物 ID 子集）
- `waves`（campaign 至少 3 个，`strength` 严格递增）
- `spawn_schedule`（每个波次至少 1 个出怪）
- `star_goals`（campaign 至少 2 个，无尽可为空；day_01 也随本次更新补足 2 个）

`day_01.json` 的既有波次和数值保持不变；新增字段的默认值必须复现当前行为，确保 `config.load()`、replay fixture 和现有测试不变。

### StarGoal

`kind` 只能是：

| kind | 语义 | threshold |
|---|---|---|
| `mowers_used_at_most` | 本局触发的割草机数不超过阈值 | 非负整数 |
| `clear_within_ticks` | 在阈值 tick 内通关 | 正整数 |
| `sun_collected_at_least` | 本局收集阳光不少于阈值 | 非负整数 |

星级只在 `phase=="won"` 时结算；未通关不授予。星级不参与解锁。

## 加载契约

- `config.load()` 保持返回 `(balance, day_01)`，不引入新必填字段。
- 新增 `config.load_campaign()`，返回 `(balance, CampaignManifest, levels_by_id)`；必须校验全部关卡和引用关系。
- `Simulation(config, level)` 保持现有签名；新关卡通过 `level` 传入。
- `Simulation.snapshot()` 和事件 schema 不变；新增数据通过：
  - `Simulation.run_stats() -> dict`
  - `Simulation.wave_preview() -> dict | None`
  - `domain.campaign.evaluate_stars(level, stats) -> list[str]`（由 app 在胜利时调用；不在 Simulation 内硬编码关卡规则）
- 不新增模拟事件；表现层从既有事件和实体的出现/消失推导特效。

## 进度契约

### 文件

`%LOCALAPPDATA%\PvzMiniGame\progress.json`（Windows）。结构见 `data-model.md`。

- 写入使用同目录临时文件 + `os.replace`；失败只记日志，不影响游戏继续。
- 读取失败、JSON 损坏、`schema_version` 不匹配或字段类型错误：返回默认进度（day_01 解锁、其他锁定、无尽锁定/零记录），并在界面给出一次可理解提示。
- 未知关卡 ID 忽略；缺失 day_01 自动补为解锁；不因存档损坏而误解锁。
- 通关：`unlocked` 追加下一关；`levels[id].cleared=true`；`best_stars=max`；`best_ticks=min`。
- 失败：不推进解锁，不写入胜利记录；重试必须使用完整初始状态。
- 无尽失败：`best_wave=max`、`best_kills=max`；解锁状态由最后一关通关决定。

### 解锁规则

1. 初始只解锁 `stages[0]`。
2. 通关 `stages[i]` 解锁 `stages[i+1]`；已解锁关卡可重复进入。
3. 通关最后一关后 `endless.unlocked=true`；未解锁时入口锁定并显示条件。
4. 星级和最佳成绩只增不减；重复通关不重复解锁或回退进度。

## 无尽契约

- `EndlessDirector` 只在 `mode=="endless"` 时启用；由 `Simulation.step` 在推进前调用，保证规则与测试一致。
- 导演必须始终保留至少 2 个未来波次/出怪，避免“清空即胜利”或空场卡住。
- 每波保持至少 1 个敌人；随波数增加数量、快速/高耐久比例并缩短间隔，直到配置下限。
- 同屏僵尸数不得超过 `max_active_zombies`；超限时延迟后续出怪，不得丢弃已计划波次。
- 无尽模式不触发 `won`；失败沿用现有割草机/防线突破规则，进入结算并记录本次最佳。
- 所有参数来自 `campaign.json`；不得在 `endless.py` 中散落裸数值。

## UI 流程契约

- 主菜单“开始游戏”进入关卡选择；“怎么玩”“选择外观”“退出”保持可用。
- 关卡选择：5 个关卡卡片 + 无尽入口；每张卡显示锁/解锁、名称、最佳星级；点击已解锁卡进入该关。
- 结果页：胜利显示星级与“下一关/重试/返回菜单”；失败显示“重试/返回菜单”；无尽显示生存波数/击杀/最佳记录。
- 关卡选择/结果操作只改 `app` 的界面状态或调用 `start_level(level_id)`；不直接改 `Simulation` 内部状态。
- 暂停、重开、返回菜单和外观选择保持现有行为；外观选择不写入进度。

## 兼容性门槛

- 现有 `tests/replay/test_base_replay.py`、`tests/integration/test_skin_invariance.py`、`test_playable_loop.py` 必须继续通过；若无法保持，必须记录并说明原因，不能静默更新基线。
- 旧关卡 JSON 不写扩展字段时仍按默认值运行。
- 构建前 `tools/validate_assets.py` 必须同时校验战役/关卡 JSON；坏配置应阻止 Windows 构建。
