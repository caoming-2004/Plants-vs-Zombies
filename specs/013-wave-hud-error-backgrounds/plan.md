# Implementation Plan: 波次 HUD 修复、通关稳定性与高清可切换背景

**Branch**: `013-wave-hud-error-backgrounds` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/013-wave-hud-error-backgrounds/spec.md`

## Summary

在现有 Python 3.12 + pygame-ce 架构上增量修复三件事：把波次/关卡状态从草坪上方浮动面板移到顶部 HUD 状态条；复现并修复第一关结算/下一关流程的报错，确保结算、重试、返回和进度保存稳定；新增日间、夜间、黄昏三套高清背景和主菜单背景选择，选择本机保存、运行时离线。

不引入第二套引擎、新运行时依赖或新玩法；背景素材采用真实感/高级感摄影或写实渲染（允许开发阶段联网检索授权高清照片），不使用幼稚卡通图片，最终全部随 Windows 包提供。验证只保留 HUD 截图、20 次第一关结算流程、背景切换/回退、少量定向 pytest 和一次基准，不跑全量矩阵或安卓。

## Technical Context

**Language/Version**: Python 3.12.15（项目现有版本）

**Primary Dependencies**: pygame-ce 2.5.8；Windows 打包沿用 PyInstaller 6.x；运行时不新增依赖

**Storage**: 现有 JSON 资源；新增 `assets/backgrounds/` 高清素材与清单；背景偏好写入现有 `%LOCALAPPDATA%\PvzMiniGame\progress.json` 的设置区，读取失败回退默认

**Testing**: 定向 pytest + headless 结果流程 harness + 1050×600/1920×1080 截图 + 一次标准基准；不跑全量矩阵

**Target Platform**: Windows x64 桌面版；安卓不在本轮范围

**Project Type**: 单机离线桌面游戏（单一 Python 包）

**Performance Goals**: 标准场景平均不低于 58 帧/秒、95% 帧间隔不超过 18 毫秒；背景切换和 2560×1440 素材加载不造成可见长时间停顿

**Constraints**: 1050×600 逻辑画布、五行十二列；顶部 HUD/安全区不放草坪；背景运行期离线；不改变玩法数值/碰撞/点击区域；背景素材来源和授权可追溯

**Scale/Scope**: 1 个 HUD 状态条、1 条第一关结算/下一关流程、3 套高清背景、1 个背景选择菜单；不新增关卡/角色/模式

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原则 | 状态 | 计划依据 |
|---|---|---|
| I. 完整可玩的核心循环优先 | PASS | 先修复 HUD 遮挡和第一关结算报错，保证开局→战斗→胜利→下一关/重开→进度保存完整；背景在可玩路径稳定后接入。 |
| II. 游戏规则与界面渲染分离 | PASS | HUD 重排和背景只改表现层；结算错误处理在 app/进度边界，不复制胜负/关卡规则；背景选择不进入模拟。 |
| III. 关键数值集中管理 | PASS | HUD 安全区坐标写入 `presentation/scenes.py` 几何常量；背景 ID/分辨率/缩略图进入 `assets/backgrounds/manifest.json`；不新增散落玩法数值。 |
| IV. 核心玩法修改必须验证 | PASS | 20 次第一关结算/下一关流程、损坏/只读进度、背景回退、HUD 双分辨率截图和现有玩法回归；验证结果写入 `docs/validation/013/`。 |
| V. 新增功能保持已有功能可运行 | PASS | 保持 5 关战役、星级、无尽、狗狗外观、暂停/重开/菜单和现有测试；背景缺失只回退视觉，不阻断游戏。 |
| 开发约束：复用结构、职责和数值边界 | PASS | 复用 `Renderer`、`scenes`、`Progress`、`app` 和现有资源加载；新增背景目录/模块只承担素材清单与选择，无第二框架。 |

**Pre-Phase 0 Gate**: PASS。无宪章冲突或需要豁免的复杂抽象。

## Project Structure

### Documentation (this feature)

```text
specs/013-wave-hud-error-backgrounds/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── hud-status-layout.md
│   ├── result-flow-and-errors.md
│   └── background-assets-and-selection.md
├── checklists/
│   └── requirements.md
└── tasks.md                         # 后续由 $speckit-tasks 创建
```

### Source Code (repository root)

```text
assets/
├── levels/                          # 现有 5 关；本次不改波次/数值
├── skins/                           # 现有皮肤；背景不再混入 default 皮肤
└── backgrounds/                     # 新增高清背景权威来源
    ├── manifest.json
    ├── day.png                      # 2560×1440 或更高
    ├── night.png
    ├── dusk.png
    ├── thumbs/{day,night,dusk}.png
    └── source/                      # 原始生成/下载图与来源记录

src/pvz_game/
├── app.py                           # 结果流程、下一关/重试、背景菜单入口
├── progress.py                      # settings.background_id、旧存档迁移、原子保存
└── presentation/
    ├── backgrounds.py               # 新增：背景清单加载、校验、回退、缓存
    ├── scenes.py                    # 顶部 HUD 条/背景菜单/缩略图几何常量
    ├── renderer.py                  # HUD 状态条、背景绘制、选择页
    └── input.py                     # 背景菜单点击、HUD 安全区命中

tools/
├── generate_backgrounds.py          # 开发期生成/整理三套高清背景与缩略图
└── validate_assets.py               # 增加背景清单/分辨率/文件校验

tests/
├── unit/test_backgrounds.py         # 清单、回退、偏好迁移
├── integration/test_hud_layout.py   # 状态条与草坪/HUD 不相交
└── integration/test_result_flow.py  # 第一关结算/下一关/重试/损坏进度
```

**Structure Decision**: 继续单项目结构。背景作为独立资源与表现模块，不塞进 `skins/default`，避免和植物外观耦合；HUD/菜单仍复用 `Renderer`、`button`、`rounded`、`text`，不引入 UI 框架。

## Design Artifacts

- [research.md](research.md)：HUD 状态条、第一关报错复现、背景素材/预缩放/偏好迁移和最小验证决策。
- [data-model.md](data-model.md)：HUD 布局、BackgroundOption/Manifest、Progress schema v2、结果流程和背景渲染状态。
- [contracts/hud-status-layout.md](contracts/hud-status-layout.md)：顶部 HUD 安全区和不遮挡契约。
- [contracts/result-flow-and-errors.md](contracts/result-flow-and-errors.md)：第一关结算、下一关/重试和错误恢复契约。
- [contracts/background-assets-and-selection.md](contracts/background-assets-and-selection.md)：三套高清背景、选择、持久化与回退契约。
- [quickstart.md](quickstart.md)：最小验证命令、截图、背景/结算试玩和 Windows 构建。

## Design Decisions

1. **顶部 HUD 状态条**：在现有 HUD 下方、草坪上方建立单行状态带（约 y=114–128，卡片底边下方到草坪起点之前），集中显示关卡名、当前波次、出怪进度和下一波预告。移除当前覆盖第 1 行的 `(650,166)` 预告面板和浮动波次公告；所有文字只在草坪矩形之外绘制。长文本单行截断/省略，状态条高度固定在草坪上边界和第一行角色上方。
2. **第一关结算报错**：先用真实窗口/无头 harness 复现“清空第一关→结算→点击下一关/重试/返回”并记录 traceback；在 `app` 的结果与进度边界增加明确异常处理：记录详细日志、显示可理解的回退提示、保持可返回菜单/重试。修复根因后，保证结算只记录一次、下一关/重试使用新关卡完整状态、read-only/损坏进度不崩溃。
3. **高清背景资源**：新增 `assets/backgrounds/`，以授权的真实感/高级感摄影或写实渲染为基础，提供日间、夜间、黄昏三套至少 2560×1440 的 PNG（附缩略图、作者/来源/授权和派生记录）；不使用幼稚卡通或低龄插画。允许开发期联网检索/本地生成，运行时只读取随包文件，不发起网络请求。
4. **背景选择与持久化**：新增 `presentation/backgrounds.py` 负责清单校验、加载、缓存和缺失回退；`Progress` 的 schema 增加 `settings.background_id`，旧存档缺失时回退默认、未知 ID 回退默认。选择在主菜单“更换背景”中完成，点击立即应用，背景只影响绘制。
5. **背景绘制**：启动时按 1050×600 逻辑尺寸预缩放/裁切并缓存三套背景，避免每帧大图缩放；背景层只替换 `Renderer.background()` 的底图，保留草坪格、HUD、角色和点击区域不变。夜间/黄昏背景需保证角色与文字对比度。
6. **菜单与输入**：主菜单新增“更换背景”按钮/背景选择页；显示三张缩略图、名称和当前标记；`input.click` 增加背景菜单分支和默认参数，保持现有测试调用兼容；返回主菜单/开始游戏时选择立即生效。
7. **最小验证**：HUD 只截 1050×600 与 1920×1080 的关键状态；第一关用可重复的 20 次结算 harness + 一次真实窗口试玩；背景做三套切换/重启/损坏回退；只跑定向 pytest 和现有回归，不跑全量矩阵。
8. **兼容性**：现有 `load()`、`snapshot()`、事件序列、5 关配置、星级、无尽和狗狗外观不变；新增背景模块可选，缺失时回退到现有默认背景。`Progress` 旧 schema 自动迁移，不丢解锁/星级。

## Compatibility Guardrails

- `Simulation.snapshot()`、事件、关卡数值和 60Hz 模拟保持不变；HUD/背景只在 `presentation` 层。
- `config.load()` 仍返回 day_01；`load_campaign()` 和 5 关 JSON 不因本功能改变。
- 新背景偏好写入 `Progress.settings`；旧 v1 progress JSON 读取后自动补默认背景，不重写玩法进度。
- `Renderer.draw`、`input.click`、`visible_plant_cards` 的新参数默认值保持旧调用兼容。
- 背景加载失败、文件缺失、清单损坏只回退默认背景，不得阻断菜单/对局/结算。
- Windows 包继续递归打包 `assets/`；三套背景和缩略图随包提供，运行时不联网。

## Phased Delivery（先修复，后美化）

### Milestone A - 可玩性修复（P1）

1. 复现第一关结算/下一关报错并修复结果流程、进度保存和回退提示。
2. 建立顶部 HUD 状态条，移除覆盖草坪的波次/预告面板，完成双分辨率截图。
3. 运行 20 次第一关结算 harness、现有 5 关/星级/无尽/狗狗回归。

### Milestone B - 高清背景与切换（P2）

1. 生成/整理三套高清背景、缩略图、manifest、来源记录。
2. 接入背景清单、预缩放缓存、主菜单选择页、立即应用和本机持久化。
3. 完成三套切换、重启恢复、损坏回退、清晰度和性能检查。

## Focused Validation Plan

1. **HUD**：运行 `tests/integration/test_hud_layout.py`；在 1050×600/1920×1080 截取第 1 波前、进行中、最后一波前和暂停；检查状态条与草坪矩形不相交、文字不裁切、卡片/暂停按钮不重叠；断言下一波预告与实际出怪一致且提前 ≥2 秒。
2. **第一关流程**：用真实 day_01 胜利路径（复用 replay 策略/实际 systems.advance，不允许只强制 phase='won'）连续 20 次“清空第一关→胜利→下一关/重试/返回/退出”；检查 0 未处理异常、结果只保存一次、day_02 正确初始状态；再测只读/损坏 progress 和第二关 JSON 缺失。
3. **背景**：运行 `tools/validate_assets.py` 检查三套文件/分辨率/清单；在主菜单切换日间/夜间/黄昏，截图检查清晰度和可读性；重启恢复；临时移除当前背景确认回退；标准场景基准确认无性能回退；断网启动/切换确认 0 网络请求。
4. **回归**：现有战役配置/进度/无尽、狗狗帧、可玩循环/拖放和皮肤不变性定向用例；不跑全量 pytest。
5. **Windows 包**：构建 `PvzMiniGame-v0.7.1`（或下一版本），启动并完成第一关结算→下一关、背景切换、重启恢复一次。

不执行：安卓、全量 pytest、所有外观矩阵、长时间压力测试、背景极限切换压力。

## Risks and Mitigations

- **第一关报错根因未知**：先用真实窗口/traceback harness 复现；若无法稳定复现，补充异常日志和结果流程防护，并以“20 次无未处理异常/可恢复”作为门槛，不掩盖错误。
- **HUD 状态条拥挤**：固定状态条高度，长文本两行/截断；只保留当前波次、下一波摘要和关卡名，避免重新堆叠覆盖草坪。
- **背景素材体积/内存**：启动预缩放/缓存；三张 2560×1440 PNG 随包；如包体过大，评估有损/压缩但不降低可见清晰度，并记录取舍。
- **背景授权/来源**：每套记录生成提示词/下载 URL、日期、SHA-256 和授权说明；运行时不下载。
- **偏好迁移**：旧 progress 无 settings 时补默认；未知背景 ID 回退；保存失败不阻断游戏。

## Complexity Tracking

无宪章违规。没有新增引擎、数据库、网络运行时或第二套 UI；新增背景模块和资源目录属于现有结构的必要扩展。

## Post-design Constitution Check

| 原则 | 状态 | 复核依据 |
|---|---|---|
| I | PASS | 先修复 P1 结算和 HUD，再接入背景；核心循环完整。 |
| II | PASS | HUD/背景只改表现层；错误处理在 app/进度边界；规则未改。 |
| III | PASS | HUD 几何在 scenes；背景参数在 manifest；玩法数值不变。 |
| IV | PASS | 20 次结算 harness + 双分辨率 HUD 截图 + 背景回退 + 定向回归。 |
| V | PASS | 5 关/星级/无尽/狗狗外观/旧进度保持；背景缺失只回退。 |
| 开发约束 | PASS | 复用现有结构，无新运行时依赖。 |
