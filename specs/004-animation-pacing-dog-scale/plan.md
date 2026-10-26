# Implementation Plan: 动画节奏与小狗显示尺寸调整

**Branch**: version1 (current Git branch) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: [Feature specification](spec.md)

## Summary

复用当前60Hz模拟、manifest驱动帧时长、Animator表现层、稳定锚点绘制及清行视觉事件架构，调整所有必需clip的姿势呈现节奏到12–18个可辨认姿势/秒。表现层播放时钟独立于游戏规则结算，default与dogs皮肤同一组输入必须产生完全相同的模拟结果。小杜清行特效从现有帧清单挑选并按序呈现35个源姿势，分配约120个60Hz tick，完整播放2.0秒。小宝、小杜草坪显示尺寸提高至少15%；共用缩放策略扩展到卡片、预览、拖动预览、死亡与特效显示，并用既有锚点和不重叠验证约束裁切与遮挡。

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: pygame-ce 2.5.8; pytest 8.x for existing project verification; PyInstaller 6.x for existing Windows packaging  
**Storage**: 本地 JSON 配置与素材manifest、PNG图集；不新增持久化状态  
**Testing**: 复用 pytest 单元/集成/回放测试、素材验证器、动画预览和既有窗口/打包冒烟流程  
**Target Platform**: Windows x64 桌面；运行与素材离线随包  
**Project Type**: 单体 Python 桌面游戏，simulation domain 与 pygame presentation 分层  
**Performance Goals**: 保持60 tick/s模拟与60FPS目标呈现；所有循环及一次性动作的姿势速率在12–18/s；小杜清行特效2.0±0.1s；不降低既有核心循环可玩性  
**Constraints**: 不改攻击、移动、伤害、冷却、资源、死亡和胜负规则时序；无新增第三方运行依赖；动画遵守暂停与重开生命周期；放大后不裁切主体或造成相邻角色主要身体重叠  
**Scale/Scope**: default/dogs两种完整皮肤，skin_catalog.REQUIRED中的所有动作clip，以及小宝/小杜在草坪、卡片、预览和拖动预览中的显示路径

## Constitution Check (before design)

- **I. 完整可玩的核心循环优先**: PASS — 不新增玩法阶段，不阻塞核心循环；爆炸视觉延长与规则清行分离。
- **II. 规则与渲染分离**: PASS — 攻击/伤害/胜负仍由domain权威处理；姿势节奏、特效寿命和角色大小属于presentation/素材manifest。
- **III. 关键数值集中管理**: PASS — 12–18姿势/s范围由具名presentation常量提供，模拟tick频率读取assets/config/balance.json的tick_hz；小宝/小杜倍率只存dogs manifest角色元数据，animation.py仅提供统一读取入口。
- **IV. 核心玩法修改必须验证**: PASS — 本方案不改玩法规则；增加表现与模拟结果一致性回放验证及真实尺寸/暂停/生命周期集成验证。
- **V. 新增功能保持已有功能可运行**: PASS — 保留动画清单schema、经典/狗皮肤回退、锚点机制、既有玩法及打包入口；执行核心循环与两套皮肤回归。
- **依赖与结构约束**: PASS — 复用现有模块，不新增外部依赖或新运行时子系统。

## Constitution Check (post-design)

- **I** PASS — 清行规则当帧只结算一次；展示特效持续约2秒而不冻结或延迟对局。
- **II** PASS — Simulation与命令契约不承担展示插值；Animator不写回领域状态。
- **III** PASS — clip时间由manifest duration_ticks表达；小宝/小杜倍率唯一存于dogs manifest角色元数据，animation.py的共享接口读取该值，所有显示上下文共用接口。
- **IV** PASS — 验证覆盖姿势速率、爆炸开始/结束、暂停与重开、锚点/裁切/占位、以及皮肤切换下逐tick模拟回放等影响面。
- **V** PASS — 保留已有包结构、皮肤数据兼容、游戏输入和重新开始行为；quickstart列出核心回归和发行验证。

## Design Decisions

1. **动画速度以帧清单的模拟tick时长表达。** 60Hz是唯一时间基准，渲染每次根据当前tick采样manifest，不使用独立累加器，避免掉帧和暂停/恢复造成漂移。
2. **按定义明确的不同可见姿势速率验收。** 素材验证器将manifest帧解码为RGBA，像素内容完全相同的帧合并计数，姿势率为唯一姿势数×balance.json的tick_hz/clip总tick数；导出的接触表另做人工动作姿势检查。统一门槛12–18/s，循环动作同时保留完整循环时长要求。小杜ignite严格按provenance的35个源姿势计数，不把生成中间帧纳入源姿势数。
3. **受击是表现动作而非领域状态。** 继续消费既有hit事件，在Animator内保存开始tick并播放角色hit clip；受击表现结束后回归当前基础/攻击动作。受击反馈的延长不得改写领域伤害、攻击周期、死亡或命令。
4. **清行一次性结算、视觉独立计时。** 继续消费row_clear_started事件并由Animator管理视觉生命周期。选取小杜素材明确的35个源姿势，按原顺序、约每帧3–4 tick展示；总时长约120 tick，规则清除维持原事件点且仅一次。效果自然结束、暂停时冻结、会话改变时清空。
5. **角色大小由dogs manifest角色元数据唯一驱动。** 小宝和小杜的display_scale_multiplier只存入dogs manifest各自role对象；animation.py提供公共读取接口，以现有DOG_SCALE乘该倍率得到最终比例。代码常量不保存每个角色的倍率值，旧manifest字段缺省按1.0兼容。所有上下文使用同一接口；沿用manifest anchor和trim_offset，校验使用最终倍率，卡片/预览按可视框fit并保留全身。
6. **兼容现有素材清单。** 保留manifest schema v1和duration_ticks字段；如需增加可选显示比例元数据，旧清单缺省行为与当前表现相同。default与dogs保持同一动作/帧接口，不加运行依赖。

## Project Structure

### Documentation (this feature)

    specs/004-animation-pacing-dog-scale/
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    ├── contracts/
    │   └── animation-presentation.md
    └── tasks.md                 # 下一阶段 speckit-tasks 生成

### Source Code (reuse existing structure)

    src/pvz_game/
    ├── domain/
    │   ├── simulation.py        # 规则时钟、玩法结果；预期保持无行为变更
    │   └── systems.py           # 移动/攻击/伤害/清行规则；预期保持无行为变更
    └── presentation/
        ├── animation.py         # frame_at、Animator、特效生命周期、缩放/锚点共用绘制
        ├── renderer.py          # 草坪、卡片、预览、拖动预览等显示上下文
        ├── skin_catalog.py      # manifest角色元数据和必需clip验证
        └── dog_validation.py    # 小狗角色尺寸、脚底与相邻角色边界验证

    assets/skins/
    ├── default/manifest.json    # 经典动作帧时长
    └── dogs/manifest.json       # 狗角色帧时长及小宝/小杜展示倍率

    tests/
    ├── unit/                    # 纯规则结果不变量
    ├── integration/             # clip速率、Animator、渲染边界、爆炸时长
    └── replay/                  # 换肤前后模拟行为一致性

    tools/
    ├── validate_assets.py       # 全clip姿势速率及素材验证
    ├── preview_animations.py    # 两套皮肤逐动作预览
    └── benchmark.py             # 最坏场景呈现性能

**Structure Decision**: 这是现有Python桌面单体项目；本Feature只扩展既有presentation、manifest素材清单、校验工具与测试，不新增项目根、框架或运行时子系统。领域层保持规则权威。若实现发现领域修改不可避免，须先同步规格与契约并证明必要性。

## Complexity Tracking

无宪章偏离，无新增依赖或项目边界。
