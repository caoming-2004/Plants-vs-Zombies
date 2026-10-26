# Data Model: 动画展示节奏与角色边界

本Feature只扩展表现数据和校验语义；simulation实体/规则状态保持不变。

## Existing entities

### Skin manifest / Role appearance

存于assets/skins/{skin_id}/manifest.json，既有schema version 1。每个role含卡片、预览帧与动作clips；皮肤加载由presentation.skin_catalog.Skin负责。

- skin_id：外观标识，default或dogs。
- pixel_scale：图像源像素到逻辑像素的换算。
- roles[role]：植物/僵尸角色展示数据。
- display_scale_multiplier：仅dogs皮肤wallnut和jalapeno角色在本Feature完成后必须提供的manifest倍率；其他角色及旧manifest可省略，缺省读取为1.0。它乘以通用DOG_SCALE得到角色实际显示比例。代码只提供读取接口，不复制保存wallnut/jalapeno的倍率。
- preview、card：单张角色帧及锚点信息，供卡片和选肤预览使用。
- clips[state]：动作循环标记与有序姿势列表。
- frame.rect/source_size/trim_offset：图集源矩形、逻辑前画布大小及裁切补偿。
- frame.anchor：稳定脚底/落点基准；显示尺寸改变以此点做缩放。
- frame.duration_ticks：该姿势在60Hz表现时间轴上的正整数tick长度。

### Animation clip

对每个必需role/state组合：

- pose_count：将manifest帧解码为RGBA后，按整张图逐像素相同去重所得的姿势数；运行时无需持久保存，由资产验证器计算。该算法为确定性的计数代理，接触表人工检查用于排除只有无关像素差异的伪姿势。
- duration_ticks：所有姿势duration之和。
- pose_rate_hz：pose_count * balance.json.tick_hz / duration_ticks；tick_hz当前为60，验收范围12–18。
- loop：循环或单次动作；单次clip必须按素材顺序完整播放。hit由表现事件开始播放；原规则不等待clip结束。
- 循环clip继续满足原有至少一秒循环周期规则（如需与姿势速率范围协同，校验应报告可行性并要求补充素材/重新选姿势，不允许默默豁免门槛）。

### Timed presentation event

由既有simulation事件消费、只保存在Animator：

- kind：hit或row_clear_started等动画事件类型。
- entity_id / role / row / x / col：既有事件定位信息。
- start_tick：事件起始tick，使用事件tick，不另建wall-clock。
- clip_key：用来呈现的动作clip。
- expires_at_tick：表现寿命结束tick；会话切换时清除。
- 不向simulation快照写入表现帧、缩放或特效年龄。

小杜ignite特殊验收：clip恰有provenance映射的35个源姿势且不含插值中间帧，按序播放；总时长120 ticks，姿势率17.5/s，视觉寿命随clip结束。规则侧row-clear事件仍按现行逻辑只发出/结算一次。

## Relationships and transitions

- Skin → Role appearance → Card/preview/clips。
- Clip → ordered Frame[] → atlas pixels + anchor + duration tick。
- Simulation event → Animator presentation state → Renderer frame/overlay。
- Session ID变化 → 清空旧死亡/受击/清行等暂存表现状态。
- Pause → simulation tick不变 → 表现采样不前进；resume继续。
- Skin selection changes visual source only; replayed gameplay inputs retain identical simulation result.

## Validation rules

1. 所有REQUIRED clips在default、dogs皮肤均存在；RGBA逐像素去重后的姿势率落在12–18/s，接触表通过人工姿势有效性检查。
2. 每帧duration_ticks为正整数，anchor保持现有manifest单位与pixel_scale转换。
3. 所有clip图像顺序、锚点基线与主体边界有效；循环周期至少60 tick。
4. 小杜清行clip恰含35个provenance源帧、按序播放，duration_ticks总和恰为120；不包含额外生成in-betweens。
5. 小宝/小杜所有必须动作的草坪角色可见高度比当前基准至少增加15%；锚点偏移不超过2逻辑像素；UI预览不得裁切。
6. 相邻角色主要身体区域不重叠；越界或遮挡检测采用最终角色倍率。
7. Presentation变更不修改Simulation快照字段、domain平衡配置或规则事件数量。

## Out of scope

不增加domain实体，不改变植物价格/生命/伤害/冷却/波次，不保存玩家动画状态，不改变皮肤选项格式或运行时联网下载素材。
