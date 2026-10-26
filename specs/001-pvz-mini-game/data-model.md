# Data Model

所有玩法实体只属于模拟层。世界位置使用1050×600逻辑坐标；时间使用非负整数tick，60 tick/s。
战斗显示画布为1050×600；初始窗口为1260×720，窗口客户区不得小于1050×600逻辑像素；更大窗口等比缩放及反向输入映射，不能缩小到逻辑画布以下。角色、碰撞和格子位置均按逻辑坐标定义。
实体ID为同一局内唯一递增正整数；重新开始建立新局，禁止复用旧事件。

## 配置与关卡

| 实体 | 字段与约束 |
|---|---|
| BalanceConfig | schema_version=1；initial_sun>=0；tick_hz=60；plant_types、zombie_types使用唯一字符串ID；金额/生命/伤害为整数；生命及行动周期>0，价格>=0，速度>0 |
| PlantType | id、price、hp、cooldown_ticks、role（producer/shooter）；producer的production_interval_ticks>0、sun_value>0；shooter的attack_interval_ticks>0、projectile_speed>0、damage>0；数值只在此引用 |
| ZombieType | id、hp>0、speed>0、bite_damage>0、bite_interval_ticks>0、contact_distance>0 |
| LevelDefinition | id=day_01；rows=5；cols=12；sun_schedule、spawn_schedule；生成项含tick>=0、row为0..4、有效type_id；按tick和原始序号稳定排序；至少一个僵尸，必须有限 |
| DisplayLayout | canvas_width=1050、canvas_height=600；grid_x=105、grid_y=160、cell_width=72、cell_height=76；12列草坪边界x=969，须在画布内；spawn_x=1010；window_size=1260×720；min_client_size=1050×600；窗口不得缩小至逻辑画布以下，较大窗口保持比例缩放并将输入映射回相同逻辑坐标 |

首轮可调默认：初始阳光150；每份阳光25；向日葵价格50、射手100；两者生命300、卡片冷却450tick；
自然阳光间隔600tick、向日葵产出间隔1440tick；射手攻击间隔90tick、伤害20、投射物速度300像素/秒；
普通僵尸生命200、速度12像素/秒、啃咬伤害20/60tick；阳光寿命600tick、割草机速度600像素/秒。
以上为本小游戏首轮平衡提案而非声称测得原版精确数值。配置储存速度单位为像素/秒，模拟每tick换算。
第一关生成表默认12只，tick=1200+900*i（i=0..11），row=i%5；后续平衡只改关卡/配置并重验可获胜性。

## 运行时实体

| 实体 | 字段与约束 |
|---|---|
| GameSession | session_id；phase=menu/playing/paused/won/lost；tick>=0；sun>=0；level_id；next_spawn_index；entity集合；每种卡片ready_tick；selection；递增事件序号 |
| GridCell | row 0..4，col 0..11；plant_id可空；每格最多一个存活植物；单位移除时原子清空占用 |
| Plant | id、type_id、row、col、hp 0..type.hp、action=idle/producing/attacking/dying、next_action_tick；hp=0立即失去占格及行动能力，死亡效果由表现层短暂保留 |
| Zombie | id、type_id、row 0..4、x、hp、target_plant_id可空、action=walking/biting/dying、next_bite_tick；target必须存活且同排，消失后恢复walking |
| Projectile | id、source_id、row、previous_x、x、damage>0、active；按上一位置到当前位置的线段命中最近存活敌人一次，不穿透；记录born_tick，出生tick不移动也不命中，下tick开始更新 |
| SunPickup | id、x、y、value>0、expires_tick、collected；只能收集一次；tick < expires_tick才可收集，tick >= expires_tick立即失效，不以是否已清理对象判断；铲除向日葵不删除已经生成的阳光 |
| LawnMower | row唯一且0..4、state=ready/sweeping/spent、previous_x、x；每局正好5台；ready→sweeping→spent，不可逆，重开新建 |
| Selection | none/plant/shovel三选一；plant必须有有效type_id；切换自动取消旧选择 |
| AppearanceSelection | plant_skin_id、zombie_skin_id；默认default；只可在menu修改，重开保留，会话退出不保存 |

## 状态转换与事务

- menu→playing；playing↔paused；playing→won/lost；won/lost→playing重建对局；返回菜单清空对局。
- 种植命令必须同时满足playing、合法格、空格、足够阳光、卡片就绪；一次事务扣费、生成植物、占格、更新冷却；失败全不变。
- 铲除只在playing且铲子已选中时有效，移除植物但不退款、不更改卡片冷却，空格不变；右键或Esc取消当前选择。
- 暂停不推进模拟tick，操作命令除恢复/退出外均拒绝；重开保留外观但重建计时、实体、资源与全部割草机。
- 死亡植物不再攻击或产出；已发出的投射物继续飞行；死亡僵尸不能啃咬、触发割草机或触发失败。
- 同tick处理顺序见 contracts/simulation.md；失败优先于胜利且只产生一次结算事件。

## 皮肤数据

SkinManifest含schema_version=1、skin_id、display_name、完整角色映射、卡片/预览、图集、clips及source_refs。
角色必须覆盖 sunflower/peashooter/zombie_basic 的适用状态；每帧rect宽高>0、duration_ticks>=1，图集内边界合法。
每帧必须记录source_size与trim_offset；source_size宽高>0，裁切偏移不得超出原始画布。anchor、muzzle和contact使用每帧未裁切逻辑画布坐标；不能以图片尺寸推导碰撞盒。
clip包含loop、帧序列及动作周期相位。视觉事件只驱动表现，不生成伤害或资源。
默认外观缺必需资源则中文错误并中止开局；小狗外观不完整则整套所选阵营回退default并提示，不逐帧混搭。
source_refs指向assets/sources.json，包含来源URL/本地来源、角色、动作、版本、参考时间段及制作说明。
小狗映射文档包含候选名称、身份参考、外观参考、三角色映射、动作适配与用户确认记录；确认前状态proposed。
重复动作循环（idle、walk、produce、attack、bite）完整周期不得短于60模拟tick；hit、die等一次性动作不受该下限约束。
狗狗角色统一按对应默认角色的标定高度进行缩放，最终高度不得低于75%；将三种角色的全部两两组合（含同角色配对）置于同一行相邻列的格子中心，对所有动作帧成对检查依据trim_offset及脚底锚点还原后的非透明像素遮罩，不得有可见像素相交。
动画采样频率至少30Hz，渲染目标60 FPS；动画时间基于模拟tick/单调呈现时间映射，不得回调或推进玩法状态。窗口不得缩小到1050×600逻辑像素客户区以下；不裁切、不滚动地图且不改变逻辑格尺寸。
