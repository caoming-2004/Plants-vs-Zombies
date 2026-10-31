# Implementation Plan: 狗狗外观与玩法体验优化

**Branch**: `010-dog-gameplay-polish` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-dog-gameplay-polish/spec.md`

## Summary

在现有 Python/Pygame 桌面架构上完成被窝、嗷嗷嗷的全身显示与朝向修正，被窝产阳光短弧跳出，拖动植物预览连续跟手并按唯一最近格校验；在现有外观页中明确展示胖宝宝、黄黄两个独立角色，并将单关升级为三类僵尸、三阶段递增波次。继续由 `Simulation` 持有玩法状态，`assets/config` 集中平衡数值，`assets/levels` 保存出怪和波次节奏；不引入新框架、联网服务、手机端或多关卡系统。

## Technical Context

**Language/Version**: Python 3.12.x（项目声明 `<3.13`）

**Primary Dependencies**: pygame-ce 2.x；发行构建使用已有 PyInstaller 6.x，不加依赖。

**Storage**: 本地 JSON；植物/僵尸数值在 `assets/config/balance.json`，关卡波次在 `assets/levels/day_01.json`，皮肤表现继续用现有 manifests/atlases。

**Testing**: 项目现有 pytest；仅运行本功能相关的规则、拖放、渲染/素材、胜负/重开用例，随后进行一次标准窗口帧时间验收和一次发行 EXE smoke；不跑全量 pytest、压力矩阵或六种皮肤组合矩阵。

**Target Platform**: Windows 桌面版；Android/iOS 明确不属于本次。

**Project Type**: 离线单窗口桌面塔防游戏。

**Performance Goals**: 维持固定 60 Hz 模拟和既有植物 12–18 个可辨动作姿势/秒；标准场景连续 10 秒至少 95% 的帧间隔不超过 20 ms，且无超过 100 ms 的非预期停顿；拖动预览逐帧跟随。

**Constraints**: 保留 1050×600 逻辑画布、5×12 草坪和现有单关完整胜负循环；外观资源继续来自已安装图集；新增僵尸通过现有角色动作图集加轻量可辨提示呈现；被占最近格拒绝且不自动改放；无新模式、联网、移动端适配或额外 ZIP。

**Scale/Scope**: 1 张关卡；普通、快速、高耐久 3 类僵尸；至少 3 个递增波次；只触及输入、表现、关卡配置、模拟和少量对应验收。

## Constitution Check

| 原则 | 状态 | 计划依据 |
|---|---|---|
| I. 完整可玩的核心循环优先 | PASS | 保留资源、种植、战斗、波次、胜负、重开/返回流程，MVP只扩现有单关。 |
| II. 游戏规则与界面渲染分离 | PASS | 放置候选与校验由输入适配加既有 `placement_reason`/Simulation 负责；僵尸、波次、阳光运动状态由 `Simulation`/systems 持有；Renderer 只读快照和事件。 |
| III. 关键数值集中管理 | PASS | 敌人生命、速度、啃食参数写 `balance.json`；出怪 tick、波次顺序和行写 `day_01.json`，配置校验集中在 `config.py`。 |
| IV. 核心玩法修改必须验证 | PASS | 仅对这次新增规则执行小规模定向测试，另做一轮实际窗口观察、可赢/可输/重开回归和发行包 smoke；未执行项如实记录。 |
| V. 新增功能保持已有功能可运行 | PASS | 保持点击种植、旧皮肤、植物职责和本地发行路径；用定向旧规则回归和正式包启动检查确认。 |

**Gate**: 全部通过，无需宪章例外或新增抽象层。

## Phase 0: Research Decisions

详见 [research.md](research.md)。已通过 010 clarify 解决平台范围和最近格占用行为；不存在待决的产品问题。具体 HP/speed 和每波出怪 tick 属于平衡配置，在实现中采用保守的初始数值，并通过一局可赢回放微调。

## Phase 1: Design & Contracts

- [data-model.md](data-model.md)：定义复用/扩展的敌人类型配置、波次、阳光弹跳轨迹和拖动候选状态。
- [contracts/interaction.md](contracts/interaction.md)：定义玩家可见的拖放、阳光、外观入口和波次提示行为。
- [quickstart.md](quickstart.md)：列出最小必需的定向验证、一次标准窗口测量和正式包 smoke 步骤。

## Project Structure

### Documentation (this feature)

```text
specs/010-dog-gameplay-polish/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── interaction.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # 后续 $speckit-tasks 生成
```

### Source Code (existing single project)

```text
assets/
├── config/balance.json
├── levels/day_01.json
└── skins/{dogs,dogs_photo}/manifest.json
src/pvz_game/
├── config.py
├── domain/{models.py,simulation.py,systems.py,plant_rules.py}
└── presentation/{animation.py,input.py,renderer.py,scenes.py,skin_catalog.py}
tests/
├── unit/{test_config_and_models.py,test_combat_and_lifecycle.py}
├── integration/{test_animation.py,test_drag_input.py,test_playable_loop.py,test_skin_selection.py}
└── replay/test_base_replay.py
tools/benchmark.py
packaging/pvz_game.spec
```

**Structure Decision**: 复用现有单一 Python 项目；不新增应用子项目或依赖层。`Simulation`/systems 是规则权威，input 将物理鼠标位置映射到逻辑坐标并发命令，Renderer 处理预览、朝向、图集和提示，已有配置负责平衡。内部 Pygame 桌面游戏没有对外 API，contract 仅记录玩家可见交互，不新增网络或 IPC 协议。

## Design Decisions

1. **完整显示与朝向**：仅调低 `dogs`/`dogs_photo` 中 `sunflower` 与 `zombie_basic` 的角色比例；继续用 alpha 可见边界 `fit_visible_frame` 校准。嗷嗷嗷的朝向用表现层的缓存水平镜像处理，翻转透明裁切偏移和锚点时仍以完整画布为基准；不改变僵尸在模拟中的左移方向。
2. **被窝阳光跳出**：从被窝当前可见身体内/邻近处作为起点，目标落点仍在同一行草坪附近；在 `SunPickup` 中以确定性轨迹参数表达短弧跳，运动位置继续由模拟快照提供，渲染和点击使用同一坐标。天空阳光轨迹、价值、寿命和暂停规则不变。
3. **连续拖放**：保留 `DragState.pointer` 的连续逻辑坐标，Renderer 不再把预览主体强制移到 hover cell 中心；hover cell 只用于候选格颜色/有效性反馈。释放时按网格中心最近格选唯一候选；等距边界使用确定性 tie-break。复用 `placement_reason` 和原拒绝原因，不向相邻空格重定向。
4. **胖宝宝/黄黄入口**：在既有外观菜单中补充两张可单独点选的角色预览卡及原职责标签；点选只切换菜单中的预览焦点，不代表选择对局角色皮肤，狗狗卡通外观选择仍沿用现有全局皮肤按钮；进入对局后它们仍是 `pangbaobao`、`huanghuang` 两张独立功能卡，不为其他植物建立皮肤覆盖或替换关系。预览复用 `Catalog.preload_async('dogs')`，图集未就绪时画加载占位，不同步解码图集或阻塞输入。
5. **敌人和波次**：在 balance JSON 增加 `zombie_fast` 与 `zombie_tough` 配置（快型较快、耐久型更耐打且较慢；具体值作为单一配置初值），在 `day_01.json` 增加三段渐进波次及各波出怪列表/时点。模拟生成事件中保留独立 type ID 和统计数值，表现层把三种敌人映射到现有 `zombie_basic` 狗狗动作素材，并使用轻量速度/护甲标记区分；HUD/波次提示读取快照，不在 UI 重复推算波次。普通敌人、冰冻、爆炸、割草机、失败和最后清怪胜利仍沿用现有系统。
6. **发行与测试规模**：只构建一个 `v0.6.0` 正式目录包并做一次狗狗外观可玩 smoke；不创建 ZIP。用 PyInstaller 直接构建后复制现有启动说明与字体许可，移除本轮 staging `build/PvzMiniGame-v0.6.0`，保留正式 `dist` 发行目录。

## Focused Validation Plan

只覆盖这次改动的直接风险：

1. Dog animation：两种外观下全身 alpha bounds、缩放和嗷嗷嗷各动作左向；菜单两个新增角色项可显示。
2. Drag input：连续预览；格中心、格边及等距边界按稳定 tie-break 选择唯一最近格；占用格、其他无效格和草坪外释放均拒绝，且阳光/冷却不变。
3. Domain rules：三类僵尸的配置和移动/耐久差异；波次顺序/提示状态；清空后胜利、失败、重开状态归零。
4. Sun loop：被窝来源起点和弧线，移动位置仍可收集且余额只结算一次；暂停与过期沿用现有规则。
5. Core flow and release: 定向回归确认胜负、重开和结果页返回菜单；一次标准场景 10 秒窗口记录、一次 PyInstaller 目录包启动/渲染 smoke。避免全量测试、压力场景、长时输入时延矩阵和多种子组合重复打包。

**Post-design Constitution Check**: 全部五项仍 PASS；没有原则冲突或需记录的复杂度例外。

## Complexity Tracking

无宪章违规；无新增复杂抽象、依赖或项目层级。

