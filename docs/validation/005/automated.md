# 005 自动化验证

## 聚焦测试记录

最终聚焦命令：

```powershell
.venv/Scripts/python.exe -m pytest -q tests/integration/test_skin_selection.py tests/integration/test_background_layout.py tests/unit/test_performance.py tests/integration/test_asset_manifest.py tests/integration/test_animation.py
```

最终结果：43 passed in 58.36s。全量 `.venv/Scripts/python.exe -m pytest -q` 结果：120 passed in 163.21s。

资源验证 `.venv/Scripts/python.exe tools/validate_assets.py` 结果：default 538、dogs 587、dogs_photo 539个引用帧均有效，动作符合12–18不同姿势/秒。双狗皮肤最坏遮挡率为dogs 0%、dogs_photo 1.44%。

`git diff --check` 通过。编辑器静态问题检查未报告语法或类型错误。以上自动化结果不替代真实窗口截图、人工视觉验收、发行包验证或实机性能与输入测量。
