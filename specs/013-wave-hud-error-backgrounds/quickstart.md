# Quickstart Validation: 波次 HUD、通关稳定性与高清背景

**Feature**: `013-wave-hud-error-backgrounds` | **Date**: 2026-10-31

只验证本次改动必要的路径：HUD 不遮挡、第一关结算/下一关、三套高清背景、偏好回退和 Windows 包启动。不跑全量 pytest、外观矩阵或安卓。

## 环境

```powershell
.\.venv\Scripts\python.exe -m pvz_game --smoke-frames 5
```

预期：菜单正常打开，无资源错误。

## 1. HUD 状态条

```powershell
.\.venv\Scripts\python.exe -m pvz_game --window-size 1050x600 --smoke-play --smoke-frames 30 --screenshot docs\validation\013\hud-1050.png
.\.venv\Scripts\python.exe -m pvz_game --window-size 1920x1080 --smoke-play --smoke-frames 30 --screenshot docs\validation\013\hud-1920.png
```

检查：

- 状态条在草坪上方，矩形与草坪 `(105,160,864,380)` 不相交。
- 关卡名、波次、出怪进度、下一波预告完整可读；卡片/铲子/暂停不重叠。
- 第 1 行植物、阳光、僵尸没有被任何波次文字覆盖。
- 下一波预告的敌人类型/数量/主要行与实际出怪一致，且至少提前 2 秒出现；切换后无旧预告残留。
- 长“最后一波”/长关卡名不越界。
- 如果 `--smoke-play` 不能显示预告阶段，再正常启动并等待第 1 波，截图补证。

## 2. 第一关结算与下一关

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration/test_hud_layout.py tests/integration/test_result_flow.py -q
```

预期：

- 连续 20 次第一关结算，未处理异常/错误弹窗/进程退出为 0。
- “下一关/再玩一局/返回主菜单/退出”均可完成；day_02 使用全新状态。
- 同一局只保存一次；day_02 解锁 100%；重启后保留。
- 只读/损坏 progress、缺失 day_02 时提示且可返回菜单/重试。

再实际启动游戏通关第一关一次，点击“下一关”，确认无报错并进入 day_02；退出重开确认 day_02 仍解锁。

## 3. 高清背景

```powershell
.\.venv\Scripts\python.exe tools\validate_assets.py
.\.venv\Scripts\python.exe -m pytest tests/unit/test_backgrounds.py -q
```

预期：

- `assets/backgrounds/manifest.json` 通过：3 套 day/night/dusk，源图≥2560×1440，文件存在/SHA 匹配，作者/来源/授权可追溯。
- 主菜单“更换背景”：三张缩略图、名称、当前标记；切换立即生效。
- 1050×600/1920×1080 截图清晰；角色/HUD 可读；只改视觉；三张背景必须是真实感/高级感摄影或写实渲染，不能是幼稚卡通。
- 重启恢复上次选择；临时移除当前背景文件后回退默认并提示；运行期无网络请求。

截图建议：

```powershell
.\.venv\Scripts\python.exe -m pvz_game --window-size 1920x1080 --smoke-frames 30 --screenshot docs\validation\013\backgrounds-1920.png
```

## 4. 回归与性能

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_campaign_config.py tests/unit/test_campaign_progress.py tests/unit/test_endless.py tests/integration/test_campaign_flow.py tests/integration/test_animation.py -q
.\.venv\Scripts\python.exe tools\benchmark.py --window --scene standard --seconds 10 --output docs\validation\013\benchmark.json
```

预期：既有战役/进度/无尽/狗狗检查通过；标准场景平均 ≥58 帧/秒、p95 ≤18 毫秒（dummy 10 秒为快速冒烟，最终以真实窗口 60 秒为准）。

## 5. Windows 包

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File packaging\windows\build.ps1 -ArtifactName PvzMiniGame-v0.7.1
Start-Process -FilePath ".\dist\windows\PvzMiniGame-v0.7.1\PvzMiniGame.exe" -Wait
```

预期：包内 `_internal/pvz_game/assets/backgrounds/` 含三套背景；启动后完成一次第一关结算/下一关、切换一次背景、重启恢复。

## 不执行

全量 pytest、外观矩阵、长时压力、安卓安装/触控/性能、4K/多设备矩阵。
