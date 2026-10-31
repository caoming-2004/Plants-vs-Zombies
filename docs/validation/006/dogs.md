# 006 狗狗动作素材验收

## 素材重建

- 输入保留在 `assets/skins/dogs/source/`；小宝、小杜、好孩子使用原始 10×6 用户动作表，源文件未覆盖。被窝继续使用初始灰白毛造型，嗷嗷嗷继续沿用红背心僵尸造型。
- 卡通处理已移除 64×64 缩放往返，在 256×256 姿势单元内保留原始轮廓/毛色细节，透明边缘只做阈值清理。
- 输出卡通图集 `assets/skins/dogs/atlas-005.png`、照片图集 `assets/skins/dogs_photo/atlas-002.png`，manifest/provenance 均保留角色映射、源帧索引、锚点与时长。新卡通源图用 `20261027` 版本名，旧生成图不覆盖。

## 自动校验与预览

- `tools/validate_assets.py`：通过。default 538、dogs 587、dogs_photo 539 个引用帧均有效；动作姿势速率在 12–18 distinct poses/s 范围；两种狗皮肤通过 `validate_dog_non_overlap`，无相邻种植格遮挡诊断。
- `tools/preview_animations.py --export docs/validation/006/previews`：已导出三套皮肤的动作接触表和每个动作的完整姿势条。
- 人工预览检查：`dogs-actions.png` 与 `dogs_photo-actions.png` 中角色身份清楚，脚底基线对齐；实际对局尺寸截图中狗狗与草坪/格子仍可辨认。逐动作原始姿势条一并留档供复核。

## 三档窗口截图

卡通版同场景截图：

- [1050×600](background-1050.png)
- [1260×720](background-1260.png)
- [1920×1080](background-1920.png)

照片版同场景截图：

- [1050×600](background-1050-photo.png)
- [1260×720](background-1260-photo.png)
- [1920×1080](background-1920-photo.png)

以上截图为静态显示布局核对；当前显示帧样例不替代 60 秒真实窗口流畅度测量。
