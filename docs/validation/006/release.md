# 006 最终发行验收

## 构建与包验证

- 构建命令：`tools/build.ps1 -ArtifactName PvzMiniGame-visual-quality-release`
- 构建结果：121项测试通过（150.53秒）；default/dogs/dogs_photo 资源检查通过；PyInstaller 6.22.3 Windows 11 x64 完成。
- 独立发行包：[PvzMiniGame-visual-quality-release-windows-x64.zip](../../../dist/PvzMiniGame-visual-quality-release-windows-x64.zip)
- ZIP SHA-256：`ca9681f77bab43155e901ecc0e3a31b084043995da16e4e5056997bfa516d903`
- 包完整性/换目录检查：`tools/verify_bundle.py --archive dist/PvzMiniGame-visual-quality-release-windows-x64.zip --app-name PvzMiniGame-visual-quality-release` 通过。发行文件齐全；在隔离工作目录启动，没有 Python 放入子进程 PATH，并将 HTTP(S) proxy 设为不可达本机端口。
- 七种植物/僵尸皮肤组合与照片皮肤菜单均以 exit code 0 启动，生成截图。结果见 [`bundle-smoke.json`](../bundle-smoke.json)，图像在 `docs/validation/` 的 `bundle-*.png`。

该检查是重定位后的 headless SDL 冒烟测试，带不可达代理设置；不是操作系统级断网测试，也不替代真人鼠标操作。

## 核心回归

- 固定输入回放的事件/快照/终态与历史 fixture 完全一致：[回放对照](replay.md)。
- 背景与狗狗两种皮肤的三档窗口布局截图及自动输入映射校验：[背景报告](background.md)、[狗狗报告](dogs.md)。
- 同机窗口标准/压力60秒性能采样均达标：[性能报告](performance.md)。
- 最终手动输入延迟状态：`INCONCLUSIVE`，120秒内没有检测到有效操作（0/20）。可见窗口输入样本：[JSON](input-latency.json)、[控制台原始输出](input-latency-console.txt)。需要用户手动完成种植拖放、铲除和阳光收集后重新采集；目前不能据此确认真人输入 P95 门槛。
- 本次自动测试未执行主菜单完整真人路线（暂停/恢复及实际胜负后重开）；胜负、重开和游戏循环由回归测试覆盖，菜单照片皮肤入口由发行包烟测覆盖。此处记录为未进行真人验收。
