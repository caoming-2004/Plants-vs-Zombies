# v0.5.0 可玩版本验收

- 正式发行目录：`dist/PvzMiniGame-v0.5.0/`。保留可运行程序 `PvzMiniGame.exe`（2,083,698 字节）、游戏说明和字体许可；该目录随附所需 `_internal` 资源。
- 发行版冒烟启动通过：无控制台窗口运行打包 EXE，分别加载并渲染 `dogs` 对局（2 帧）与 `dogs_photo` 对局（8 帧），两个进程退出码均为 0。
- 截图证据：[卡通狗狗对局](playable-smoke-dogs.png)、[照片狗狗对局](playable-smoke-dogs_photo.png)。照片狗狗截图画面正常，角色完整显示；两种外观的图像也通过打包后的资源路径加载。
- 目标回归通过：定向用例 `50 passed`，包含 `tests/replay/test_base_replay.py` 可赢关卡及重开；完整狗狗素材检查通过，经典、`dogs`、`dogs_photo` 三套资源引用有效。
- 性能记录：标准窗口 10.014 秒、62.31 FPS、P95 帧间隔 16.01 ms；开始到目标画面 42.23–59.60 ms，打开换肤页 33.42–54.69 ms。换肤确认立即响应，照片图集在后台约 568–603 ms 就绪；详见本目录 `performance-check.md`。
- 清理：已删除本轮生成的 PyInstaller staging 目录 `build/PvzMiniGame-v0.5.0/`（含中间测试 EXE）。本轮未生成 ZIP，因此没有 ZIP 测试件需要删除。正式发行目录保留；其他已有发行文件未动。

运行：打开 `dist/PvzMiniGame-v0.5.0/开始游戏.txt` 查看说明，并从该发行目录启动 `PvzMiniGame.exe`；请保持 `_internal` 文件夹与 EXE 同级。
