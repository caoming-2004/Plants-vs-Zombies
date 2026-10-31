# 005 背景验收

## 资产与构图

- 已重新绘制高细节横版背景；在原有布局参考上保留左侧房屋、顶部围栏、中央草坪、右侧步道/道路和底部草边。新 PNG 为 1915×821，纹理与边缘为重新生成的细节，并非插值放大旧 JPEG。
- 原始生成图：[`background-005-high-detail.png`](../../../assets/skins/default/source/background-005-high-detail.png)。游戏使用同内容的本地 [`ui-background.png`](../../../assets/skins/default/ui-background.png)，离线可加载。来源与 SHA-256 记录在 `assets/sources.json` 的 `generated-background-005`。
- `default/manifest.json` 引用 `ui-background.png`。生成脚本可从保留的主图无损重建运行时文件。
- 游戏逻辑画布维持1050×600；网格原点(105,160)，12×5格，每格72×76。背景只替换绘图资源，点击/拖放坐标映射不变。

## 同场景新旧截图

截图来自同一固定 smoke 对局及同一 1050×600 逻辑画布；通过 SDL dummy 稳定保存并用于像素尺寸目视比较，不能代表显示设备帧率。

| 窗口 | 改前 | 改后 | 房屋/草坪/道路布局 | 纹理细节与边缘 | 网格可读、角色对比 |
|---|---|---|---|---|---|
| 1050×600 | [baseline](baseline-1050.png) | [新图](background-1050.png) | 通过 | 通过 | 通过 |
| 1260×720 | [baseline](baseline-1260.png) | [新图](background-1260.png) | 通过 | 通过 | 通过 |
| 1920×1080 | [baseline](baseline-1920.png) | [新图](background-1920.png) | 通过 | 通过 | 通过 |

目视结果：门窗、围栏、草地与道路边界清晰；新草地纹理在三种目标尺寸均无放大旧 JPEG 造成的块状；格线仍可辨认，前景角色和可收集物没有被背景遮盖。

## 自动验证

- `.venv/Scripts/python.exe -m pytest -q tests/integration/test_background_layout.py tests/integration/test_asset_manifest.py tests/integration/test_animation.py tests/integration/test_skin_selection.py tests/replay/test_base_replay.py tests/replay/test_skin_invariance.py`：47 passed。
- `.venv/Scripts/python.exe tools/validate_assets.py`：default、dogs、dogs_photo 资源清单均通过。
- 相同游戏会话仍通过固定的菜单/种植 smoke 及逻辑网格映射测试；完整三种尺寸的真实桌面窗口与鼠标实测仍需打包后确认。
