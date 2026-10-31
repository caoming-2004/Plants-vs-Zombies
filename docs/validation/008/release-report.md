# 可玩版本发布验收

## 结果

- 正式目录：`dist/PvzMiniGame-v0.4.0/`；入口：`PvzMiniGame.exe`。发行说明与字体许可已随包保留。
- 正式 EXE 大小：2,074,650 bytes；完整目录：251,794,528 bytes。
- 正式包启动烟测：退出码 0；狗狗植物/狗狗敌方外观，8 帧可玩场景成功渲染并保存截图：[release-smoke.png](release-smoke.png)。
- 必要回归：新增植物、卡片输入、资源清单、动画、可玩流程 60 项通过；完整关卡胜利/帧率独立性/重开 1 项通过；三套皮肤素材校验通过。
- 真窗口标准场景 10 秒：62.26 FPS、P95 16.03 ms、最长连续 >33ms 帧 1；姿态素材逐循环核对为 12 姿态/秒。

## 临时测试文件清理

- 清理前本轮 staging：`build/PvzMiniGame-v0.4.0/pvz_game/PvzMiniGame.exe`（PyInstaller 中间 EXE，2,074,650 bytes）。
- 清理后 staging 目录已删除，未保留测试 EXE。
- 本轮没有生成 ZIP；清理后 `dist/` 下 ZIP 数量为 0。
- `dist/PvzMiniGame-v0.4.0/PvzMiniGame.exe` 是正式可玩包，按要求保留；其他已有发行目录未改动。

人工鼠标延迟没有单独量化；输入与拖放路径由针对性自动化检查覆盖。
