# Quickstart: 验证 010 狗狗外观与玩法优化

本清单只运行此次功能直接相关的验证。使用仓库现有 `.venv` 和测试夹具；不要执行全量 pytest 或压力场景矩阵。

## 先决条件

- Windows 工作目录为项目根目录 `Plants vs Zombies`。
- `.venv/Scripts/python.exe` 已安装项目与开发依赖。
- 新增/改写的定向用例已按 `$speckit-tasks` 放入下列现有测试模块。

## 必要定向检查

```powershell
.venv/Scripts/python.exe -m pytest -q `
  tests/unit/test_config_and_models.py::test_wave_and_enemy_configuration_validates `
  tests/unit/test_combat_and_lifecycle.py::test_new_enemy_archetypes_move_and_resolve_combat `
  tests/unit/test_combat_and_lifecycle.py::test_wave_progression_and_restart_reset `
  tests/integration/test_playable_loop.py::test_result_menu_button_returns_to_menu `
  tests/integration/test_drag_input.py::test_drag_preview_tracks_pointer_continuously `
  tests/integration/test_drag_input.py::test_nearest_cell_tiebreak_and_invalid_rejection_without_cost `
  tests/integration/test_animation.py::test_dog_zombie_faces_left_in_all_actor_states `
  tests/integration/test_animation.py::test_adjusted_dog_roles_fit_all_visible_frames `
  tests/integration/test_playable_loop.py::test_sunflower_sun_hops_from_visible_body_and_tracks_click `
  tests/integration/test_playable_loop.py::test_sun_expiry_remains_based_on_creation_tick `
  tests/integration/test_skin_selection.py::test_special_dog_plant_roles_are_shown_in_skin_menu `
  tests/replay/test_base_replay.py::test_actual_level_is_winnable_and_replay_is_fps_independent `
  tests/replay/test_base_replay.py::test_actual_undefended_level_loses_then_restarts
```

这 13 个 node ID 覆盖配置/波次与敌人规则、拖放连续性/最近格/tie-break/无效释放、角色边界/朝向、被窝阳光起点、外观入口，以及真实关卡胜利/失败/重开和结果页返回菜单；新用例在实现任务中加入。不运行这些模块的其他无关用例，也不运行全量测试。

素材清单边界和引用只额外运行一次：

```powershell
.venv/Scripts/python.exe tools/validate_assets.py
```

## 一次帧时间验收

```powershell
.venv/Scripts/python.exe tools/benchmark.py --window --scene standard --seconds 10 --plant-skin dogs --zombie-skin dogs --output docs/validation/010/performance.json
```

预期：10 秒标准窗口下 P95 间隔不超过 20 ms，且无超过 100 ms 的非预期停顿。使用真实显示路径，只测一次，不执行压力矩阵。

## 构建并 smoke 正式目录包

完成版本号更新后，在项目根目录执行一次目录构建；不调用包含全量 pytest 和 ZIP 步骤的 `tools/build.ps1`：

```powershell
$env:PVZ_DIAGNOSTIC = '0'
$env:PVZ_OUTPUT_NAME = 'PvzMiniGame-v0.6.0'
.venv/Scripts/python.exe -m PyInstaller --noconfirm --clean --distpath dist --workpath build/PvzMiniGame-v0.6.0 packaging/pvz_game.spec
.venv/Scripts/python.exe tools/copy_release_files.py --artifact-name PvzMiniGame-v0.6.0
```

运行 `dist/PvzMiniGame-v0.6.0/PvzMiniGame.exe` 一次，并使用 smoke 参数进入一局狗狗卡通外观，确认卡片和敌人渲染、运行帧与结果流程无启动错误，返回菜单由上述定向回归确认。保存一张对局截图及简短报告至 `docs/validation/010/`。完成后只删除 `build/PvzMiniGame-v0.6.0/` staging；保留正式 `dist/PvzMiniGame-v0.6.0/`，本功能不生成 ZIP。

从项目根目录运行包内 smoke（GUI EXE 用 `Start-Process -Wait` 获取真实退出码）：

```powershell
New-Item -ItemType Directory -Force -Path docs/validation/010 | Out-Null
$exe = (Resolve-Path dist/PvzMiniGame-v0.6.0/PvzMiniGame.exe).Path
$shot = Join-Path $PWD 'docs/validation/010/release-smoke.png'
$arguments = "--smoke-frames 8 --smoke-play --plant-skin dogs --zombie-skin dogs --screenshot `"$shot`""
$process = Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $PWD -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0 -or -not (Test-Path $shot)) { throw 'Packaged game smoke failed' }
```


