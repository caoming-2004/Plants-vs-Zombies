# Data Model

## BackgroundAsset

- 本地资源路径、原始来源链接、作者、许可、必要署名、改编方式及 SHA-256；所有字段可核查。
- 保留既有逻辑画布和房屋、道路、种植格位置；逻辑网格仍由当前配置定义。

## DogSourceSheet

- 身份/角色一对一：小杜/jalapeno、小宝/wallnut、好孩子/peashooter。
- 三张原始 PNG 均为 1619×971、10 列×6 行。导入时核验 60 姿势、透明主体、足部基线和帧间串色。
- 原始文件永久保留；导出图集和 manifest 可重建，来源记录存 SHA-256 与原帧索引。
- 被窝初始灰白毛源表 `assets/skins/dogs/source/beiwo-sheet.png` 为1448×1086、4列×3行；需单独记录其12个原始姿势及映射到 idle、produce、hit、die 的规则，不修改原件。

## Appearance

- `skin_id`：`default`、`dogs`、`dogs_photo`。植物在菜单选择三者之一；僵尸沿用 `default` 或 `dogs`。
- 每套完整皮肤提供 `REQUIRED` 角色、card、preview 和全部动作 clip。
- 帧沿用 `rect`、`anchor`、`source_frames`、`duration_ticks`；角色倍率存 `display_scale_multiplier`，缺省为 1.0。
- 选肤只在菜单改变；素材失效时整套回退 `default`，不混用角色。

## PerformanceRun

- 设备、打包版本、显示驱动、窗口尺寸、场景负载、测量时长。
- 场景固定负载：标准为5向日葵、5豌豆射手、5僵尸、10投射物、3阳光、5割草机；压力为45植物、30僵尸、100投射物、20阳光、5割草机。
- 帧间隔序列、平均 FPS、P95 帧间隔、超过 50ms 的最长连续帧数。
- 至少 20 次有效操作的事件接收和可见反馈时间、操作结果；与同设备、同场景旧版本配对比较。
