# 006 背景素材与构图验收

## 在线候选核验

- [High res animated grass for fixed background](https://opengameart.org/content/high-res-animated-grass-for-fixed-background-1920x1080)：OpenGameArt 页面列出作者 Puffolotti、CC0 和 1920×1080；素材是草地/前景/桥等分层组件，需要与道路或平台组合。它没有第一版房屋、道路与种植区布局，且风格不匹配，所以未下载进游戏、未打入发行包。
- [Grass](https://opengameart.org/content/grass-9)：页面列出作者 Starry Skydancer、CC0 与 1024×1024 俯视草地纹理；作为纹理缺少第一版建筑/道路构图，本次未采用。
- 最终图采用项目生成的重绘图，不包含第三方网络素材；因此无需把未采用候选登记为发行资源。

## 最终图

- 第一版构图来源：`7305e3d` 的 1400×600 背景，见 `baseline-visuals.md`。
- 原始重绘：[`background-006-imagegen.png`](../../../assets/skins/default/source/background-006-imagegen.png)，由图像生成工具按原布局重绘，尺寸 1915×821。
- 生产主图：[`background-006-high-detail.png`](../../../assets/skins/default/source/background-006-high-detail.png)，2800×1200；由重绘图用 Pygame smoothscale 生成。项目拥有该生成图，无第三方素材许可证依赖。
- 运行时文件：`assets/skins/default/ui-background.png`；由 `tools/generate_background.py` 从高分辨率主图可重复生成，静态离线加载并缓存。
- `assets/sources.json` 记录主图与生成源图的 SHA-256、分辨率及派生关系。

## 三档窗口截图与布局核对

| 窗口 | 同场景截图 | 房屋/草坪/道路布局 | 网格/输入坐标 |
|---|---|---|---|
| 1050×600 | [background-1050.png](background-1050.png) | 保留首版左侧房屋、中央草坪、右侧道路 | `test_background_keeps_logical_board_and_window_input_mapping` 通过 |
| 1260×720 | [background-1260.png](background-1260.png) | 保留 | 同一逻辑网格，命中映射测试通过 |
| 1920×1080 | [background-1920.png](background-1920.png) | 保留 | 同一逻辑网格，命中映射测试通过 |

照片版皮肤的同场景窗口截图另存为 `background-1050-photo.png`、`background-1260-photo.png` 和 `background-1920-photo.png`。

生成文件重建一致性与最终像素哈希记录于 `assets/sources.json`。自动布局/交互位置检查：`tests/integration/test_background_layout.py` 的2项测试通过。渲染保持缓存画布和1050×600逻辑坐标，窗口缩放沿用原输入坐标转换路径。
