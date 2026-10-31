# Quickstart: 006 视觉与流畅度验证

以下操作针对 Windows PowerShell 与项目现有 .venv。除构建第一版基线的步骤外，命令从仓库根目录运行。真人输入步骤要求测试者在游戏窗口可见时手动操作。

## 1. 检查现有核心回归

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools/validate_assets.py
~~~

预期：自动化测试通过；默认、卡通和照片素材都可加载，必要动作时长/姿势速率、帧锚点和狗狗遮挡检查通过。

## 2. 检查视觉资产与导出动作预览

~~~powershell
New-Item -ItemType Directory -Force docs/validation/006 | Out-Null
~~~

保存不同尺寸的同一关卡画面：

~~~powershell
.\.venv\Scripts\python.exe -m pvz_game --smoke-play --smoke-frames 1 --screenshot docs/validation/006/background-1050.png --window-size 1050x600
.\.venv\Scripts\python.exe -m pvz_game --smoke-play --smoke-frames 1 --screenshot docs/validation/006/background-1260.png --window-size 1260x720
.\.venv\Scripts\python.exe -m pvz_game --smoke-play --smoke-frames 1 --screenshot docs/validation/006/background-1920.png --window-size 1920x1080
.\.venv\Scripts\python.exe -m pvz_game --smoke-play --smoke-frames 1 --screenshot docs/validation/006/background-1050-photo.png --window-size 1050x600 --plant-skin dogs_photo
.\.venv\Scripts\python.exe -m pvz_game --smoke-play --smoke-frames 1 --screenshot docs/validation/006/background-1260-photo.png --window-size 1260x720 --plant-skin dogs_photo
.\.venv\Scripts\python.exe -m pvz_game --smoke-play --smoke-frames 1 --screenshot docs/validation/006/background-1920-photo.png --window-size 1920x1080 --plant-skin dogs_photo
~~~

导出各动作预览：

~~~powershell
New-Item -ItemType Directory -Force docs/validation/006/previews | Out-Null
.\.venv\Scripts\python.exe tools/preview_animations.py --export docs/validation/006/previews
~~~

检查 default、dogs、dogs_photo 的全部角色动作接触表和姿势条。另以开发窗口分别在 1050×600、1260×720、1920×1080 保存相同白天关卡；输出目标见 contracts/packaged-validation-report.md。核对首版房屋/道路/草坪/种植区位置，角色身份、面部/毛色细节、脚底锚点、杂边和裁切。

## 3. 构建诊断发行包

~~~powershell
.\tools\build.ps1 -Diagnostic -ArtifactName PvzMiniGame-visual-quality
~~~

预期：构建脚本先运行回归测试与素材验证，诊断包包含窗口性能及操作采样选项。最终验收必须使用新背景、新狗狗图集集成后的最终打包版重测。

## 4. 记录实机帧率

先使用隔离目录内从 `7305e3d` 构建的第一版打包程序采集同机基线（1260×720、当前90Hz刷新率、每场景60秒）：

~~~powershell
$baselineExe = (Resolve-Path .tools/feature-006-baseline/dist/PvzMiniGame-v0.2.0/PvzMiniGame.exe).Path
& $baselineExe --benchmark-scene standard --seconds 60 --benchmark-output (Join-Path (Resolve-Path docs/validation/006).Path baseline-standard-raw.json)
& $baselineExe --benchmark-scene pressure --seconds 60 --benchmark-output (Join-Path (Resolve-Path docs/validation/006).Path baseline-pressure-raw.json)
.\.venv\Scripts\python.exe tools/normalize_baseline_report.py --input docs/validation/006/baseline-standard-raw.json --output docs/validation/006/baseline-standard.json --refresh-rate-hz 90 --display-driver windows --display-size 1600x1000
.\.venv\Scripts\python.exe tools/normalize_baseline_report.py --input docs/validation/006/baseline-pressure-raw.json --output docs/validation/006/baseline-pressure.json --refresh-rate-hz 90 --display-driver windows --display-size 1600x1000
~~~

原始结果经慢帧统计补充后保存为 `baseline-standard.json` 和 `baseline-pressure.json`。standard 运行前从第一版标准报告读取 average_fps，并将其传给诊断包：

~~~powershell
$baselineAverageFps = (Get-Content docs/validation/006/baseline-standard.json | ConvertFrom-Json).average_fps
dist/PvzMiniGame-visual-quality/PvzMiniGame.exe --benchmark-scene standard --seconds 60 --baseline-average-fps $baselineAverageFps --benchmark-output docs/validation/006/packaged-standard.json
dist/PvzMiniGame-visual-quality/PvzMiniGame.exe --benchmark-scene pressure --seconds 60 --benchmark-output docs/validation/006/packaged-pressure.json
~~~

分别在实际显示窗口记录 standard 与 pressure 场景。标准场景5株向日葵、5株豌豆射手、5只僵尸、10个投射物、3个阳光、5台割草机；压力场景23株向日葵、22株豌豆射手、30只僵尸、100个投射物、20个阳光、5台割草机。标准场景目标为平均循环帧率≥58 FPS且≥第一版的97%、P95≤18ms；压力场景P95≤20ms；两者连续两帧以上>33ms的次数必须为0。实测不得使用 SDL dummy 结果替代。

## 5. 手动输入反馈与基线比较

~~~powershell
dist/PvzMiniGame-visual-quality/PvzMiniGame.exe --input-latency --seconds 60
~~~

在窗口可见期间完成至少20次有效的种植拖放、铲除、阳光收集。保存 JSON 输出，并与从 7305e3d 构建的第一版在同一电脑、窗口和显示刷新率下的帧率结果并列。若显示器刷新率低于60Hz，记录限制后再判断结果；不可把基准包的诊断改动混入游戏行为。

## 6. 确定性回放对照

分别在 `7305e3d` 隔离源码和当前源码根目录执行同一回放命令。基线目录中的测试确认冻结快照可在原版重现；当前目录中的测试确认新版与同一快照一致：

~~~powershell
$projectRoot = (Get-Location).Path
$env:PYTHONPATH = Join-Path $projectRoot '.tools/feature-006-baseline/src'
Push-Location .tools/feature-006-baseline
& "$projectRoot\.venv\Scripts\python.exe" -m pytest tests/replay/test_base_replay.py -q
Pop-Location
Remove-Item Env:PYTHONPATH

.\.venv\Scripts\python.exe -m pytest tests/replay/test_base_replay.py -q
~~~

分别保存两次运行的事件类型/tick、最终胜负、阳光、击杀数和割草机状态，并将逐项对照写入 `docs/validation/006/replay.md`。预期事件序列及列出的终态字段一致；若有差异，保留证据并先定位原因。任一版本无法读取冻结基准或无法执行时，回放比较状态记为 `INCONCLUSIVE`，不得判定通过。

## 7. 离线发行回归

~~~powershell
.\tools\build.ps1 -ArtifactName PvzMiniGame-visual-quality-release
.\.venv\Scripts\python.exe tools/verify_bundle.py --archive dist/PvzMiniGame-visual-quality-release-windows-x64.zip --app-name PvzMiniGame-visual-quality-release
~~~

然后断开网络启动，检查菜单、背景、两类狗狗外观、开始/暂停/恢复/重开和核心对局；最终实际结果写入 `docs/validation/006/release.md`。失败、未能执行或环境受限必须保持为失败/未验证状态。
