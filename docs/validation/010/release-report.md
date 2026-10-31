# v0.6.0 可玩目录包验收

- PyInstaller 目录构建：通过，生成 `dist/PvzMiniGame-v0.6.0/PvzMiniGame.exe`。
- 随包文件：已复制 `开始游戏.txt` 与 `字体许可.txt`。
- 打包 smoke：退出码 0；以狗狗卡通外观运行 8 帧并成功生成 `release-smoke.png`。截图中可见六张植物卡、狗狗僵尸和对局 HUD。
- 性能测量：10.009 秒、平均 62.04 FPS、P95 帧间隔 16.03 ms、最大帧间隔 85.438 ms；未出现超过 100 ms 的帧间隔。基准工具因没有提供首版 FPS 基线，将汇总状态标为 `INCONCLUSIVE`；本次功能的帧时间和平均 FPS 门槛通过。
- ZIP：本轮没有生成 ZIP。
- 清理：完成 smoke 后删除本轮 `build/PvzMiniGame-v0.6.0/` staging；保留正式 `dist/PvzMiniGame-v0.6.0/` 可玩目录包。
