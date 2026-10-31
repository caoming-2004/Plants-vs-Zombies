# Data Model: 狗狗外观与玩法体验优化

## Existing Authoritative State

`Simulation` 是唯一游戏状态所有者。`step()` 在固定 tick 中应用命令，再调用 `systems.advance()`；`snapshot()` 输出只读快照供 Renderer 和输入适配读取。外观菜单选择状态仍由 `AppearanceController` 拥有，不进入战斗规则状态。

## Entities and Changes

### Plant

- **Existing fields**: `id`, `type_id`, `row`, `col`, `hp`, `next_action_tick`, `action`。
- **Use in this feature**: `sunflower`/被窝作为阳光起点角色；`pangbaobao`、`huanghuang` 仍是独立植物 ID 和职责。
- **Change**: 无必需字段更改。被窝的 actor frame/scale 从现有 skin manifest 与 Animator 解析。
- **Invariants**: 植物位置仍为单个逻辑格；角色展示不得更改价格、冷却或规则职责。

### ZombieTypeConfiguration

由 `assets/config/balance.json:zombie_types[]` 定义的配置实体：

| 字段 | 含义 |
|---|---|
| `id` | 稳定逻辑 ID：`zombie_basic`、`zombie_fast` 或 `zombie_tough` |
| `display_name` | 本地化类型名称，用于波次/识别提示 |
| `hp` | 初始生命值；耐久型高于普通型，快速型低于普通型 |
| `speed` | 每秒地图逻辑像素；快速型高于普通型，耐久型低于普通型 |
| `bite_damage` | 每次啃食伤害，正整数 |
| `bite_interval_ticks` | 啃食间隔，tick 为单位 |
| `contact_distance` | 开始啃植物的水平接触距离，逻辑像素 |

Rules: IDs nonempty and unique; all values finite and in valid ranges; every spawn type ID references one configured type. New archetypes reuse the current zombie animation role, with renderer cues keyed by type ID; combat reads only the corresponding config record.

### Zombie

- **Existing fields retained**: `id`, `type_id`, `row`, `x`, `hp`, `next_bite_tick`, `target_plant_id`, `action` and existing slow fields.
- **Change**: None required if `type_id` already identifies the archetype. `add_zombie` initializes HP from the selected `ZombieTypeConfiguration`.
- **Invariants**: All archetypes move left; target selection, bite cadence, damage, projectile hits, mower clearing, death and loss handling remain in `systems.py` against the configured type ID.
- **Presentation mapping**: `type_id` stays gameplay identity; dog/default appearance maps the zombie actor art to existing `zombie_basic` clips. Fast/tough identity gets a small distinct renderer cue; no duplicate zombie movement logic in Renderer.

### WaveSchedule and WaveState

Level data stays in `assets/levels/day_01.json`:

- `waves[]`: ordered wave entries with `id`, `start_tick`, and localized `label`/announcement text.
- `spawn_schedule[]`: existing `tick`, `row`, `type_id`, extended by `wave_id`.
- At least three waves; valid wave IDs are unique and referenced by scheduled spawns; ticks are nonnegative and ordered. The schedule contains the three configured enemy archetypes and phases with progressively stronger compositions.
- Simulation transient state: `current_wave_id` (or index), initialized to no wave on reset and advanced when the scheduled start tick is reached; a `wave_started` event reports ID/label/tick once.
- Snapshot adds current wave and total wave count for HUD display. Reset restores wave progress. Victory still requires all scheduled enemies to have spawned and all living zombies to be gone; a mower cannot bypass remaining waves.

### SunPickup Motion

- **Existing fields retained**: `id`, `x`, `y`, `value`, `expires_tick`, `born_tick`, `source_kind`, `start_x/y`, `target_x/y`, `motion_duration_ticks`.
- **Addition**: Optional `motion_arc_height` (logical pixels, `0` by default) or equivalent explicit hop-path parameter.
- For `source_kind='plant'` when produced by sunflower, start coordinate is derived from the current visible sunflower body/frame, target remains its existing nearby grass position, and arc height is positive. Tick-based deterministic interpolation updates `x/y`, followed by current bobbing behavior after flight.
- **Invariants**: `expires_tick = born_tick + configured lifetime`; moving visual position and input hit position both use snapshot `x/y`; collect remains an atomic one-time command. Sky-source sun retains the current fall path.

### DragState

- **Existing fields retained**: `plant_type_id`, continuous logical `pointer`, `tool_kind`, `hover_cell`, `preview_valid`, `reason_code`.
- `pointer` remains the exact mapped pointer coordinate during movement. `hover_cell` is only a candidate/highlight and must not replace preview coordinates.
- On release inside the lawn, one deterministic nearest-cell candidate is computed; exact-distance ties choose the same side every time. `placement_reason` is applied to that candidate. An occupied/invalid candidate is rejected with the existing reason, no resource/cooldown cost, and no search for another empty cell. Release outside lawn is rejected.
- **Authority**: Renderer previews; input adapter maps to a command; `Simulation`/`placement_reason` revalidates before charging resources.

### Appearance Selection View

- Existing skin choice remains `default`, `dogs`, `dogs_photo` for plants and `default`, `dogs` for zombies.
- Dog role previews add `pangbaobao` and `huanghuang` as individually selectable preview items with Potato Mine/Ice Shooter labels. A renderer-owned `focused_preview_role` indicates which role is being previewed in the menu; it is transient presentation state and is not saved into `Simulation`.
- Preview requests use the existing asynchronous catalog load; before the `dogs` atlas is ready, the menu keeps rendering and accepting input with a loading placeholder.
- The global appearance choice remains unchanged; selecting either preview does not replace another role. In-game cards remain separate role IDs and are available in dog cartoon appearance as today.
- No per-role replacement map or new skin assets are added; selecting a dog appearance never changes plant prices, mechanics, or other role identity.

## Snapshot and Events

- Existing snapshot shape remains source of display state. Add wave progress fields only as required by the HUD.
- Add `wave_started` event at most once for each scheduled wave; use its payload for a brief announcement. Existing `sun_created`, `collected`, `planted`, `died`, and `result` event shapes remain backward compatible.
- Simulation/replay state includes wave scheduling and deterministic sun motion parameters. Renderer transient effects are cleared by the existing `session_id` reset boundary.
