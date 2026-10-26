# Plant and Input Contract

## 种植命令

现有Command接口不变：SelectPlant(type_id)、PlantAt(row,col)、CancelSelection。成功种植规则只有Simulation.command一个权威实现；UI的格子预览只是snapshot预测，不能扣费、占格或宣告成功。

### PlantType roles

- producer：创建持久植物，按配置周期产阳光。
- shooter：创建持久植物，按配置周期发射投射物。
- blocker：创建持久植物，不产出、不远攻；同排僵尸依既有target()规则停下啃咬。
- row_clearer：一次性作用，不创建持久Plant，不占格。有效放置后扣费并设冷却，立即清除命令执行时该行所有现存存活僵尸。

PlantAt统一拒绝不合法行列、占格、冷却、资源不足和错误阶段；失败不改变任何玩法状态。默认/狗狗外观、动画状态和拖动路径均使用相同数值与校验。

### RowClearStarted event

字段：kind=`row_clear_started`、session_id、event_seq、tick、effect_id、type_id=`jalapeno`、row、col、zombie_ids。

同tick事件顺序：接受PlantAt并生成RowClearStarted → 按zombie_ids升序通过统一damage路径发出hit/died → systems.advance继续既有波次、投射物、攻击、割草机和胜负步骤。选中目标仅包括PlantAt处理时已存在且hp>0的同排僵尸；该tick随后生成的僵尸不受影响。死亡单位不参与后续步骤，击杀统计单次递增，失败仍优先于胜利。

渲染器只凭事件播放横向火焰clip并在clip结束时清理临时效果。重复消费同一event_seq不得重复生成伤害或逻辑效果。

## DragState输入契约

DragState属于presentation input/controller，不出现在Simulation、Command payload或snapshot中。指针与格子坐标均先经logical_position映射到1050×600逻辑空间。

1. 左键按下植物卡：选择该植物并创建DragState；移动时只更新指针和目标提示，不发送PlantAt。
2. 在草坪格释放：依序处理SelectPlant/既有选择与单次PlantAt(row,col)。规则层在处理时重新验证。成功后沿用既有清除选择行为；失败显示reason_code映射的中文反馈，pointer drag结束。
3. 卡片上按下并在卡片上释放：等同原有点击选卡，不产生PlantAt。原有选卡后点击空地继续可用。
4. 草坪外/HUD/留边释放：不发送PlantAt。右键、Esc、窗口失焦、暂停、结算或切换场景清除DragState；绝不保留指针预览或生成重复命令。
5. 目标为空且余额足够/卡片就绪/对局进行时显示可放置样式；占格、余额不足、冷却及范围外分别显示无效样式/文本。预判状态不得取代Simulation最终结果。
6. 一次释放最多生成一个PlantAt；一个鼠标事件不得同时触发卡片、收集阳光与草坪动作。HUD优先于世界拾取物/草坪，保留现有优先级。

## 必须覆盖的输入验收

- 四张卡的点击选择和拖动到第一列/最后一列空格。
- 释放到占用格、草坪外、HUD、留边；阳光不足与卡片冷却。
- Escape、右键、失焦、暂停/结果/菜单期间取消并无残留拖动预览。
- 相同输入用点击模式和拖动模式得到相同sun/plant/cooldown状态。
- 释放附近两个event或连续释放不能造成双扣费、双种植或触发遮挡下方目标。
