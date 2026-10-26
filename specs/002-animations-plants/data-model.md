# Data Model: 植物、拖动输入与动画

本特性复用已有1050×600逻辑场地、60 tick/s Simulation、Plant、Zombie、Command、事件序号及皮肤配置边界。表现层不拥有规则数值或单位生命。

## 配置

| 实体 | 字段与约束 |
|---|---|
| PlantType | id/name/price/cooldown_ticks/role；ID非空唯一，价格为非负整数，冷却为正整数。role取producer、shooter、blocker、row_clearer之一。 |
| producer配置 | 持久Plant需要hp>0、production_interval_ticks>0、sun_value>0。 |
| shooter配置 | 持久Plant需要hp>0、attack_interval_ticks>0、projectile_speed>0、damage>0。 |
| blocker配置 | 持久Plant需要hp>0；不得包含产出或远程攻击行为。 |
| row_clearer配置 | 一次性能力，无持久hp实体；需要price和cooldown_ticks，在放置时清除同排现存僵尸。 |

所有参数仅在assets/config/balance.json定义。初始建议值：wallnut 50阳光/1200生命/1800tick冷却；jalapeno 125阳光/3000tick冷却。向日葵、射手、普通僵尸的既有数值不变。

## 运行时状态

| 实体 | 字段与生命周期 |
|---|---|
| Plant | 既有字段id/type_id/row/col/hp/next_action_tick/action；向日葵、豌豆射手和坚果墙为持久单位。坚果墙占一格、接触后由同排Zombie攻击，hp为0后立即释放格子。 |
| 一次性火爆辣椒 | 不进入plants，不持续占格；PlantAt验证成功后扣费、设置冷却、清除选择并产生RowClearStarted事件和稳定的击杀事件。 |
| RowClearStarted | event kind、session_id、event_seq、tick、effect_id、type_id=jalapeno、row、col及本次受影响的zombie_ids；目标ID按升序排列，事件只表示已结算的逻辑动作，不是待处理伤害。 |
| Zombie | 使用既有结构。火爆辣椒调用统一伤害/死亡路径，hp=0立即不再作为攻击、移动、割草机或胜负的有效目标，击杀数只加一次。 |
| DragState | 仅presentation持有：active、plant_type_id、pointer_screen、pointer_logical、hover_cell(row/col可空)、preview_valid、reason_code；只在鼠标拖动期间存在，按键释放、取消、失焦、暂停、结算和场景切换时清除。 |
| RowClearVisual | Animator从RowClearStarted创建的临时呈现对象，记录effect_id/row/col/start_tick和当前clip帧；只影响绘制，不存入Simulation或snapshot。播放结束后删除。 |

## 种植事务与顺序

1. PlantAt先按既有顺序确认对局阶段、坐标范围、格子空闲、卡片冷却和余额；任一失败不改变余额、格子、冷却或植物集合。
2. producer/shooter/blocker成功时创建持久Plant并扣费、更新冷却、占格、清除选择，沿用既有planted事件。
3. row_clearer成功时不创建持久Plant；原子扣费/更新冷却后分配effect_id，发出RowClearStarted，并对该命令执行时已在场且存活的本行Zombie按ID调用既有damage/kill路径。
4. 本tick后续波次生成不追溯加入目标名单；已死亡Zombie不再次受击、啃咬、移动、触发割草机或增加击杀数。
5. `systems.advance`仍负责波次、投射物、植物/僵尸行动、割草机及唯一胜负结算；失败优先于胜利。视觉RowClearVisual不会推迟或重做步骤3的结果。

## 皮肤与动画资源

Manifest角色集合：sunflower、peashooter、wallnut、jalapeno、zombie_basic。default与dogs均须提供对应卡片、预览和适用动作；dogs角色名称为被窝、黄黄、小宝、小杜、嗷嗷嗷（敌方红背心）。

Frame元数据包含atlas rect、source_size、trim_offset、anchor、muzzle、contact、duration_ticks。素材坐标均使用源图像素；manifest pixel_scale=2表示每个逻辑像素对应至少2个源像素。渲染位置通过 `(trim_offset-anchor)/pixel_scale` 转换到逻辑单位，再乘窗口显示比例。所有来源指向assets/sources.json并保留版本/许可/生成提示记录。

循环动作继续遵守完整周期不少于60tick。clip独特可见帧率定义为不同规范化帧数 ÷ (sum(duration_ticks)/60)，结果至少24帧/秒。重复帧按裁剪和透明边标准化后的像素内容去重；不能复制同一姿态凑数。受击/死亡等短动作不要求最短持续时间，但仍须达到适用的24姿势/秒采样要求。

## 显示布局

输入、格子与世界坐标继续采用1050×600逻辑单位。显示目标surface跟随窗口实际像素尺寸；统一逻辑到显示坐标转换供绘制使用，鼠标先映回逻辑坐标后执行同一hit-test。当前窗口比例、留边与最低支持客户区规则不变。

四张卡同屏使用逻辑位置 `(162,22)`, `(282,22)`, `(402,22)`, `(522,22)`，卡片尺寸均为110×97；铲子移至x=645附近，保留右上阳光HUD独立矩形。具体间距以控件合同和截图核验为准。
