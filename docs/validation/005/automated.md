# 005 自动化验证

## 聚焦测试记录

```powershell
.venv/Scripts/python.exe -m pytest -q tests/integration/test_skin_selection.py tests/integration/test_background_layout.py tests/unit/test_performance.py tests/integration/test_asset_manifest.py tests/integration/test_animation.py tests/replay/test_base_replay.py tests/replay/test_skin_invariance.py
```

最终结果：47 passed in 131.10s。

完整发行构建命令 `.\tools\build.ps1 -ArtifactName PvzMiniGame-v0.3.0`：121 passed in 157.58s；紧随其后的 `.venv/Scripts/python.exe tools/validate_assets.py` 校验 default 538、dogs 587、dogs_photo 539 个引用帧均有效，动作符合12–18不同姿势/秒。PyInstaller Windows x64 构建与 v0.3.0发行包生成成功。

搬迁目录离线启动检查：`.venv/Scripts/python.exe tools/verify_bundle.py --archive dist/PvzMiniGame-v0.3.0-windows-x64.zip --app-name PvzMiniGame-v0.3.0`；7/7 经典、卡通、照片外观组合及照片选肤菜单 smoke 均退出码0。

遮挡校验：dogs 最坏0%，dogs_photo 最坏1.44%。`git diff --check` 通过。上述 smoke 使用 SDL dummy，不能替代真人窗口操作及20次输入反馈测量。
