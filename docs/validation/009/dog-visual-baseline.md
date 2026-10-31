# 狗狗轮廓基线（修改前）

采样自 `dogs` / `dogs_photo` 当前 manifest 和图集，方法为取所有要求动作帧的非透明 alpha 外接框（alpha > 0），按 `DOG_SCALE × display_scale_multiplier / pixel_scale` 换算逻辑像素。完整动作边界后续验收仍按实际锚点绘制位置核对。

| 外观 | 角色 | 当前倍数 | 最大可见高度 | 最大可见宽度 |
|---|---|---:|---:|---:|
| dogs | 被窝 (`sunflower`) | 1.32 | 68.7 | 96.0 |
| dogs | 嗷嗷嗷 (`zombie_basic`) | 1.32 | 65.1 | 96.0 |
| dogs | 好孩子 (`peashooter`) | 1.43 | 86.5 | 70.5 |
| dogs | 小宝 (`wallnut`) | 1.43 | 77.8 | 70.5 |
| dogs | 小杜 (`jalapeno`) | 1.43 | 78.3 | 70.5 |
| dogs | 胖宝宝 (`pangbaobao`) | 1.40 | 67.6 | 101.9 |
| dogs | 黄黄 (`huanghuang`) | 1.40 | 72.8 | 101.9 |
| dogs_photo | 被窝 (`sunflower`) | 1.02 | 74.2 | 76.3 |
| dogs_photo | 嗷嗷嗷 (`zombie_basic`) | 1.00 | 74.8 | 49.3 |
| dogs_photo | 好孩子 (`peashooter`) | 1.43 | 86.5 | 70.5 |
| dogs_photo | 小宝 (`wallnut`) | 1.43 | 77.8 | 70.5 |
| dogs_photo | 小杜 (`jalapeno`) | 1.43 | 78.3 | 70.5 |

最大伸展姿态来自狗狗自己不同的循环/攻击动作；卡通和照片使用不同图集与各自的原始倍数。原始 alpha 框和角色缩放本次复算，记录日期 2026-10-30。
