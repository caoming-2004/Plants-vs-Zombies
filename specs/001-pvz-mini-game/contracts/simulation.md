# Simulation Contract

## 边界

Simulation(config, level) 提供 step(commands) → snapshot, events。
模拟层仅依赖标准库和已验证数据，不导入pygame、不读取皮肤、系统时间或真实鼠标。
快照只读，渲染不得反写。输入命令包含session_id、tick、顺序号，拒绝旧局命令。
单线程执行命令与模拟；同tick命令按顺序逐个校验，重复点击不会双扣或双收集。

## 命令

Start、SelectPlant(type_id)、SelectShovel、CancelSelection、PlantAt(row,col)、
ShovelAt(row,col)、CollectSun(id)、Pause、Resume、Restart、ReturnToMenu、Quit。
SetAppearance(plant_skin_id,zombie_skin_id)属于menu的app层状态，不进入战斗数值计算。
命令返回accepted或稳定reason_code，例如insufficient_sun、cooldown、occupied、out_of_bounds、wrong_phase、stale_session。
UI负责将代码映射成中文。不能把命令异常当作正常失败反馈。

## Tick执行顺序

1. 以当前tick=t顺序处理命令及阶段变化；CollectSun必须先检查t < expires_tick，t >= expires_tick返回sun_expired且不增加余额（即使对象尚未清理）；非playing立即返回，不推进时间。
2. 生成本tick波次与阳光，清理t >= expires_tick的阳光；记录tick开始时已有投射物ID集合，更新存活僵尸目标并推进移动，随后计算植物行动周期。新生成阳光在本次命令阶段之后出现，最早下个tick收集。
3. 先移动步骤2记录的已有投射物（previous_x保存移动前位置），按投射物ID升序以移动线段命中同排最近存活目标，距离相同时按目标ID升序；命中即应用伤害并标记死亡。再由存活植物按ID升序执行产出/射击，新投射物生成在逻辑发射点，出生tick不移动也不命中。最后由存活僵尸按ID升序重新校验接触目标并结算到期啃咬；已被投射物消灭的僵尸不能啃咬，死亡植物不再接受后续啃咬。每次伤害立即更新生命与逻辑死亡状态。
4. 检查存活僵尸触发ready割草机；推进割草机并以扫描线段消灭沿途接触的存活僵尸。
5. 清理逻辑死亡与失效对象；检查无救场能力的越界存活僵尸，成立即lost；否则波次耗尽且无存活僵尸为won。
6. 本次事件标记已处理tick=t及唯一(session_id,event_seq)；模拟tick推进为t+1后输出只读快照，snapshot.tick表示下次要处理的tick。结算只发一次。

割草机触发线与失败线在配置中分别命名，触发线在失败线右侧；清扫期间仍可能有未被扫到的后续僵尸突破。
投射物/割草机采用连续线段碰撞，避免帧间跨越目标漏判。无随机出怪；回放包含配置摘要和命令序列。

## 时间与动画

app以单调计时累计时间，每次模拟固定1/60秒；单次最多追赶5步，极长阻塞丢弃多余积压，避免恢复窗口后突进。
暂停清空累计量。展示允许插值但不反向驱动模拟。
模拟事件包含action_started、shot、sun_created、bite、hit、died、mower_started、result。
action_phase按规则周期提供，皮肤帧映射到相同相位；更换帧数和帧时长不能改变射击/啃咬/产出的时刻。
外观动画只读取模拟tick/事件；重复动画的视觉循环时长至少60 tick，呈现侧采样至少30Hz、绘制目标60FPS。
采样、插值或动画循环不得创建、推迟或取消玩法事件。30/60FPS回放对比相同输入时，状态摘要和事件序列必须一致。
测试回放直接按tick执行，比较不含外观字段的状态摘要及完整玩法事件序列。

## 时间边界验收

- expires_tick=100时，tick=99收集成功；tick=100或101收集均拒绝且余额不变；重复收集不能再次入账。
- 同一到期边界在暂停/恢复后仍以模拟tick判定，不使用墙钟时间；暂停期间收集仍返回wrong_phase。
- 已有投射物先命中致死的僵尸本tick不能啃咬或触发割草机；新发投射物本tick保持发射点，下tick才移动和命中。
- 至少覆盖线段跨越目标、同距离目标、两个投射物竞争同一目标，以及本tick新生成投射物的行为；30/60FPS回放事件tick与结果一致。