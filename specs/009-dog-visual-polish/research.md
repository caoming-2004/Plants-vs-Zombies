# Research: 狗狗视觉与阳光动效优化

## 1. Existing project structure and extension points

**Decision**: Use the current single-project architecture and extend the existing plant config and deterministic simulation paths.

**Findings**:

- `assets/config/balance.json` declares plant ID, role, health, cooldown, price, attack speed and damage. Current dog roles `pangbaobao` and `huanghuang` are configured as generic blocker and shooter.
- `src/pvz_game/domain/systems.py::advance` handles producer/shooter actions, projectile movement/hit and zombie movement. `simulation.py` owns commands, economy, snapshots and `add_sun`; `models.py` owns `Plant`, `Projectile`, `Zombie` and `SunPickup` state.
- `presentation/renderer.py` uses the same snapshot to render plants, projectiles and sun tokens. `presentation/input.py` uses snapshot sun coordinates for collection, so visual travel must keep the hit-test coordinate synchronized.
- `presentation/animation.py` supplies role-specific dog scale, frame anchors and actor drawing; `dog_validation.py` and `tools/validate_assets.py` provide existing silhouette/asset validation paths.
- `presentation/scenes.py` and `app.py` own menu drawing/input and scene transition; `skin_catalog.py` caches skin data.

**Alternatives considered**: A separate effect/plant framework would duplicate the current role dispatch and lifecycle. Extend the existing data models and `advance` logic with two narrow roles/effects instead.

## 2. Original-game reference and mechanic selection

**Decision**: Use Potato Mine's delayed trigger/explosion and Snow Pea's damage-plus-slow as the recognizable dog character mechanics; keep both behaviors configurable and aligned with this project's simpler enemy/balance model.

**Rationale**: The user explicitly selected 胖宝宝→土豆雷 and 黄黄→寒冰射手. The EA original-game readme groups potato mines with cheap one-hit-kill plants, notes multiple Snow Peas do not slow zombies more than one, and says frozen zombies eat more slowly; this supports a one-use mine and a bounded, non-stacking slow that affects movement and bite cadence. It also documents sun falling to the ground and disappearing after a few seconds if not collected. [EA Plants vs. Zombies Readme](https://akamai.cdn.ea.com/eadownloads/u/f/manuals/GAME-PVZ/en_US_readme.html)

**Alternatives considered**: Reusing blocker/shooter roles would ignore the user's correction. A generalized effect scripting system is unnecessary for these two roles.

## 3. Potato Mine lifecycle

**Decision**: Represent preparation, armed and triggered states through the existing plant action/tick state. An unarmed mine cannot explode but remains vulnerable to the existing zombie bite target; an armed mine triggers once when a zombie approaches its tile, deals configured damage to nearby same-row zombies, and is removed.

**Rationale**: A short role branch in the deterministic `advance` loop is enough; no new timer or event subsystem is needed. An initial arming interval of 840 ticks (14 seconds at the existing 60 Hz simulation rate) gives a meaningful setup window and remains centralized in configuration. An arming zombie can still damage the plant through the current target/bite path.

**Alternatives considered**: Activating on placement would not feel like Potato Mine; allowing an unarmed mine to block zombies would conflict with its hidden preparation phase.

## 4. Snow Pea slow effect

**Decision**: Store a temporary slow duration and factor on the zombie or effect state; use the existing projectile hit to apply damage and refresh the effect. Repeated hits refresh time, do not stack strength, and expiry restores normal movement and bite cadence.

**Rationale**: This reuses current projectile travel and collision and makes the change deterministic/replayable. A starting factor of 0.5 and duration 300 ticks (5 seconds) are configuration values for first playable balance, not hard-coded in presentation.

**Alternatives considered**: A purely visual ice tint would not change gameplay. Multiplying movement speed per hit would stack incorrectly and could permanently stop a zombie.

## 5. Sun movement and collection

**Decision**: Keep sun creation, value and expiry in `Simulation`; store enough deterministic motion state to derive the current displayed/collectible position. Render the fall and resting bob from that state, and use the same position for input hit-testing.

**Rationale**: Current sun pickups have fixed coordinates and the renderer/input both read snapshot coordinates. Separating rendered and clickable positions would make collection feel inaccurate. The EA readme documents the fall-to-lawn and uncollected-expiry pattern; it does not require changing this game's resource timing.

**Alternatives considered**: A renderer-only animation cannot reliably update pointer hit-testing. Wall-clock-only motion risks advancing while paused and becoming replay/non-deterministic.

## 6. Dog size, full-body visibility and transition performance

**Decision**: Keep source art and atlas unchanged; adjust role scales/anchors and validate alpha bounds for all dog action poses in both `dogs` and `dogs_photo`. The two new plant roles remain dog-cartoon-only. Inspect the existing start/switch path and asset cache before changing it; only move expensive work off the first visible transition if profiling confirms it is responsible.

**Rationale**: The user asked for immediate visual correction and a quick playable update. The 008 benchmark observed 62.26 FPS after throttling skin manifest checks, so performance work should target the actual remaining transition/frame stalls rather than add broad optimizations. Measure click-to-first-target-frame with timestamped 60fps capture or a monotonic clock over 10 trials.

**Alternatives considered**: Cropping source frames could hide paws/tails and conflict with full-body visibility. Rewriting the app loop or introducing asynchronous loading before profiling would be a larger unnecessary change.

## Open decisions

None. User confirmed Potato Mine and Snow Pea. Numeric values in this research are initial tunable configuration targets, not requirements to change the existing overall economy.
