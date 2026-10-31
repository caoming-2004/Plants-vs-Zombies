# Data Model: 完整狗狗形象、五关战役与流畅表现

**Feature**: `012-dog-legs-playability-smoothness` | **Date**: 2026-10-31

本文件描述新增/扩展的数据边界。既有 `Simulation.snapshot()` 和事件 schema 保持不变；新增的预告、统计和进度数据通过独立只读接口或本地文件提供。

## 1. 实体总览

| 实体 | 权威来源 | 生命周期 | 说明 |
|---|---|---|---|
| CampaignManifest | `assets/levels/campaign.json` | 只读资源 | 五关顺序、解锁规则、无尽参数 |
| LevelDefinition | `assets/levels/day_0*.json` | 只读资源 | 单关波次、可用植物、压力条件、星级目标 |
| SimulationState | 内存 `Simulation` | 单局 | 权威玩法状态；schema 不新增字段 |
| RunStats | 内存 `Simulation.run_stats()` | 单局 | 星级判定所需的只读统计 |
| WavePreview | 内存 `Simulation.wave_preview()` | 单局、按召唤点变化 | 下一波类型/数量/行预告 |
| ProgressFile | 本机 `progress.json` | 跨启动 | 解锁、最佳星级/时间、无尽记录 |
| DogFrameAsset | dogs/dogs_photo atlas + manifest/provenance | 素材构建期 | 完整轮廓帧、锚点、留白 |
| PresentationState | 内存表现层 | 单帧/单局 | 次级动作、尾迹、光晕、命中特效；不入存档 |

## 2. CampaignManifest

```json
{
  "schema_version": 1,
  "stages": ["day_01", "day_02", "day_03", "day_04", "day_05"],
  "endless": {
    "unlock_after": "day_05",
    "initial_sun": 150,
    "sky_sun_interval_ticks": 600,
    "available_plants": ["sunflower", "peashooter", "wallnut", "jalapeno", "pangbaobao", "huanghuang"],
    "mower_rows": [0, 1, 2, 3, 4],
    "first_wave_tick": 600,
    "base_interval_ticks": 900,
    "min_interval_ticks": 360,
    "base_zombies": 2,
    "zombie_growth": 1,
    "max_zombies_per_wave": 10,
    "fast_ratio_base": 0.15,
    "fast_ratio_growth": 0.04,
    "tough_ratio_base": 0.0,
    "tough_ratio_growth": 0.05,
    "max_active_zombies": 28
  }
}
```

**Validation**

- `schema_version` 必须为 1。
- `stages` 至少 5 个、ID 唯一、顺序连续；每个 ID 必须存在对应关卡文件。
- `unlock_after` 必须是 `stages` 中最后一关。
- 无尽参数必须为正数；比例在 0..1；`min_interval_ticks <= base_interval_ticks`；`max_active_zombies` 为正整数。
- 所有 `available_plants` 必须存在于 `balance.json` 的 `plant_types`。

## 3. LevelDefinition

```json
{
  "schema_version": 1,
  "id": "day_01",
  "order": 1,
  "name": "第 1 关 · 前院",
  "mode": "campaign",
  "rows": 5,
  "cols": 12,
  "initial_sun": 150,
  "sky_sun_interval_ticks": 600,
  "mower_rows": [0, 1, 2, 3, 4],
  "available_plants": ["sunflower", "peashooter", "wallnut", "jalapeno", "pangbaobao", "huanghuang"],
  "waves": [
    {"id": "wave_1", "name": "第一波", "start_tick": 1200, "strength": 1},
    {"id": "wave_2", "name": "第二波", "start_tick": 4800, "strength": 1.5},
    {"id": "wave_3", "name": "最后一波", "start_tick": 8400, "strength": 2.2}
  ],
  "spawn_schedule": [
    {"tick": 1200, "row": 0, "type_id": "zombie_basic", "wave_id": "wave_1"}
  ],
  "star_goals": [
    {"id": "no_mower", "kind": "mowers_used_at_most", "threshold": 0, "text": "不触发割草机"},
    {"id": "fast", "kind": "clear_within_ticks", "threshold": 9600, "text": "在 160 秒内清场"}
  ]
}
```

**Field rules**

- `id`、`order`、`name` 非空；`id` 唯一；`order` 与 campaign 顺序一致。
- `mode` 为 `campaign` 或 `endless`。
- `rows=5`、`cols=12`；草坪必须落在 1050×600 画布内。
- `initial_sun >= 0`、`sky_sun_interval_ticks > 0`；缺省时沿用 `balance.json`。
- `mower_rows` 可选；缺省为全部 5 行；显式给出时为 0..4 子集。未列出的行在初始状态即为已消耗（`state="spent"`），用于“割草机受限”压力条件。
- `available_plants` 可选；缺省为 `balance.json` 的全部植物；显式给出时非空、ID 唯一、必须存在于 `balance.json`；未列出的植物不能选择、种植或显示卡片。
- `waves` 至少 3 个（campaign），`strength` 严格递增；每个波次至少 1 个 spawn；`spawn.tick >= wave.start_tick`。
- `star_goals` 在 campaign 中至少 2 个；无尽可为空；`day_01` 也随本次更新补足 2 个。`kind` 仅允许 `mowers_used_at_most`、`clear_within_ticks`、`sun_collected_at_least`；阈值必须为非负整数/有限正数；`text` 非空。
- 无尽关卡使用 `mode="endless"`，允许 `star_goals=[]`，波次由 `EndlessDirector` 追加。

**day_01 兼容性**

`day_01.json` 的波次、出怪、初始阳光、天空阳光间隔和 12 只僵尸保持现状；新增字段取与旧行为相同的默认值。`config.load()` 继续返回 day_01，现有 replay 基线和测试不受影响。

## 4. RunStats（内存，不入快照）

| 字段 | 类型 | 来源 | 用途 |
|---|---|---|---|
| `sun_collected` | int | `CollectSun` 成功累加 | `sun_collected_at_least` |
| `plants_placed` | int | 成功 `PlantAt` 累加 | 可选星级/调试 |
| `mowers_used` | int | 割草机从 ready 进入 sweeping 的次数 | `mowers_used_at_most` |
| `plants_lost` | int | 植物 hp 归零时累加 | 可选星级/调试 |
| `elapsed_ticks` | int | 当前 `Simulation.tick` | `clear_within_ticks` |
| `won` | bool | 结算时传入/派生 | 星级只在胜利时结算 |

`Simulation.run_stats()` 返回普通只读副本；不写入 `snapshot()`，避免破坏 replay 对比。

## 5. WavePreview（内存，不入快照）

| 字段 | 类型 | 说明 |
|---|---|---|
| `wave_id` | str | 下一个尚未开始的波次 ID |
| `name` | str | 波次名称 |
| `start_tick` | int | 计划开始 tick |
| `total` | int | 该波 spawn 数量 |
| `type_counts` | dict[str,int] | 敌人类型 → 数量 |
| `rows` | list[int] | 该波涉及的行（升序、去重） |
| `lead_ticks` | int | `start_tick - 当前 tick`，用于“至少提前 2 秒”展示 |

`Simulation.wave_preview()` 从 `waves` + `spawn_schedule` 计算；无下一波时返回 `None`。无尽模式由导演保证始终有下一波。

## 6. ProgressFile

```json
{
  "schema_version": 1,
  "unlocked": ["day_01", "day_02"],
  "levels": {
    "day_01": {"cleared": true, "best_stars": 2, "best_ticks": 8420}
  },
  "endless": {"unlocked": false, "best_wave": 0, "best_kills": 0}
}
```

**Rules**

- 保存位置：`%LOCALAPPDATA%\PvzMiniGame\progress.json`（Windows）；目录复用 `resources.error_logger` 的用户数据约定。
- `unlocked` 至少包含 `day_01`；只能包含 campaign 中存在的关卡；连续解锁必须由通关产生。
- `levels[level_id].cleared` 为 bool；`best_stars` 为 0..该关星级目标数；`best_ticks` 为正整数或 null。
- `endless.unlocked` 仅在通关最后一关后为 true；`best_wave`、`best_kills` 非负；只增不减。
- 写入：临时文件 + `os.replace`；文件缺失/损坏/版本不符时返回默认进度并记录日志。
- 外观选择不写入；重启后仍回到默认/本次选择状态。
- 重复通关：星级取最大值，时间取最小值；不会重复解锁或回退记录。

**State transitions**

```text
locked --(previous stage cleared)--> unlocked --(clear)--> cleared
campaign last stage cleared --> endless.unlocked = true
endless run --> lost --> best_wave/best_kills = max(...)
progress load failure --> default progress (day_01 unlocked)
```

## 7. DogFrameAsset

| 字段 | 类型 | 说明 |
|---|---|---|
| `source` | str | 原始 PNG 文件名/路径，只读 |
| `source_component_index` | int | 完整轮廓连通体序号（0..11） |
| `source_bbox` | [x,y,w,h] | 源图完整轮廓包围盒 |
| `rect` | [x,y,w,h] | atlas 中 256×256 帧 |
| `source_size` | [256,256] | 输出画布 |
| `trim_offset` | [0,0] | 当前帧内偏移 |
| `anchor` | [128,232] | 脚底锚点 |
| `source_frames` | [int] | 源姿态索引，用于 provenance/校验 |
| `margin` | 8 | 可见像素距帧边界最小透明留白 |

**Invariants**

- 每帧只含一只狗；可见 alpha 包围盒完整落在 `8..248`（x）和 `8..232`（y）。
- 12 个源姿态全部存在且映射唯一；帧顺序按源布局行优先。
- 被窝/嗷嗷嗷在 dogs 与 dogs_photo 两套外观中引用同一目标轮廓规则。
- 原始 PNG 不改写；atlas/manifest/provenance 同步更新。

## 8. PresentationState（内存，不持久化）

| 结构 | 字段 | 说明 |
|---|---|---|
| DogMotion | `role`, `state`, `state_since`, `bob_phase`, `sway`, `squash` | 程序化次级动作；只影响显示位置/缩放 |
| ProjectileTrail | `projectile_id`, `points[(x,y)]`, `max_points=3` | 子弹短尾迹；按会话清理 |
| Effect | `kind`, `x`, `y`, `born_tick`, `ttl_ticks` | 命中/枪口/收集/挥砍特效 |
| SunVisual | `alpha`, `pulse_phase` | 阳光淡入淡出与呼吸光晕 |

**Rules**

- 不得修改 `Simulation` 或快照；只读取 tick、实体位置、事件。
- 暂停/失焦时随模拟 tick 冻结；恢复不跳变。
- 尾迹/特效数量有上限（如每类 64 个），超限丢弃最旧；不进入存档。
- 不引入 alpha 整帧混合的双姿态；次级动作用位置/缩放/透明度实现。

## 9. 关系

```text
CampaignManifest 1 ── N LevelDefinition
ProgressFile     1 ── N level records (by level id)
SimulationState  1 ── 1 LevelDefinition (运行期)
SimulationState  1 ── 1 RunStats
SimulationState  0..1 EndlessDirector（仅 endless）
DogFrameAsset    N ── 1 dog skin atlas
PresentationState 1 ── 1 当前快照/场景
```

## 10. 验证映射

| 数据/行为 | 定向检查 |
|---|---|
| 关卡/战役配置 | `tests/unit/test_campaign_config.py`：5 关、顺序、数值、可用植物、割草机行、星级目标 |
| 进度/解锁/损坏回退 | `tests/unit/test_campaign_progress.py`：通关解锁、最佳星级/时间、无尽记录、损坏文件 |
| 无尽导演 | `tests/unit/test_endless.py`：追加波次、强度递增、无胜利、失败结算、并发上限 |
| 狗狗帧 | `tests/integration/test_animation.py -k dog_frame_bounds` + 人工源图对照 |
| 兼容性 | 现有 `tests/replay/test_base_replay.py`、`tests/integration/test_skin_invariance.py` 保持通过 |
