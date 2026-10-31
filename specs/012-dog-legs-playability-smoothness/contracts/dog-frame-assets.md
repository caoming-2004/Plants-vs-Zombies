# Contract: 狗狗动作帧资产（完整轮廓）

**Feature**: `012-dog-legs-playability-smoothness` | **Date**: 2026-10-31

## 目的

规定被窝与嗷嗷嗷从原始高清图片到游戏动作帧的边界，确保脚掌、腿、尾巴、耳朵和口鼻完整显示；此契约只约束素材导入与清单，不改变游戏规则。

## 输入

| 角色 | 外观 | 源文件 | 布局 |
|---|---|---|---|
| 被窝（向日葵） | dogs | `assets/skins/dogs/source/被窝.png` | 1672×941，4×3，12 个姿态 |
| 嗷嗷嗷（普通僵尸） | dogs | `assets/skins/dogs/source/嗷嗷嗷.png` | 1672×941，4×3，12 个姿态 |
| 被窝（向日葵） | dogs_photo | `assets/skins/dogs/source/beiwo-sheet.png` | 1448×1086，4×3，12 个姿态 |
| 嗷嗷嗷（普通僵尸） | dogs_photo | 现有复用/生成素材 | 按实际清单验证 12 个姿态 |

源 PNG 必须保持不变，不得覆盖、重命名或在原图上做破坏性处理。

## 提取规则

1. 读取 RGBA 源图，以 alpha 阈值 96 生成遮罩；保留面积不小于 80 像素的连通体，过滤孤立噪点。
2. 必须得到 **12 个主体连通体**；少于/多于 12 个时失败并提示源图或阈值需要人工核对。
3. 按连通体包围盒中心排序：先按 y 归入 3 行（行高约 `height/3`），每行再按 x 升序排列，得到 4×3 行优先的 12 个姿态。排序必须稳定、可复现。
4. 每个姿态使用其**完整包围盒**，不得按等分格线直接切块，也不得只取某个连通体而丢弃越线肢体。
5. 等比缩放到 256×256 帧：可见内容距左/右/上边界至少 8 像素；脚底基线固定为 y=232；水平居中。禁止非等比拉伸。
6. 输出帧的 `source_size=[256,256]`、`trim_offset=[0,0]`、`anchor=[128,232]`；`source_frames` 记录源姿态 0..11。
7. 动作 clip（idle/walk/attack/hit/die 等）可以继续使用现有插值帧；每个输出帧必须仍只包含该姿态的完整轮廓，不得带入相邻姿态碎片。

## 清单与图集

- 同步更新 `assets/skins/dogs/atlas*.png`、`manifest.json`、`provenance.json`，以及 dogs_photo 中复用该角色的清单/图集。
- provenance 至少记录：源文件名、SHA-256、源 bbox、连通体序号、输出帧 rect、`source_frames`、提取方法和日期。
- manifest 的帧矩形、画布、偏移和锚点必须通过现有 `skin_catalog.Skin.validate_frame`。
- 其他狗狗角色的外观和帧映射不得因本次提取发生非预期变化。

## 可见性不变量

对每个实际使用的帧：

- 可见 alpha 包围盒完全位于帧内：`left >= 8`、`top >= 8`、`right <= 248`、`bottom <= 232`。
- 可见包围盒包含该姿态的完整狗身；不得出现脚掌/尾巴被平切、只剩半只脚或只剩部分尾巴的情况。
- 帧中不得出现相邻姿态的肢体检出物；每个帧最多一个主体。
- 地图显示高度与脚底基线满足 `tests/integration/test_animation.py` 现有约束（高度差 ≤20%，基线波动 ≤2 逻辑像素）。
- 菜单、卡片、拖动预览、地图、攻击、受击、倒地和地图四角位置均完整可见；`fit_visible_frame` 只能为保持在画布内平移，不能改变角色所属格或点击区域。

## 验收

1. 运行 `.venv\Scripts\python.exe tools\import_dog_assets.py`，确认成功生成 12 个源姿态且无异常。
2. 运行 `.venv\Scripts\python.exe tools\validate_assets.py`，确认 dogs/dogs_photo 图集和清单有效。
3. 运行 `.venv\Scripts\python.exe -m pytest tests/integration/test_animation.py -k dog_frame_bounds -q`。
4. 用源图与输出帧逐姿态对照，人工检查待机、抬腿、尾巴展开、卧倒和倒地帧；在菜单、卡片、地图和拖动预览中确认完整。
5. 重点检查被窝与嗷嗷嗷两套外观；若 dogs_photo 某角色素材本身已完整，只需记录检查结果，不做无关重画。
