# Quickstart: 视听优化验证

Run from the repository root in PowerShell. Use the existing Python 3.12 environment.

## Minimal focused checks

1. Validate bundled asset references and background metadata:

   ```powershell
   .venv/Scripts/python.exe tools/validate_assets.py
   .venv/Scripts/python.exe -m pytest tests/unit/test_backgrounds.py tests/integration/test_background_layout.py
   ```

2. Verify legacy/new preference defaults and persistence, plus music scene transitions and missing-device fallback. Run only the directly affected unit and integration test files named in `tasks.md`; do not run the full test suite.

3. Confirm the standard window render still meets its 60 FPS acceptance. `tools/benchmark.py` must use the same window-scaling function as `src/pvz_game/app.py`, so this measures the actual display path:

   ```powershell
   .venv/Scripts/python.exe tools/benchmark.py --window --scene standard --seconds 15 --output docs/validation/014/standard-performance.json
   ```

4. Build and verify a fresh Windows directory artifact using a unique artifact name:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File packaging/windows/build.ps1 -ArtifactName PvzMiniGame-visual-audio
   .venv/Scripts/python.exe packaging/windows/verify_bundle.py --artifact-name PvzMiniGame-visual-audio --screenshot docs/validation/014/windows/desktop-smoke.png
   ```

5. Launch the new directory bundle and perform one brief desktop pass at 1050×600 and 1920×1080: check font clarity, layout and background legibility; open settings, adjust/disable music, start a level, pause/resume, finish a victory and defeat path if quickly reachable, then restart and confirm music/background preferences persist.

## Expected result

- Asset validation and focused checks pass; no unrelated full-suite run is required.
- Standard render meets average ≥58 FPS, p95 frame interval ≤18 ms, and existing no-consecutive-slow-frame gate.
- Fresh offline directory build launches with music/assets bundled; if the audio device is unavailable, silent play remains functional.
