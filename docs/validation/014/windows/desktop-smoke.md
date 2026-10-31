# Windows 视听版本验收记录

日期：2026-10-31  
交付目录：`dist/windows/PvzMiniGame-visual-audio-release/`

## 已完成

- 使用 `packaging/windows/build.ps1` 构建 Windows 目录包；字体许可、三种背景、三首音乐及来源清单已随包提供。
- `packaging/windows/verify_bundle.py` 离线运行包内程序 8 帧并生成对局截图 `desktop-smoke.png`；退出码为 0。
- 从打包程序分别生成 1050×600 和 1920×1080 菜单截图，见 `menu-1050x600.png` 与 `menu-1920x1080.png`。两张截图均显示写实草坪背景；菜单文字和音乐控件完整可读。
- 定向检查：11 项通过；`tools/validate_assets.py` 通过，确认背景尺寸/哈希、音乐来源/哈希及角色资源有效。
- 15 秒标准窗口基准通过：平均 60.96 FPS、P95 帧间隔 16.02 ms、最长连续超过 33 ms 的帧数为 1；相同环境基准为 62.04 FPS。

## 交互验收边界

原生 Windows 窗口观察过程中，用户按 Esc 停止了 Computer Use。按该指示未继续进行鼠标交互；因此本记录不声称已在真实窗口点击切换背景、调整音乐、完成胜利结算或重启验证。音乐场景转换、单次胜利提示、静音降级和设置保存/恢复已由定向单元检查覆盖。
