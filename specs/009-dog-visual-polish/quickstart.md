# Quickstart Validation: 狗狗视觉与阳光动效优化

Run only after implementation. From the project root in PowerShell:

## 1. Focused rules and input regression

```powershell
.venv/Scripts/python.exe -m pytest -q tests/unit/test_new_plant_rules.py tests/integration/test_drag_input.py tests/integration/test_animation.py tests/integration/test_playable_loop.py
```

Expected: mine arming/trigger/single explosion, Snow Pea damage/slow/expiry, existing placement/cards, actor rendering and core loop pass.

## 2. Assets and dog silhouettes

```powershell
.venv/Scripts/python.exe tools/validate_assets.py
```

Expected: all supported skins validate; every dog role present in `dogs` and `dogs_photo` has alpha silhouettes fitting the canvas in idle, maximum reach and lying poses; 被窝 is visibly smaller than its corresponding previous build in both skins. New roles remain dog-cartoon-only.

## 3. Standard-window responsiveness

```powershell
.venv/Scripts/python.exe tools/benchmark.py --window --seconds 10 --scene standard --plant-skin dogs --zombie-skin dogs --output docs/validation/009/window-benchmark.json
```

Expected: most frame intervals ≤20 ms and no unexplained interval >100 ms. Repeat start/skin-switch 10 times; use timestamped 60fps screen capture (count frames from click to first target-scene frame) or runtime monotonic timestamps. Record the measurement method and all 10 results; each must be ≤500 ms.

## 4. One full game and playable package smoke

Run the existing replay/winnability check once and launch the packaged EXE with its standard smoke option. Confirm a full resource/plant/combat/result/restart cycle, all core plant cards, dog visuals, and collectible animated sun. Record exact command/results in `docs/validation/009/release-report.md`.

Do not run unrelated load/stress suites. Delete only test-generated EXE/ZIP files created for this validation; retain the official playable package.
