# Research: 阳光界面、拖铲操作与小狗动作素材

日期：2026-10-26。研究范围为当前仓库已有实现和本功能规格，不引入外部服务或新运行时依赖。

## Decision 1: 阳光余额在共享逻辑UI矩形中改位

**Decision**: `src/pvz_game/presentation/scenes.py` 继续作为按钮与HUD命中区域的单一来源；将共享阳光HUD矩形从当前右上区移到左上角，`renderer.py`在该矩形绘制图标和`Simulation.snapshot()['sun']`，`input.py`仍用同一矩形阻止草坪/拾取穿透。拖动预览的遮挡检测也引用同一矩形。

**Rationale**: 现有真实余额只保存在`Simulation.sun`，snapshot已经供渲染读取；改UI坐标不需要复制/迁移领域状态。首张植物卡从逻辑x=162开始，左上角余额框可放在其左侧并保持非重叠。事件输入使用逻辑坐标，窗口缩放和留边转换无需更改。

**Alternatives considered**: 把阳光余额放入植物卡槽或复制一份HUD资源状态。前者挤占四张卡片，后者制造第二个可能过期的余额来源，因此不采用。

## Decision 2: 统一植物卡和铲子拖动的Presentation状态

**Decision**: 在`presentation.input`中扩展当前`DragState`以表达植物工具或铲子工具；`app.py`将植物卡和铲子按下/移动/释放/失焦/暂停/结算事件路由到同一拖动态接口；`renderer.py`绘制植物幽灵预览、有效格反馈和铲子目标反馈。点击选择路径继续用既有命令。

**Rationale**: 当前植物拖动已经通过`begin_drag`、`update_drag`、`finish_drag`运行，逻辑层已有`SelectShovel`和`ShovelAt`，`Simulation.command()`完成唯一移除结算。扩展Presentation比增加规则状态或新命令更小，也符合宪章第二原则。

**Alternatives considered**: 单独增加铲子拖放子系统或直接在Renderer中移除植物。前者会复制输入生命周期；后者把规则从Domain移到显示层；均不采用。

## Decision 3: 60帧素材接入现有manifest与Animator

**Decision**: 保留dogs的manifest schema v1、`skin_catalog.REQUIRED`的五角色动作集合、图集采样、`Animator`按tick播放、阵营级回退及现有来源记录。针对上传文件的真实版式调整`tools/import_dog_assets.py`，把小宝、小杜源帧映射到现有`wallnut`/`jalapeno` clips；保存原始图片，并在provenance/source refs记录来源和SHA-256摘要。不能靠重复帧伪装素材数量。

**Rationale**: 运行时已经按role+clip查找帧并依manifest anchor定位，完整清单检查和回退行为已存在；仅替换源帧/导入内容可以避免改变换肤和游戏规则。

**Alternatives considered**: 为小宝和小杜新增独立角色runtime schema、在渲染器里硬编码图片路径、或继续把新资源写成内置imagegen素材。它们会破坏清单一致性/回退，或错误标注用户来源，因此不采用。

**素材检查结果**: 已接收`xiaodu-user-60.png`与`xiaobao-user-60.png`，两图为1619×971 RGBA透明PNG，按10列×6行切分，每图60格；逐格检查得到60个不同源像素帧。小杜火焰喷射区主要在中间行，小宝由站立/行走逐渐过渡到坐下/卧倒。导入后每帧保留角色与源序号，插值帧记录相邻原帧编号；源图SHA-256写入provenance和sources登记。

**兼容门槛**: 继承自`specs/002-animations-plants/spec.md` FR-010的关键动作验收要求：各适用clip至少24个不同可见姿势/秒，循环clip至少60个模拟tick；现有`tools/validate_assets.py`执行相应资源检查；manifest还须通过锚点、透明轮廓及邻格检查。小宝源帧按0–19待机循环、20–29受击、30–59卧倒结束分组；小杜按0–9种植/待机、10–44喷火、45–51受击、52–59结束分组。相邻动作帧间插值用于满足姿势速率，插值输出追溯原帧；不重复帧充数。

## Decision 4: 验证采用自动逻辑检查与真实窗口分层

**Decision**: 自动测试覆盖共享HUD命中优先级、点击和拖放命令等价、工具拖动态状态、每次释放命令数、domain扣费/冷却/铲除结果、皮肤回放不变量和素材验证。SC-004的响应测量固定为Windows 60Hz设备、1260×720真实窗口、普通对局、至少200个实际拖动鼠标移动样本；起点为程序取出鼠标移动事件，终点为首次显示对应更新预览的画面。真实桌面试玩还核对左上角布局、取消/失焦/暂停及帧序观感。构建与移动路径包检查保持现有on-dir发行流程。

**Rationale**: pygame的headless测试能确定命令和坐标规则，但不能证明真实指针反馈和视觉连续性；分层证据避免把模拟环境误当作人工窗口验收。

**Alternatives considered**: 仅以单元测试或仅以截图验收。前者不足以覆盖输入与素材视觉，后者难以可靠核验计费和无重复操作，因此两者组合。


