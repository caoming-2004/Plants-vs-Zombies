# 角色动作矩阵与资产验收

所有图集使用 2x 像素画布，运行时按皮肤 pixel_scale 映射到逻辑尺寸。动画时间轴为 60 tick/s。循环动作至少 60 tick，目标采样率至少 24 个不同可见姿势/秒；禁止重复同一帧填充帧率。锚点以画布内逻辑脚底位置固定，射击与啃咬使用独立 muzzle/contact 锚点。

| 角色 | 默认动作 | 小狗动作 | 朝向/锚点 |
|---|---|---|---|
| 向日葵 | idle、produce、hit、die | 被窝 idle、produce、hit、die | 植物朝右；脚底居中，产阳光用抬爪姿势。 |
| 豌豆射手 | idle、attack、hit、die | 黄黄 idle、attack、hit、die | 植物朝右；muzzle 对齐豌豆生成位置。 |
| 坚果墙 | idle、hit、die | 小宝 idle、hit、die | 植物朝右；固定脚底线，阻挡不触发攻击。 |
| 火爆辣椒 | plant、ignite、hit、die | 小杜 plant、ignite、hit、die | 植物朝右；ignite 是玩法事件的视觉响应。 |
| 普通僵尸 | walk、bite、hit、die | 嗷嗷嗷 walk、bite、hit、die | 面向左；固定接触锚点，啃咬不移动脚底。 |

同一角色的所有帧使用同一 256×256 源画布、固定 anchor 与足底位置。manifest `pixel_scale=2`。验证器需检查帧矩形、动作覆盖、采样帧差异、帧时长和锚点；狗狗另需至少达到默认角色可见高度的75%，并逐帧检查相邻格不重叠。
