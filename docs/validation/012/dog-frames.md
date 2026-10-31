# 012 狗狗完整轮廓验收

**结果：通过（2026-10-31）**

- 使用 `tools/import_dog_assets.py` 的整张图连通轮廓路径重新提取被窝、嗷嗷嗷和狗狗照片版被窝：每张源图 12 个主体连通体，按 4×3 行/列排序，不再按等分格切块。
- 每帧 256×256，可见内容距边界至少 8 像素，脚底基线 232；provenance 记录 12 个源姿态 bbox 与提取方式。
- 重新生成 `assets/skins/dogs/atlas-005.png`、`manifest.json`、`provenance.json` 和 `assets/sources.json`，同步 dogs_photo 的被窝素材；其他狗狗角色保持原导入路径。
- 实测：`tools/validate_assets.py` 通过（campaign 5 关、dogs 372 帧、dogs_photo 316 帧）。
- `pytest tests/integration/test_animation.py -q`：**17 passed**，包含完整轮廓比例和帧边界检查。
- 运行 `python -m pvz_game --smoke-play --plant-skin dogs --zombie-skin dogs`，截图确认被窝/嗷嗷嗷的脚掌、腿和尾巴完整（`docs/validation/012/play-smoke.png`）。
- 卡片、菜单、地图、拖动预览和倒地姿态由 animation/asset 定向检查覆盖；被窝与嗷嗷嗷在两套外观中均已检查。
