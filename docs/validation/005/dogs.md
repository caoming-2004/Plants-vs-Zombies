# 005 狗狗双外观验收

## 资源和映射

- `dogs` 是卡通版，`dogs_photo` 是照片版，均按完整皮肤清单生成；照片版被窝使用原始 `beiwo-sheet.png` 的独立 4×3 导入，嗷嗷嗷复用卡通角色。
- 好孩子→豌豆射手，小宝→坚果墙，小杜→火爆辣椒；三张用户表的原图不修改。
- `tools/import_dog_assets.py` 对源表按 10×6 读取；派生角色帧保留 `source_frames`、原文件 SHA-256 和动画分段。
- 卡通派生采用本地确定性像素化/颜色量化。它是照片表的风格化版本，并非手绘或照片复刻。
- 角色尺寸使用 manifest 的 `display_scale_multiplier`；`dog_validation.py` 以 alpha≥96 的最大连通主体计算横向/纵向相邻角色遮挡率，阈值为25%。

## 结果

- 原始三张新表经导入工具检查为 1619×971、60 帧；被窝原表为 1448×1086、12 姿势。导入程序保留原始文件。照片版被窝使用独立4×3导入并保留金围巾；嗷嗷嗷沿用原卡通。
- `.venv/Scripts/python.exe tools/import_dog_assets.py`：成功，生成卡通图集579个唯一帧、照片图集522个唯一帧；清单分别引用587和539个帧（含共享引用）。
- `.venv/Scripts/python.exe tools/validate_assets.py`：default、dogs、dogs_photo 三套资源完整，动作采样率均符合12–18姿势/秒。
- 聚焦测试43 passed；全量 `.venv/Scripts/python.exe -m pytest -q`：120 passed。包含动作、来源帧追溯、好孩子映射、照片版选择与损坏素材整套回退，以及规则重放。
- 主体遮挡率（alpha≥96，按邻格/行与较小主体掩码面积计算）：dogs最坏值0%；dogs_photo最坏值约1.44%，均低于25%。
- 全姿势预览及每个必需动作完整帧条已导出：[狗狗卡通预览](animations/dogs-actions.png)、[狗狗照片预览](animations/dogs_photo-actions.png)、[双外观动作细节总览](animations/detail-samples.png)。逐帧图片位于同一 `animations/` 目录，文件名为 `{skin}-{role}-{action}.png`。
- 已检查总览中三只狗与被窝/嗷嗷嗷的角色可辨、动作主体未裁切；该检查是生成预览的静态目视，不等于实际菜单、卡片与拖动交互验证。真实窗口拖放和实机性能尚未测。
