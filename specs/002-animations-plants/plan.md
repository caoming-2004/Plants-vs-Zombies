# Implementation Plan: 动画、操作与植物扩展

**Branch**: version1 | **Date**: 2026-10-26 | **Spec**: specs/002-animations-plants/spec.md

**Input**: Feature specification from specs/002-animations-plants/spec.md

## Summary

在现有小游戏中加入卡片拖动与放置、新增坚果墙和火爆辣椒、更新小狗角色映射，并为全部适用动作提供至少24个不同姿势/秒。保留60 tick/s玩法模拟与现有点击种植；显示层按窗口实际像素绘制并缓存高密度素材。植物规则统一由Simulation处理，画面只呈现状态与事件。

## Technical Context

**Language/Version**: Python 3.12 x64。

**Primary Dependencies**: pygame-ce 2.5.8；pytest 8.4.2；PyInstaller 6.22.3。版本来自requirements.lock.txt；不增加依赖。

**Storage**: 玩法、关卡和角色动作使用随程序分发的JSON/PNG资源；本特性不引入玩家存档或音频数据。

**Testing**: pytest单元/集成/回放测试；assets清单和独特帧率校验；SDL headless smoke用于确定性渲染；标准Windows显示设备进行性能、拖放及视觉实测。

**Target Platform**: Windows 10/11 x64桌面；完整解压、本机离线运行。

**Project Type**: 现有单项目桌面2D游戏。

**Performance Goals**: 固定玩法60 tick/s；目标显示60 FPS。SC-004标准场景连续60秒平均≥58 FPS，P95帧间隔≤25 ms；关键动作至少24个不同姿势/秒，动画状态每秒更新至少60次。SC-007固定压力场景连续60秒平均≥55 FPS且P95帧间隔≤33 ms；同场景输入事件至首个可见预览P95≤50 ms，20次操作零丢失/重复。

**Constraints**: 保留1050×600逻辑坐标、五行十二列和现有点击种植；仅本行现存僵尸受火爆辣椒清除；新数值仅在balance.json定义；角色视觉不得改变玩法；本轮不做音效；所有资源离线随包并记录来源；狗狗重复循环继续至少60 tick。

**Scale/Scope**: 单个day_01关卡、四种植物、一种普通僵尸、双方独立外观选择的四种组合。新增狗狗对应小宝、黄黄、小杜；向日葵被窝与僵尸嗷嗷嗷保持。

## Constitution Check

| 原则 | 研究前检查 | 设计后检查与证据 |
|---|---|---|
| 完整可玩的核心循环优先 | PASS：现有开始、经济、种植、战斗、胜负和重开流程已存在。 | PASS：新增植物增加防守选择；保留射手/向日葵及既有胜败条件；使用固定胜负回放确认可胜与失败路径。 |
| 规则与界面渲染分离 | PASS：Simulation拥有规则；renderer/input负责展示与命令转换。 | PASS：DragState只在presentation；row_clearer由PlantAt命令触发；动画消费row_clear_started/death事件，不能击杀单位。 |
| 关键数值集中管理 | PASS：balance.json已集中存放植物/僵尸参数。 | PASS：坚果墙50阳光/1200HP/1800tick冷却、火爆辣椒125阳光/3000tick冷却在配置内各定义一次；24姿势、2×素材密度和卡片位置属于呈现/资源元数据，不作为玩法平衡散落常数。 |
| 核心玩法修改必须验证 | PASS：pytest和固定回放已有基础。 | PASS：覆盖角色职责校验、扣费/冷却事务、阻挡/击杀、同tick与spawn边界、输入、视觉事件以及标准设备性能测量。 |
| 新增功能保持已有功能可运行 | PASS：核心环路、铲子、割草机、暂停、胜负、重开和选肤已实现。 | PASS：回归原有规则与US1闭环；测试四种外观和原有点击种植，检查完整资源包及可启动入口。 |

**Gate**: 五项原则均通过，无需宪章例外。

## Current Codebase and Design

当前项目已经有可运行的游戏和严格的domain/presentation边界。本特性只扩展以下位置：

- config.py / assets/config/balance.json：plant角色的role-specific字段验证与四种植物参数。
- domain/simulation.py / systems.py / models.py：持久坚果墙、一次性整行清除、可靠的击杀统计和事件顺序。
- presentation/input.py / scenes.py：四卡几何、拖动手势状态、悬停预览、旧点击种植和目标反馈。
- presentation/renderer.py / animation.py：窗口目标尺寸绘制、高密度素材采样、植物/僵尸动作、一次性火焰效果。
- presentation/skin_catalog.py：角色/动作清单、2×帧元数据、独特帧率和回退验证。
- assets/skins/default 与 assets/skins/dogs：五角色完整矩阵；更新tools/import_dog_assets.py、tools/validate_assets.py和tools/benchmark.py。
- tests/unit、tests/integration、tests/replay：数值/事务、拖放、动作矩阵、性能兼容和外观不变性。

## Implementation Stages

### A. 规则、配置与事件
1. 扩展植物配置角色到producer、shooter、blocker、row_clearer，并按角色校验专属字段。
2. 写入坚果墙与火爆辣椒参数；验证旧配置用例仍合法，未知职责拒绝。
3. 坚果墙创建普通持久Plant并复用同排target/bite逻辑；死亡后占格清除，僵尸恢复移动。
4. 有效PlantAt种植row_clearer时校验占格、余额、冷却，原子扣费并生成row_clear_started；按Zombie ID调用统一damage处理本tick命令时现存僵尸。
5. 固定命令/波次/投射物/攻击/结果先后顺序；本行稍后生成敌人不受伤，死亡单位不会重复受击/啃咬/割草或计数。
6. 实现角色和同tick规则的单元、集成与胜负回放。

### B. 卡片、拖动输入与反馈
1. 统一四卡控件几何，四张卡与铲子/阳光HUD在最低支持画面不重叠且同时可见。
2. 在input层实现press→move→release状态；卡片拖动呈现透明角色、当前格/有效性提示，不向模拟层发送鼠标移动。
3. 松开草坪内格子时发原SelectPlant/PlantAt顺序；Simulation在最终处理时重新验证余额、占格及冷却。
4. 松开在草坪外/HUD、右键/Esc、窗口失焦、暂停或切换场景均清除拖动态并避免双命令；无效格提示中文，保留旧点击种植行为。
5. 在1050×600和1260×720至少覆盖卡片四角、末列、留边、HUD及阳光优先级的可重复交互验证。

### C. 角色素材、高清呈现与动作
1. 完成default/dogs五角色素材角色表；Peashooter狗狗皮肤替换为黄黄，wallnut用小宝，jalapeno用小杜；保留被窝/嗷嗷嗷现有对应。
2. 制作≥2×密度透明源帧，更新来源许可、提示词、动作/锚点/trim及素材manifest；每个适用clip不少于24独特可见帧/秒，狗狗循环仍≥60 tick。
3. 调整Renderer以1050×600逻辑几何直接绘到当前窗口目标像素尺寸，避免整张低分辨率canvas二次拉伸；保持点选区域用原逻辑坐标计算。
4. 缓存converted alpha和目标尺寸缩放面片，缓存有界且皮肤/缩放变更不会复用错误像素；检查透明边、脚底锚点、卡片与HUD清晰度。
5. 为坚果墙制作idle/hit/die；为火爆辣椒制作plant/ignite一次性表现、火焰横扫和完整淡出；相位只关联模拟事件，不产生玩法命令。
6. 自动验证动作矩阵、唯一帧数/速率、loop时长、资源边界、裁切锚点、所有相邻角色轮廓；真实尺寸截图审核经典/狗狗四种组合。

### D. 回归、发行与验收证据
1. 四种appearance replay对比sun/plant/zombie/projectile/kill/result和事件序列；所有皮肤采用完全相同的balance配置。
2. 60秒标准场景与SC-007固定压力场景测量平均FPS、P95间隔、动画采样、可见独特姿势及输入到可见预览延迟；SDL dummy用于自动化，不代替真实窗口SC-004/SC-007验收。
3. 执行正常/失败/取消拖放、两种新植物、首局胜负、暂停/重开以及资源缺失回退场景。
4. 更新quickstart、发行构建配置、来源清单与验收报告；在真实窗口检查用户双击可启动和四卡一屏。
5. 未完成的硬件性能、目标环境运行或人工外观验收记录为NOT_RUN，不以headless smoke替代。

## Project Structure

- specs/002-animations-plants/: plan.md、research.md、data-model.md、quickstart.md、contracts/、tasks.md（tasks.md由speckit-tasks阶段创建）。
- src/pvz_game/domain/: 配置、Plant/Jalapeno命令规则、行清除事件、既有回放规则。
- src/pvz_game/presentation/: 拖动控制状态、四卡UI、高分辨率目标绘制、Animator/素材清单适配。
- assets/config/balance.json：四植物及僵尸的唯一玩法参数定义。
- assets/skins/default/ 与 assets/skins/dogs/：五角色帧、manifest、Provenance与卡片/预览图。
- tests/unit、tests/integration、tests/replay：规则事务、输入、动画清单、渲染、四外观结果不变性。
- tools/: 更新现有资源导入、验证、性能工具；发行仍由packaging/pvz_game.spec与tools/build.ps1控制。

## Complexity Tracking

无宪章例外或新增第三方依赖。高清素材和较多动画帧增加资源容量，风险通过分页atlas、按需加载、alpha surface转换、缩放面片缓存和包体/帧时耗测量处理。

## Risks and Decisions

- **24姿势/秒的素材量**：所有可见角色/动作需足够不同帧，现有12姿势狗狗sheet不能直接作为最终clip。需按动作拆分制作，再逐帧锚点检查；不能以复制帧达到数量。
- **大图集内存/载入时间**：分角色/动作或图集页、按选中的阵营加载、转换和缩放surface复用；测试冷启动并在包内校验文件总量。
- **辣椒与同tick敌人**：按执行PlantAt时已有存活敌人收集目标，击杀事件使用统一函数；之后spawn不会被追溯清除；顺序写在simulation contract并以固定tick回放验证。
- **火爆辣椒威力**：首关经济低，一颗125阳光可以清掉一整行。检查被此道具单独通关的策略；如果明显破坏挑战度，由试玩后的需求修订重新确认，不以皮肤或音效调整规则。
- **原版素材许可**：已有抽取资源记录其来源与非商用说明。新增default角色素材需复用已有许可清晰的参考源或明确标记仅本地测试；正式ZIP不得把未厘清的来源描述成自由授权。
- **性能证据**：当前benchmark结果是SDL dummy下的60.15FPS/17.51ms，不能直接证明新的高清直接绘制方案达到SC-004；最终需标准Windows显示设备实测。
- **需求质量清单**：requirements.md已按本轮三项用户故事和不含音效的范围同步；后续规格变化时须一并更新检查项与通过状态。

## References

- 当前技术证据与替代方案：specs/002-animations-plants/research.md
- 当前用户验收目标：specs/002-animations-plants/spec.md
- pygame-ce smoothscale：https://pyga.me/docs/ref/transform.html
- pygame-ce convert_alpha：https://pyga.me/docs/ref/surface.html
