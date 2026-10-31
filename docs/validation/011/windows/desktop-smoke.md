# Windows 可玩目录包验收

**结果：最终目录包构建通过；自动核心回路 smoke 通过；真实窗口操作未完成。**（2026-10-30）

- 使用 `packaging/windows/build.ps1` 构建到 `dist/windows/PvzMiniGame-v0.6.1/`。构建只运行 `tools/validate_assets.py`，未运行全量 pytest，也没有生成 ZIP。
- 资源校验通过：default 538、dogs 372、dogs_photo 316 个引用帧有效。
- `.venv/Scripts/python.exe packaging/windows/verify_bundle.py`：目录版 EXE 在不含 Python 的子进程 PATH 下，以 `--smoke-play` 启动并退出码 0；截图为 `desktop-smoke.png`。
- EXE：2,089,494 bytes；SHA256 `B50D7F2C6221155FAA7F0F943D6245D8A82D1338CA40F0303B8528139138DB1F`。目录包共 194 个文件，252,363,075 bytes。
- 构建 staging、PyInstaller 缓存和临时 smoke 工作目录均在本次检查后删除；最终目录包保留。

尝试进行一次真实窗口菜单/种植操作时，Windows Computer Use 收到物理 Escape 停止信号；根据该停止信号未继续发送窗口输入。因此本记录不把 headless smoke 等同于真实鼠标试玩，菜单到关卡切换和真实窗口中的种植仍待人工验收。
