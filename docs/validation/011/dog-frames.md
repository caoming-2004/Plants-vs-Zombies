# 狗狗动作帧验收

**结果：通过**（2026-10-30）

- 只重建 `dogs` 外观图集；`dogs_photo` 的图集与姿态来源保持原样，仅同步其被窝、嗷嗷嗷、好孩子、小宝和小杜的显示比例，统一地图高度。
- 被窝、嗷嗷嗷、胖宝宝和黄黄均从项目原始 4×3 高清图片重新导入。逐姿态使用 8px 邻格余量，按主体连通轮廓提取并等比放入 256×256 帧；原始 PNG 未改写。
- `tests/integration/test_animation.py -k dog_frame_bounds`：1 passed。检查所有实际使用姿态的帧矩形、可见 alpha 边界、素材映射和地图尺寸；站立高度按最大高度归一到约 64 逻辑像素。
- 追加 `-k "dog_frame_bounds or adjusted_dog_roles or scaled_dog_card"`：3 passed，验证角色高度差、地图边缘适配和照片版卡片/预览尺寸。
- `tools/validate_assets.py`：default、dogs、dogs_photo 三套资源均有效。
- 已人工查看重建后的 atlas 总览；边界定向检查逐一覆盖全部帧，因此包含被窝/嗷嗷嗷待机、动作幅度最大帧和卧倒帧。

## 限制

运行环境无魅族 20 设备连接；本记录验收素材和边界，不代表手机实机验收。
