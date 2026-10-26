# 默认视觉参考与测量板

2026-10-25。本板记录已取得的参考和剩余验收缺项；不将社区导出的帧自动认定为官方PC初代完整时序。

## 固定参考

| 对照对象 | 来源 | 尺寸 / 帧数 | 本次接入 |
|---|---|---|---|
| 向日葵 | marblexu/PythonPlantsVsZombies, Plants/SunFlower | 73×74，18帧 | idle与produce沿用参考循环，hit叠加，die衍生淡出 |
| 豌豆射手 | 同仓库，Plants/Peashooter | 71×71，13帧 | idle与attack沿用参考循环，hit叠加，die衍生淡出 |
| 普通僵尸 | 同仓库，NormalZombie/Zombie | 166×144，22帧 | 行走，统一0.7倍率后放入128画布 |
| 僵尸啃咬 | 同仓库，NormalZombie/ZombieAttack | 21帧 | 映射到模拟啃咬周期；不修改伤害时刻 |
| 僵尸死亡 | 同仓库，NormalZombie/ZombieDie | 10帧 | 逻辑死亡后独立表现播放 |
| 草坪 | 同仓库，Background_0.jpg | 1400×600 | 适配1050×600逻辑画布；保留72×76格子，五行十二列草坪占x=105..969 |
| 主菜单 | 同仓库，Screen/MainMenu.png | 900×600 | 背景接入，按钮与中文标题为本项目界面 |
| 卡片、阳光、豌豆、割草机 | 同仓库对应Cards/Plants/Sun/Bullets/Screen/car | 尺寸见provenance文件 | 独立资源清单引用 |
| 铲子及铲子槽 | FregD156/PvZ_Assets, images/Shovel.png、ShovelBank.png | 原始导出图 | 接入默认UI图集 |

第一仓库固定提交：afc4ae12c7a19bee5aaa2c20e9d765e1afcccd80。
第二仓库提交记录在assets/sources.json与.tools/references/original-ui/commit.txt。
逐文件SHA256与原始路径在assets/skins/default/provenance.json；图集与清单在同目录。

来源入口：
- https://github.com/marblexu/PythonPlantsVsZombies
- https://github.com/FregD156/PvZ_Assets

第一仓库README标注个人学习、非商业；本次只制作本地学习试玩包，未把媒体权利描述成开源许可证。

## 测量方法与判定尺度

使用1050×600逻辑像素，按contracts/assets-and-release.md执行：布局位置≤2px；同姿态宽高偏差≤5%；
动作周期偏差≤5%且允许1tick采样误差；世界脚底接缝≤1px；事件同步≤1tick；发射/接触锚点偏差≤2px。
原始角色帧不重新绘制，统一画布、锚点与倍率在tools/import_classic_assets.py固定。
校验器验证rect、偏移、来源、完整状态；预览工具展示脚底基线、全部状态并导出逐帧条带。
加长地图的角色和草坪以72×76逻辑格布局；1050画布内新增横向空间及HUD排布按本项目明确差异记录，
不得将其算作原版静态布局测量通过。客户区低于1050×600的窗口不在支持范围。

## 尚未通过的严格原版验收

- 当前草坪/卡槽/菜单为了US1逻辑格子及中文操作做了布局适配，尚未证实与原版位置差≤2px。
- 来源没有独立向日葵产出、射手发射和植物死亡帧组；当前复用循环、事件同步和衍生淡出不是独立原版帧证据。
- 来源动画间隔只能说明该社区项目播放方法；没有官方PC初代录屏的逐动作时间段，原版周期≤5%未验证。
- 原版造型与关键姿态仍需维护者对照审核。截图和代码检查不代替该审核。

因此T043保持未完成；不能将当前默认外观宣称为已通过全部原版一致性标准。
