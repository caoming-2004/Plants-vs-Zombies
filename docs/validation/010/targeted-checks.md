# Feature 010 targeted acceptance results

Date: 2026-10-30

## Required checks

- Focused pytest set: **PASS**, 13 selected node IDs passed (`13 passed in 22.61s`). No unrelated tests or full suite were run.
- Asset validation: **PASS**. `tools/validate_assets.py` reported valid manifests and referenced frames for `default`, `dogs`, and `dogs_photo`; pose cadence remained within the validator's reported ranges.
- Standard-window benchmark: **PASS for feature frame-time gates**. 10.009 s, 621 frames, average 62.04 FPS, P95 frame interval 16.03 ms, longest consecutive run over 33 ms: 1 frame. No interval exceeded 100 ms.

The benchmark tool reports overall `INCONCLUSIVE` because no first-version average-FPS baseline was supplied; the measured average FPS and frame-time checks required by this feature passed. The first benchmark launch exposed missing wave fields in its deterministic scene snapshot; those fields were added, and the successful measurement above is the recorded run.

## Scope

Only the required focused tests, asset validator, and one 10-second standard-window measurement were run. No full pytest suite, pressure matrix, or ZIP build was run.
