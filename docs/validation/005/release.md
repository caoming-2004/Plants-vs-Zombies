# 005 发行验收

## 正式发行包

- 构建命令：`powershell -ExecutionPolicy Bypass -File tools/build.ps1 -ArtifactName PvzMiniGame-v0.3.0`。全量测试 121 passed，素材验证 default 538、dogs 587、dogs_photo 539 个引用帧均有效，动作节奏满足12–18姿势/秒；PyInstaller Windows x64 构建成功。
- 新包：[`PvzMiniGame-v0.3.0-windows-x64.zip`](../../../dist/PvzMiniGame-v0.3.0-windows-x64.zip)，SHA-256 `3823a417f1d662cdf589dd6fc8b9528c1b1747afe11e5c176e0453a6375939ec`。
- 验证命令：`.venv/Scripts/python.exe tools/verify_bundle.py --archive dist/PvzMiniGame-v0.3.0-windows-x64.zip --app-name PvzMiniGame-v0.3.0`。包已解压到带空格和中文的独立目录；子进程 PATH 不含 Python，代理指向不可达本地端口。default/dogs/dogs_photo 植物皮肤分别与 default/dogs 僵尸皮肤组合启动成功，照片选肤菜单启动成功，7/7 均退出码0并生成截图。详见 [`bundle-smoke.json`](../bundle-smoke.json)。
- `开始游戏.txt` 与字体许可已随包加入；保留用户正在运行的 v0.2.0 目录和窗口，新包使用独立目录/版本名。

## 尚待真人窗口验收

- `verify_bundle.py` 使用 SDL dummy，不是可见实机窗口或操作系统级网络隔离。它没有验证真人完整胜负、暂停/重开、20次拖放/铲除/收集、或在1050×600、1260×720、1920×1080真实窗口内操作。
- T004 原版打包基线、T025 真人输入反馈测量及T026同条件旧版对比因此保持未完成。性能报告中另有本功能 T024 前的打包标准样本，可看优化变化，但不能冒充原版基线。
- 新版标准和压力场景60秒窗口测量通过帧率目标，详见 [`performance.md`](performance.md)。
