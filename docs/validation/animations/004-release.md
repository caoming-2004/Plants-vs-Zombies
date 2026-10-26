# 004 Windows 发行验证

日期：2026-10-26；平台：Windows 11 x64。

- 构建命令：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1`；退出码 0。
- 构建内自动验证：113 pytest passed；default 538、dogs 571 引用帧，素材姿势速率及角色轮廓验证通过。
- 发行包：`dist/PvzMiniGame-windows-x64.zip`；SHA-256 `942d13b0ba0247af0884a98fc65ba7bd9a3e3b986acb3c42099e052622dd2e0b`。
- 验证命令：`.venv/Scripts/python.exe tools/verify_bundle.py`；退出码 0。ZIP 解压到不同目录，在子进程不含 Python 的 PATH 下启动成功。
- `default/default`、`dogs/default`、`default/dogs`、`dogs/dogs` 四种对局 smoke 均退出码 0；dogs 外观菜单 smoke 退出码 0。
- 冒烟测试为 SDL dummy/headless 进程启动检查，不声称替代真实鼠标试玩；此版本可双击 EXE 目录内的 `PvzMiniGame.exe` 启动。
- 使用说明随包附带 `开始游戏.txt` 和 `字体许可.txt`。
