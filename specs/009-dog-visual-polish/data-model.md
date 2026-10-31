# Data Model: 狗狗视觉与阳光动效优化

This feature extends existing domain entities; it does not add persistent storage.

## PlantProfile (existing configuration entity)

The `plant_types` entry in `assets/config/balance.json` is authoritative for plant-specific values.

| Field | Meaning | Validation |
|---|---|---|
| `id` | Stable role/type identifier (`pangbaobao`, `huanghuang`) | Unique; dog skin only for new cards |
| `role` | Simulation behavior (`potato_mine`, `snow_shooter`) | Supported by domain dispatch |
| `price`, `hp`, `cooldown_ticks` | Economy and survivability | Non-negative; existing config validation |
| `arming_ticks` | Mine preparation duration | Positive integer; only potato mine |
| `trigger_distance`, `blast_radius`, `damage` | Mine trigger and explosion | Non-negative; all in documented canvas units/HP |
| `attack_interval_ticks`, `projectile_speed` | Snow Pea cadence and travel | Positive; reuse existing projectile rules |
| `slow_factor`, `slow_duration_ticks` | Temporary enemy movement and bite-frequency modifier | `0 < slow_factor < 1`; positive integer duration |

## Plant (existing runtime entity)

| Field | Meaning / lifecycle |
|---|---|
| `type_id`, `row`, `col`, `hp` | Existing identity, location and health |
| `next_action_tick` | For a mine, arming completion; for a shooter, next shot time |
| `action` | `arming` → `armed` → `triggered` for mine; existing idle/attacking for other plants |

**Invariant**: A mine can trigger at most once. It cannot explode while arming but remains vulnerable to ordinary zombie bites; after triggering its damage is resolved once and it is removed.

## Projectile (existing runtime entity)

| Field | Meaning |
|---|---|
| Existing source, lane, position, damage, speed, birth tick, active flag | Maintains existing travel/collision contract |
| `slow_factor`, `slow_duration_ticks` | Optional impact effect; unset for ordinary peas |

**Invariant**: Impact damages once. An ice projectile additionally applies/refreshes a bounded slow effect to the hit zombie.

## Zombie (existing runtime entity)

| Field | Meaning |
|---|---|
| Existing type, lane, position, HP, action and bite target | Unchanged base simulation state |
| `slow_until_tick` | Expiration tick for the current slow effect |
| `slow_factor` | Active movement multiplier; returns to 1 when effect expires |
| `slow_bite_restore_tick` | Pending base-cadence bite tick saved while a slow effect changes the current cooldown |

**Invariant**: Slow never stacks below the configured factor; repeated ice hits refresh the expiry; movement speed and bite cadence return to their base values after expiry. Bite damage is unchanged.

## SunPickup (existing runtime entity)

| Field | Meaning |
|---|---|
| `id`, `value`, `expires_tick`, `born_tick` | Existing identity, economy and lifetime |
| `source_kind` | `sky` or `plant`, selecting a start position |
| `start_x`, `start_y`, `target_x`, `target_y` | Deterministic fall path endpoints |
| `x`, `y` | Current collectible and rendered position |
| `motion_duration_ticks` | Time to land; resting motion remains visual and deterministic |

**Invariant**: Renderer and input use the same current position; collection is single-use; expiration remains based on the existing birth/expiry ticks; pause freezes motion.

## Dog Visual Profile (existing skin manifest/rendering metadata)

Role scale, sprite frame, alpha bounds, and anchor determine visible silhouette. Scale changes are presentation-only. Each tested pose's non-transparent silhouette must fit the game canvas in both `dogs` and `dogs_photo`; visible heights remain within the spec tolerance inside each skin, with 被窝 about 20% smaller than that skin's current version. 胖宝宝 and 黄黄 remain available only in `dogs`.

