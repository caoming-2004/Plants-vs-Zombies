# Animation Presentation Contract

本契约描述桌面游戏的内部表现与输入输出验收，不创建新的网络/API协议。

## Clock and rule boundary

- Simulation以60Hz tick为唯一玩法权威。
- Renderer目标60FPS；它读取snapshot tick，不推进规则。
- Animator只消费simulation snapshot和事件并计算视觉帧，不修改或延后领域规则结果。
- 每个clip姿势节奏为12–18个可辨认姿势每秒；暂停不推进，resume延续当前tick。
- 自动姿势计数使用RGBA逐像素相同去重，pose_rate_hz = pose_count × balance.json.tick_hz / duration_ticks（当前tick_hz=60）；人工检查导出的接触表，确认姿势差异反映动作本身。小杜ignite只计provenance指定的35个源姿势。
- 皮肤或显示倍率不得影响费用、冷却、移动、伤害、清行数量或胜负结果。
- 使用同一确定性关卡输入时，修改后domain事件/tick与改动前基准中的位置、攻击/伤害、阳光、击杀及最终阶段必须一致。

## Jalapeno row clear event

- 有效种植触发一次现有row_clear_started事件，现有行内僵尸仅按规则结算一次。
- 表现层完整按序展示35个小杜源姿势，目标持续2.0秒，允许1.9–2.1秒。
- 表现播放期间规则时钟继续；结束、暂停或重开服从游戏现有场景/生命周期语义；新会话不可残留旧视觉事件。

## Dog display bounds

- 小宝/小杜草坪主体高度相对当前dogs显示基准至少+15%。
- 所有显示上下文使用角色共用倍率配置，并以帧anchor对齐落点。
- 小宝/小杜倍率唯一存于dogs manifest的wallnut/jalapeno角色元数据；代码公共接口读取该字段，缺省值1.0用于旧manifest兼容，不得在代码中复制倍率值。
- 角色主体在卡片/选肤预览/草坪/拖动预览不裁切；草坪不越逻辑画布；相邻角色主要身体不遮挡。
- 测量基准包括所有必需pose clip，特别是站立、受击、卧倒、种植及喷火姿势。

## Compatibility

保持manifest schema v1的既有必需字段、default/dogs皮肤选择、60Hz模拟、窗口缩放与发行入口。新可选角色缩放元数据须有安全缺省值。任何无法维持此契约的素材或平台结果应在验证报告中明确失败/未验证。
