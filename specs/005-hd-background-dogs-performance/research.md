# Research Decisions

## R1: 背景来源与布局

**Decision**: 以现有房屋、道路和种植格布局为构图约束，选择或制作更清晰的本地背景。对所用网络素材记录作者、许可、链接、哈希与改编方式。

**Rationale**: 现有 `ui-background.jpg` 为 1400×600，游戏将其中草坪分段拉伸到逻辑网格，再按窗口缩放；仅扩大旧 JPEG 不会增加真实细节。任意草地图片也无法直接匹配命中位置。

**Alternatives considered**: 未核实授权的 PvZ 截图不适用；纯放大旧图无画质收益。联网初步候选为 [OpenGameArt CC0 草地背景](https://opengameart.org/content/grassy-plains-background) 和 [CC0 草地纹理](https://lpc.opengameart.org/content/grass-pixel-art)，最终采用前仍需检查其授权和布局适配。

## R2: 狗狗双外观

**Decision**: `dogs` 保留为卡通版，新增 `dogs_photo` 为照片版；两者使用现有 manifest clip、Animator 和 Catalog 约定。小杜映射 jalapeno、小宝映射 wallnut、好孩子替换黄黄映射 peashooter。照片版直接利用本轮三张动作表，卡通版以其可辨认特征制作。照片版的被窝和嗷嗷嗷复用卡通动作；被窝采用已找到的 `assets/skins/dogs/source/beiwo-sheet.png` 初始灰白毛表，该表带金色围巾。该旧表为1448×1086、4列×3行，须独立适配，不能交给现有仅接受1536×1024、6列×4行的 `load_grid`。

**Rationale**: 新建完整皮肤比渲染时逐角色切换不同来源更易验证、选择和失败回退。两版均须覆盖 `skin_catalog.REQUIRED` 中的完整动作。

**Alternatives considered**: 单个 manifest 中加入混合照片开关会增加来源和缓存复杂度；静态照片不能满足已确认的动作要求。

## R3: 缩放与遮挡

**Decision**: 继续让 manifest `display_scale_multiplier` 唯一控制角色倍率；主体掩码取透明度至少96的角色像素并排除独立火焰/光效，相邻角色重叠像素除以较小掩码面积作为遮挡率，检查全部必需姿态的最大值；另目视确认头部可辨。草坪、卡片、菜单和拖动预览共用锚点与比例。

**Rationale**: 旧版小宝、小杜的 1.2 倍放大已与本轮缩小诉求冲突；须依据新源表重新测量，不能沿用旧倍率。

## R4: 性能

**Decision**: 先给未改画面和素材的旧代码增加性能采样入口，打包为基线版，在用户当前电脑测固定标准/压力场景帧间隔和输入反馈；之后测主循环绘制、缩放、Surface 创建、图集缓存等阶段，只对实测瓶颈进行优化。标准场景为5向日葵、5豌豆射手、5僵尸、10投射物、3阳光、5割草机；压力场景为45植物、30僵尸、100投射物、20阳光、5割草机。

**Rationale**: 既有约 60 FPS 结果来自 SDL dummy，不能代表真实窗口体验。任何优化不得跳过 60Hz Simulation、动作姿势或既定结算时序。
