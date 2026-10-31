# Tasks: 高清狗狗角色与十二帧动作

**Input**: `specs/008-dog-characters-12fps/spec.md`、`plan.md`、`research.md`、`data-model.md`、`contracts/`、`quickstart.md`

## Phase 1: Setup

- [x] T001 核对项目根目录 `被窝.png`、`嗷嗷嗷.png`、`胖宝宝.png`、`黄黄.png` 的实际布局、透明边界与哈希，并记录到 `docs/validation/008/source-intake.md`
- [x] T002 核对 `tools/import_dog_assets.py`、`assets/skins/dogs/manifest.json` 和 `assets/config/balance.json` 中既有角色键与职责映射，明确新素材接入点，记录到 `docs/validation/008/source-intake.md`

## Phase 2: Foundational

- [x] T003 在 `src/pvz_game/presentation/scenes.py` 与 `src/pvz_game/presentation/input.py` 规划六卡片可用布局，确保狗狗外观可见六张卡、经典外观仍只有原有卡片且种植格坐标不变

## Phase 3: User Story 1 - 查看高清被窝和嗷嗷嗷 (P1)

**Goal**: 狗狗卡通外观中的被窝和嗷嗷嗷使用项目内高清素材，身份和动作完整。

**Independent Test**: 在狗狗外观查看两角色卡片、预览及地图显示；验证图集来源和透明轮廓。

- [x] T004 [US1] 扩展 `tools/import_dog_assets.py` 以导入已核对的 `被窝.png`、`嗷嗷嗷.png` 姿态，并将原图保存在 `assets/skins/dogs/source/` 不做覆盖
- [x] T005 [US1] 重建 `assets/skins/dogs/manifest.json`、`assets/skins/dogs/provenance.json` 和狗狗图集，保持被窝/嗷嗷嗷原角色键及必要动作映射
- [x] T006 [US1] 在 `assets/sources.json` 记录两张原图来源、哈希和派生关系，并确认 `assets/skins/dogs_photo/manifest.json` 原照片形象没有被意外替换
- [x] T007 [US1] 使用 `tools/validate_assets.py` 和真实窗口核对被窝、嗷嗷嗷卡片、预览、动作、完整身体及背景边缘，结果写入 `docs/validation/008/dog-visuals.md`

## Phase 4: User Story 2 - 使用胖宝宝和黄黄两种新植物 (P1)

**Goal**: 两个新植物只在狗狗外观中可选，分别防御和远程攻击并遵守既有种植规则。

**Independent Test**: 在狗狗外观分别种植两角色并验证阻挡/攻击、扣费、冷却及失败放置；切回经典外观确认新卡片隐藏。

- [x] T008 [US2] 在 `assets/config/balance.json` 增加 `pangbaobao` 防御型与 `huanghuang` 远程攻击型植物配置，明确价格、生命值、冷却、伤害/攻击间隔，所有数值集中于该配置
- [x] T009 [US2] 在 `src/pvz_game/domain/simulation.py` 与 `src/pvz_game/domain/systems.py` 将新植物键接入既有 blocker/shooter 规则分派，复用统一扣费、占格、伤害与冷却逻辑
- [x] T010 [US2] 扩展 `src/pvz_game/presentation/input.py`、`scenes.py`、`renderer.py`，只在 `dogs` 外观显示并接受两张新卡，保持经典外观四张原卡及种植格坐标
- [x] T011 [US2] 将 `胖宝宝.png`、`黄黄.png` 导入狗狗外观素材，在 `assets/skins/dogs/manifest.json` 提供新植物预览、卡片及必要动作；皮肤资源缺失时沿用现有提示/回退策略
- [x] T012 [US2] 用最小受影响规则检查验证两新植物成功种植、阳光不足、冷却中、格子占用、攻击/阻挡和重开状态，记录到 `docs/validation/008/new-plants.md`

## Phase 5: User Story 3 - 观看统一的十二帧植物动作 (P2)

**Goal**: 循环植物动画每秒约 12 个不同姿态，游戏 60 Hz 更新和非循环玩法事件时长保持原有节奏。

**Independent Test**: 观察每种植物循环动作 10 秒，统计不同姿态并确认操作与玩法时间不变。

- [x] T013 [US3] 在 `src/pvz_game/presentation/animation.py` 调整植物循环动作帧时长/姿态采样至 12±1 个不同姿态每秒，保持 `tick_hz` 及非循环动作玩法持续时间不变
- [x] T014 [US3] 在真实窗口对经典与狗狗外观中可用植物观察 10 秒，记录姿态速率、输入响应与是否闪白/卡顿到 `docs/validation/008/animation-cadence.md`

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T015 仅运行必要的素材校验、受影响规则/既有回归和一局核心流程，构建正式可玩包并启动烟测；结果写入 `docs/validation/008/release-report.md`
- [x] T016 清点本轮临时测试 EXE/ZIP 并删除，保留正式发行目录与用户文件；清理前后清单写入 `docs/validation/008/release-report.md`

## Dependencies & Execution Order

`T001–T003 → T004–T007 (US1) → T008–T012 (US2) → T013–T014 (US3) → T015–T016`。T015 完成前不执行 T016。

## Parallel Opportunities

T001 与 T002 可并行检查不同输入；T004 和 T008 可在资产布局确认后分文件准备，但图集重建须顺序完成。US2 的规则配置与素材处理分别涉及 balance/domain 和 importer/manifest，可并行实现后在 T010 集成。真实窗口验收顺序执行。

## Implementation Strategy

先完成被窝、嗷嗷嗷替换形成可展示增量；再加入两张狗狗外观限定植物卡和对应玩法，完成可玩 MVP；最后统一动作节奏并做精简验收。正式包验证后清理临时测试包。
