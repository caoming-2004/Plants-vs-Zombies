---

description: "Implementation tasks for the dog appearance and gameplay polish feature"
---

# Tasks: 狗狗外观与玩法体验优化

**Input**: Design documents from `specs/010-dog-gameplay-polish/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: User requested only necessary acceptance checks. Keep the 13 exact node IDs in `quickstart.md`, one asset validation, one 10-second standard benchmark, and one packaged smoke. For each story, create its focused regression case(s) before implementation; do not run unrelated suites or pressure matrices.

**Organization**: Tasks are grouped by the five user stories from `spec.md`. P1 stories precede P2; shared renderer and simulation files make sequential story integration safest.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because files differ and prerequisites are complete.
- **[Story]**: User story label from `spec.md`.
- Every task names the repository file(s) it changes or validates.

## Phase 1: Setup

**Purpose**: Reuse the existing Windows/Pygame project and release assets; no repository, virtual environment, or dependency setup is needed.

No setup tasks are required. The project, test fixtures, skins, PyInstaller spec, and `.venv` already exist.

---

## Phase 2: Foundational

**Purpose**: Prepare shared architecture used by all stories.

No foundational code or schema migration is required. `Simulation`, immutable snapshots, `DragState`, `Catalog`, and the JSON configuration loaders already provide the shared boundaries. Each story adds only its own state and behavior.

---

## Phase 3: User Story 1 - 完整展示被窝和嗷嗷嗷 (Priority: P1) 🎯 MVP

**Goal**: Reduce both roles, keep every visible body part in frame, and make 嗷嗷嗷 face left during all relevant actions.

**Independent Test**: In both `dogs` and `dogs_photo`, verify all actual poses fit the viewport, compare visible scale with v0.5.0, and confirm dog zombies face left while walking, biting, hit, and dying.

### Tests for User Story 1

- [X] T001 [US1] Add `test_adjusted_dog_roles_fit_all_visible_frames` and `test_dog_zombie_faces_left_in_all_actor_states` to `tests/integration/test_animation.py`; run only these node IDs to record the expected pre-implementation failures.

### Implementation for User Story 1

- [X] T002 [P] [US1] Reduce the visible `sunflower` and `zombie_basic` scale multipliers by about 20% from v0.5.0 and retain readable silhouettes in `assets/skins/dogs/manifest.json` and `assets/skins/dogs_photo/manifest.json`.
- [X] T003 [P] [US1] Add cached horizontal mirroring for dog zombie frames, reflecting trim offsets and anchors so every action remains aligned, in `src/pvz_game/presentation/animation.py`.
- [X] T004 [US1] Recheck alpha-visible bounds and adjust actor/card/preview placement without cropping feet or tails in `src/pvz_game/presentation/renderer.py` and `src/pvz_game/presentation/dog_validation.py` (depends on T002–T003).

**Checkpoint**: Both requested dog appearances show complete, coordinated bodies; dog zombie faces left through walk, bite, hit, and death animation.

---

## Phase 4: User Story 2 - 从被窝身体跳出阳光 (Priority: P1)

**Goal**: Make plant-produced sun hop from near 被窝’s visible body while keeping authoritative positions and collection rules unchanged.

**Independent Test**: Check the source point and hop path, collect during movement once, pause/resume, and confirm existing expiry timing.

### Tests for User Story 2

- [X] T005 [US2] Add `test_sunflower_sun_hops_from_visible_body_and_tracks_click` to `tests/integration/test_playable_loop.py`; cover body-area start, deterministic hop positions, hit testing, and one-time balance change, and run only this new node ID before implementation.

### Implementation for User Story 2

- [X] T006 [US2] Add an optional arc-height field to `SunPickup` and update deterministic tick-based sun interpolation while retaining bobbing and expiry in `src/pvz_game/domain/models.py` and `src/pvz_game/domain/systems.py`.
- [X] T007 [US2] Start producer sun near the plant body, keep its snapshot position authoritative for drawing and click hit-testing, and preserve sky-sun behavior in `src/pvz_game/domain/simulation.py`, `src/pvz_game/presentation/renderer.py`, and `src/pvz_game/presentation/input.py` (depends on T006).

**Checkpoint**: Plant sun visibly hops from the producer and can be collected at its displayed position; value, lifetime, pause, and sky-sun rules are unchanged.

---

## Phase 5: User Story 3 - 连续拖动并就近种植 (Priority: P1)

**Goal**: Keep the dog preview under the pointer and use only the geometrically nearest cell as the release candidate.

**Independent Test**: Drag across cell centers and edges; verify continuous preview, stable tie handling, rejection of an occupied nearest cell, and no sun/cooldown cost on invalid release.

### Tests for User Story 3

- [X] T008 [US3] Add `test_drag_preview_tracks_pointer_continuously` and `test_nearest_cell_tiebreak_and_invalid_rejection_without_cost` to `tests/integration/test_drag_input.py`; cover grid centers, edges, stable equal-distance tie-break, occupied/other invalid cells, lawn exterior, and unchanged sun/cooldown on rejection; run only these node IDs before implementation.

### Implementation for User Story 3

- [X] T009 [P] [US3] Keep the exact logical pointer coordinate in `DragState`, use the nearest in-board cell only for candidate validation, apply a stable boundary tie rule, and never search for another empty cell in `src/pvz_game/presentation/input.py`.
- [X] T010 [US3] Render the translucent dog preview at the live pointer instead of the candidate-cell center, retain candidate validity feedback, and surface the simulation’s rejection reason after release in `src/pvz_game/presentation/renderer.py` and `src/pvz_game/app.py` (depends on T009).

**Checkpoint**: Drag movement is continuous; only the nearest cell is checked; invalid placement has visible feedback and never charges resources or cooldown.

---

## Phase 6: User Story 5 - 在一局中体验更多变化 (Priority: P1)

**Goal**: Reuse the existing level and core loop while adding fast and high-durability enemy types and at least three escalating, announced waves.

**Independent Test**: Verify configured enemy differences, wave progression and reset, then play one defended and one undefended level to confirm win, loss, and restart still work.

### Tests for User Story 5

- [X] T011 [US5] Add `test_wave_and_enemy_configuration_validates` in `tests/unit/test_config_and_models.py`, plus `test_new_enemy_archetypes_move_and_resolve_combat` and `test_wave_progression_and_restart_reset` in `tests/unit/test_combat_and_lifecycle.py`, plus `test_result_menu_button_returns_to_menu` in `tests/integration/test_playable_loop.py`; run only these four node IDs before implementation.

### Implementation for User Story 5

- [X] T012 [P] [US5] Define localized names and centralized HP, speed, bite-damage, bite-interval, and contact-distance values for `zombie_fast` and `zombie_tough`, and validate their required fields and ranges in `assets/config/balance.json` and `src/pvz_game/config.py`.
- [X] T013 [P] [US5] Add three ordered, progressively stronger waves and attach each scheduled spawn to a valid wave ID in `assets/levels/day_01.json`.
- [X] T014 [US5] Track scheduled wave state/events in snapshots, spawn all configured archetypes using their own stats, reset wave progress, and preserve the existing final-spawn-plus-no-living-zombies victory rule in `src/pvz_game/domain/models.py`, `src/pvz_game/domain/simulation.py`, and `src/pvz_game/domain/systems.py` (depends on T012–T013).
- [X] T015 [US5] Map variant IDs to the existing zombie animation role for idle/walk/bite/hit/death, add lightweight speed/armor visual cues and nonblocking wave announcements/HUD progress, and ensure all variants still face left in `src/pvz_game/presentation/skin_catalog.py`, `src/pvz_game/presentation/animation.py`, `src/pvz_game/presentation/renderer.py`, and `src/pvz_game/presentation/scenes.py`; include wave fields in deterministic benchmark snapshots in `src/pvz_game/presentation/performance.py` (depends on T014).

**Checkpoint**: One existing level includes all three recognizable enemy types and at least three announced waves; balance remains configurable and the core win/loss/restart loop works.

---

## Phase 7: User Story 4 - 在外观选择中找到胖宝宝和黄黄 (Priority: P2)

**Goal**: Add separately clickable, preview-only appearance entries for 胖宝宝·土豆雷 and 黄黄·寒冰射手 without changing in-game skin selection or plant roles.

**Independent Test**: Open the appearance menu, focus each preview and verify its name/art/role label; enter a game and confirm the existing dog look and both gameplay roles remain unchanged.

### Tests for User Story 4

- [X] T016 [US4] Add `test_special_dog_plant_roles_are_shown_in_skin_menu` to `tests/integration/test_skin_selection.py`; verify separate labels, preview-only focus behavior, and unchanged global skin/plant-role selection, and run only this node ID before implementation.

### Implementation for User Story 4

- [X] T017 [US4] Add separate clickable preview-only entries and a renderer-owned preview-focus state for `pangbaobao` and `huanghuang`; clicking them must not alter the active global skin or plant-role mapping in `src/pvz_game/presentation/scenes.py`, `src/pvz_game/presentation/input.py`, and `src/pvz_game/presentation/renderer.py`.
- [X] T018 [US4] Reuse asynchronous dog-atlas preloading and show a lightweight loading placeholder until role previews are ready; keep the appearance menu responsive and avoid synchronous atlas decoding in `src/pvz_game/app.py`, `src/pvz_game/presentation/skin_catalog.py`, and `src/pvz_game/presentation/renderer.py` (depends on T017).

**Checkpoint**: Both dog-only role previews can be selected independently in the appearance menu and remain bound to their original gameplay duties; existing appearance choices still work.

---

## Phase 8: Polish & Playable Release

**Purpose**: Run the smallest required acceptance set, make one official playable directory package, and remove only this run’s staging artifacts.

- [X] T019 Update the application/package version and user-facing version label to `0.6.0` in `src/pvz_game/__init__.py`, `pyproject.toml`, `src/pvz_game/presentation/renderer.py`, `packaging/pvz_game.spec`, `tools/build.ps1`, and `packaging/开始游戏.txt`.
- [X] T020 Run exactly the 13 targeted node IDs documented in `specs/010-dog-gameplay-polish/quickstart.md`, then run `tools/validate_assets.py`; record actual results in `docs/validation/010/targeted-checks.md`.
- [X] T021 Run one 10-second standard-window measurement with `tools/benchmark.py --window --scene standard --seconds 10 --plant-skin dogs --zombie-skin dogs --output docs/validation/010/performance.json` and save the result in `docs/validation/010/performance.json`.
- [X] T022 Build one `PvzMiniGame-v0.6.0` directory package with the PyInstaller command in `specs/010-dog-gameplay-polish/quickstart.md`, copy the existing guide/license, then run one dog-cartoon packaged smoke and save its screenshot/result in `docs/validation/010/release-smoke.png` and `docs/validation/010/release-report.md`.
- [X] T023 Remove only `build/PvzMiniGame-v0.6.0/` staging created by this build, verify the official `dist/PvzMiniGame-v0.6.0/` package remains, and record that no ZIP was generated in `docs/validation/010/release-report.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No initialization required; the repository, runtime and packaging layout already exist.
- **Foundational (Phase 2)**: No separate migration or shared framework task; existing Simulation/snapshot/input/render boundaries are reused.
- **User Stories**: Implement and integrate sequentially in this order: US1 → US2 → US3 → US5 → US4. All are independently verifiable, but US1/US2/US3/US5/US4 share `animation.py`, `renderer.py`, or `systems.py`, so avoid parallel cross-story edits.
- **Polish (Phase 8)**: Depends on all five stories; T019–T023 run sequentially.

### User Story Dependencies

- **US1 (P1)**: No logic dependency; establishes role bounds and left-facing rendering.
- **US2 (P1)**: Reuses the current producer and snapshot animation path; can follow US1 to avoid competing Renderer edits.
- **US3 (P1)**: Reuses existing placement validation and is sequenced after US2 because both adjust drawing/input feedback.
- **US5 (P1)**: Extends the same simulation/renderer used by US1–US3; wave state depends on the new config and level schedule (T012–T013 before T014).
- **US4 (P2)**: Reuses loaded dog manifests and shares the skin-menu Renderer paths; implement after US5.

### Parallel Opportunities

- T002 (manifest tuning) and T003 (cached frame mirroring) may run in parallel after T001 because they edit different files.
- T012 (enemy balance/schema) and T013 (level schedule) may run in parallel after T011 because they edit separate files; T014 waits for both.
- T010 follows T009 because presentation consumes the established drag state; do not mark or schedule these dependent tasks in parallel.
- Do not run separate story implementation tasks in parallel because they share renderer/simulation modules.

## Parallel Example: Independent Foundation Changes

```text
Task T002: Tune only dog skin manifest display scales.
Task T003: Add cached left-facing actor frame rendering.

Task T012: Add zombie archetype balance and validation.
Task T013: Add the three-wave level schedule.
```

## Implementation Strategy

### MVP First

1. Implement P1 visual, sun, drag, and wave stories (US1, US2, US3, US5) while preserving the 0.5.0 core loop.
2. Complete the P2 appearance-page previews (US4) before packaging the requested complete feature.
3. Run the exact 13 targeted tests and one asset validation; no full test suite or pressure matrix.
4. Measure one 10-second standard window, build one `v0.6.0` directory package, smoke it once, and remove only this build’s staging directory.

### Incremental Delivery

1. US1: complete, proportionate dog bodies and correct zombie facing.
2. US2: body-origin sunshine hop with synchronized hit position.
3. US3: continuous drag preview and deterministic nearest-cell release.
4. US5: three enemy archetypes and escalating waves in the existing level.
5. US4: independent special-role previews in the appearance menu.
6. Release: focused acceptance, package, smoke, cleanup, and report.

### Notes

- Every task uses the required checkbox, sequential task ID, story label where required, and concrete file path.
- [P] is reserved for work on distinct files whose prerequisites are complete.
- Exact test node IDs are centralized in `quickstart.md`; no unrelated suite or ZIP build is included.
- The user requested the Windows desktop target; no Android or iOS tasks are in scope.







