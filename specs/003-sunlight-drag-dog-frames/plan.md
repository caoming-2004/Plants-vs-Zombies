# Implementation Plan: 阳光界面、拖铲操作与小狗动作素材

**Branch**: `version1` | **Date**: 2026-10-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-sunlight-drag-dog-frames/spec.md`

## Summary

本功能在现有单进程 Windows 桌面游戏上调整阳光余额的位置，并扩展玩家输入：植物卡和铲子均可拖放，原有点击操作保留。小宝（坚果墙）和小杜（火爆辣椒）的用户提供动画素材接入现有 dogs 皮肤资产链。实现复用固定逻辑画布、`scenes.py` 共享几何、Presentation 拖动态、Domain 命令及现有 manifest/Animator；不新增玩法规则或运行时依赖。素材检查确认两张透明PNG均为10列×6行、每张60个不同姿势，分别映射小杜→火爆辣椒、小宝→坚果墙；帧序、动作组和脚底锚点按实际画面记录。

## Technical Context

**Language/Version**: Python 3.12.x。

**Primary Dependencies**: pygame-ce 2.5.x；测试使用 pytest 8.x；发行构建使用 PyInstaller 6.x。功能实现不需要新增依赖。

**Storage**: 无运行时数据库。游戏平衡配置、关卡和外观清单为随包 JSON；角色源图、图集与界面资源为随包文件。

**Testing**: pytest 单元/集成/replay 测试；`tools/validate_assets.py` 资源清单、动画速率与轮廓检查；真实窗口手动拖放/视觉检查；`tools/build.ps1` 和 `tools/verify_bundle.py` 发行回归。

**Target Platform**: Windows 10/11 x64 桌面，离线运行；逻辑画布 1050×600，窗口可调整但有最小尺寸。

**Project Type**: 单项目桌面游戏。

**Performance Goals**: 沿用现有 60 tick/s 模拟与 60FPS 绘制目标；按SC-004在Windows 60Hz设备、1260×720真实窗口、普通对局中采集至少200个拖动中的实际鼠标移动样本，从程序取出事件到首次显示对应预览的P95 ≤50ms；三种受支持窗口尺寸均能完整显示左上角余额。新资源继续通过 `specs/002-animations-plants/spec.md` FR-010 的关键动作至少24个不同可见姿势/秒门槛及既有狗狗循环长度检查。

**Constraints**: 规则状态归 `Simulation`，拖动态和可视反馈只归 Presentation；输入命令复用既有 `SelectPlant`、`PlantAt`、`SelectShovel`、`ShovelAt`。阳光余额读取 `snapshot['sun']`，不复制一份界面状态。用户原图原样保留；插值帧记录相邻源帧索引，不复制姿势填数或混用另一角色素材。

**Scale/Scope**: 现有关卡为 5 行×12 列、四种植物、一局单用户；改动范围为一块HUD区域、两个Presentation输入源（植物卡/铲子）、两个 dogs 角色的完整要求动作集及发行资产。保持游戏规则、阳光经济和对局配置不变。

## Constitution Check

| 原则 | Gate | 方案符合性 |
|---|---|---|
| I. 完整可玩的核心循环优先 | PASS | 本功能不改核心规则；HUD和拖放直接服务收集/种植/防线调整。Quickstart要求回归完整开局、资源、胜负及重开。 |
| II. 游戏规则与界面渲染分离 | PASS | `scenes.py`共享界面几何；`input.py`负责目标预览与命令生成；`Simulation.command()`仍是费用、占格、冷却和铲除的权威结算；`renderer.py`只读snapshot并绘制。 |
| III. 关键数值集中管理 | PASS | 不改价格、生命、伤害或冷却；布局尺寸集中在UI共享几何，拖放阈值若需新增则以具名Presentation常量管理，不成为玩法配置。 |
| IV. 核心玩法修改必须验证 | PASS | 计划覆盖拖放成功/失败/取消、阳光HUD点击优先级、铲除及旧点击路径；涉及渲染/输入的验收包含自动集成检查和真实窗口步骤，实际结果需如实记录。 |
| V. 新增功能保持已有功能可运行 | PASS | 回归阳光收集、点击种植/铲除、四卡、割草机、暂停、胜负、重开、换肤、皮肤回退与可执行发行包。 |

无原则豁免或新增复杂度。素材适配的具体切片映射只在收到图片后决定，不阻塞HUD/拖放设计；素材验收必须等输入文件到位。

## Project Structure

### Documentation (this feature)

```text
specs/003-sunlight-drag-dog-frames/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── interaction.md
└── tasks.md                 # 后续由 $speckit-tasks 生成
```

### Source Code (repository root)

```text
src/pvz_game/
├── app.py                                  # pygame事件路由、拖动态生命周期
├── domain/
│   ├── commands.py                         # 复用现有命令结构
│   └── simulation.py                       # 权威执行现有种植/铲除命令，不增加规则
└── presentation/
    ├── scenes.py                           # HUD区域与卡片/铲子共享逻辑坐标
    ├── input.py                            # 通用植物/铲子拖动态和目标预览输入
    ├── renderer.py                         # 左上角阳光HUD及植物/铲子拖动预览
    ├── animation.py                        # 既有tick动画和锚点绘制
    └── skin_catalog.py                     # 继续校验现有dogs清单格式和角色覆盖

assets/skins/dogs/
├── source/                                 # 用户上传的原始小宝/小杜帧，保留来源
├── atlas.png                               # 导入后随包的图集
├── manifest.json                           # 既有schema中的角色、clip和锚点
└── provenance.json                         # 用户来源、文件摘要及素材处理记录

assets/sources.json                          # 素材来源注册

tools/
├── import_dog_assets.py                     # 依实际上传版式适配导入，不预设输入切片格式
├── validate_assets.py                       # 既有帧率/循环/资源检查
└── benchmark.py                             # 帧率及输入响应测量

tests/
├── unit/
├── integration/
│   ├── test_playable_loop.py                # HUD优先级和整体输入回归
│   ├── test_drag_input.py                   # 植物卡/铲子拖动态与取消
│   ├── test_asset_manifest.py               # 角色/清单/缺失回退检查
│   └── test_animation.py                    # 动画帧与锚点检查
└── replay/
    └── test_skin_invariance.py              # 外观不改变玩法结果
```

**Structure Decision**: 继续使用现有单一 `src/pvz_game` 项目，不新增前后端、Domain实体或运行时包。应用事件循环负责启动/取消拖动；`presentation.input`扩展已有 `DragState`；所有鼠标命中共用 `scenes.py` 坐标；Renderer通过既有只读游戏快照显示余额与预览。小狗素材归入现有 `assets/skins/dogs` manifest/atlas/来源记录，不另建第二套运行时资源加载机制。测试扩展到现有 `tests/unit`、`tests/integration` 和 `tests/replay`。

## Design Decisions

1. **阳光余额只移动表现层**：将 `HUD_SUN_RECT` 定位于逻辑画布左上角，与首张卡片左缘（x=162）留出间隔；绘制、鼠标命中屏蔽和拖动遮挡计算引用同一共享矩形。余额始终取 `snapshot['sun']`，草坪阳光实体及其拾取规则不动。
2. **植物/铲子共用表现层拖动态**：将现有植物专用拖动态推广为当前工具（植物类型或铲子）的拖动态。按下来源控件建立候选，移动更新逻辑指针和目标；落到草坪格后，根据当前snapshot显示有效状态。有效释放按序提交已有选择命令与`PlantAt`/`ShovelAt`，Domain再次校验。释放到来源按钮保持其点击选择行为；无效位置、取消、失焦、暂停和结算均不发送放置/移除命令。铲子拖动只针对释放时仍存在的植物，且不返还阳光。
3. **复用外观运行时格式**：小宝对应`wallnut`（`idle/hit/die`），小杜对应`jalapeno`（`plant/ignite/hit/die`）。保留既有`Skin`、atlas、manifest schema v1、`Animator`和整套回退。导入器按已检查的10×6 PNG版式整理原帧，保留源图并记录摘要；插值帧附带源帧索引。沿用既有资产完整性、动画姿势速率（`specs/002-animations-plants/spec.md` FR-010：至少24个不同可见姿势/秒）、狗狗循环长度（至少60个模拟tick）、锚点/邻格不重叠检查。
4. **素材输入门**：两角色素材已上传并检查为各60帧透明拼图。导入清单保存原图哈希、每个clip的源帧范围及输出帧到源帧索引；若动作连续性或姿势速率不合格，记录具体缺口，不以另一角色素材替代。

## Post-Design Constitution Check

| 原则 | Gate | 设计复核 |
|---|---|---|
| I. 完整可玩的核心循环优先 | PASS | 以既有可玩循环为回归基线，变更只改善资源可见和操作方式。 |
| II. 游戏规则与界面渲染分离 | PASS | Domain不获得新的显示或鼠标状态；UI目标预览可读状态但不承担最终判定。 |
| III. 关键数值集中管理 | PASS | 不改玩法数值；HUD与卡片几何共享定义，素材帧时长留在manifest而非散落代码。 |
| IV. 核心玩法修改必须验证 | PASS | contracts与quickstart定义输入、边界和实机步骤；pytest与资源工具负责自动验证，不能把headless结果当作鼠标目视验收。 |
| V. 新增功能保持已有功能可运行 | PASS | 保留点击操作、原规则、整套外观回退和可双击发行结构。 |

## Complexity Tracking

无宪章偏离；没有新增项目层、数据库、服务或运行时依赖。






