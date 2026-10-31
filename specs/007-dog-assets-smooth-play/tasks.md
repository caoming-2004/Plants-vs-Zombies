# Tasks: 狗狗素材与流畅可玩体验

**Input**: `specs/007-dog-assets-smooth-play/spec.md`、`plan.md`、`research.md`、`data-model.md`、`contracts/`、`quickstart.md`

**Organization**: 按用户故事交付；仅做规格要求的必要验证。

## Phase 1: Setup

- [X] T001 核对 `C:/Users/Redmi/Desktop/小宝.png`、`C:/Users/Redmi/Desktop/小杜.png`、`C:/Users/Redmi/Desktop/好孩子.png` 的存在、尺寸、透明背景与文件哈希，并将实际发现记录在 `docs/validation/007/source-intake.md`
- [X] T002 核对 `tools/import_dog_assets.py`、`assets/skins/dogs/manifest.json`、`assets/skins/dogs_photo/manifest.json` 中好孩子/小宝/小杜与 peashooter/wallnut/jalapeno 的既有对应关系，记录在 `docs/validation/007/source-intake.md`

## Phase 2: Foundational

- [X] T003 从鼠标按下事件进入游戏事件循环起，记录可见反馈、图片加载、首次缩放、首个可接收有效游戏输入的画面等分段耗时，并定位瓶颈；结果写入 `docs/validation/007/start-transition.md`

## Phase 3: User Story 1 - 使用三只指定狗狗进行游戏 (P1)

**Goal**: 三图身份正确、地图尺寸接近、全姿态完整展示。

**Independent Test**: 逐狗检查站立、动作、边缘与相邻位置，站立高度比≤1.15且身体完整。

- [X] T004 [US1] 在 `tools/import_dog_assets.py` 中接入本轮三张原图，保留 peashooter=好孩子、wallnut=小宝、jalapeno=小杜 和原有动作帧来源；按实际图片尺寸/背景处理透明边缘，不混用身份
- [X] T005 [US1] 重建 `assets/skins/dogs/`、`assets/skins/dogs_photo/` 图集与 manifest，并在 `assets/sources.json` 更新三张原图哈希和来源记录
- [X] T006 [US1] 在 `assets/skins/dogs/manifest.json`、`assets/skins/dogs_photo/manifest.json` 校准角色站立倍率和锚点，使三狗站立可见高度比≤1.15；不得逐帧强制缩放或裁切身体
- [X] T007 [US1] 如绘制边缘仍裁切，在 `src/pvz_game/presentation/renderer.py` 调整狗狗显示位置与可见边界，同时保持游戏逻辑落点和碰撞规则不变
- [ ] T008 [US1] 使用 `tools/validate_assets.py`、`src/pvz_game/presentation/dog_validation.py` 及真实窗口，核对三狗所有现有动作、地图边缘、相邻重叠和透明边缘；结果写入 `docs/validation/007/dog-visuals.md`

## Phase 4: User Story 2 - 流畅进入并完成一局 (P1)

**Goal**: 开始反馈及时，1 秒内进入可操作画面，动作连续且核心循环可用。

**Independent Test**: 连续 10 次开始点击与一次完整试玩，覆盖首次进入、胜负及重开。

- [X] T009 [US2] 根据 T003 测量结果，在 `src/pvz_game/app.py`、`src/pvz_game/presentation/renderer.py` 或 `src/pvz_game/presentation/skin_catalog.py` 复用现有缓存/预热路径，消除开始切换中的同步耗时并保持即时按钮反馈
- [X] T010 [US2] 在 `src/pvz_game/presentation/animation.py` 与 `tools/import_dog_assets.py` 核对动作帧顺序、时长及缓存使用；只修复实际发现的闪白、停顿或首次缩放问题，不改变玩法 tick
- [ ] T011 [US2] 在真实窗口连续执行 10 次开始点击，以鼠标按下事件进入游戏事件循环为起点，记录可见反馈是否≤100毫秒、可接收有效游戏输入的画面是否≤1秒；首次进入及重开各至少一次，结果写入 `docs/validation/007/start-transition.md`
- [ ] T012 [US2] 运行与改动相关的现有素材/玩法检查并完成一次真实窗口试玩，核对资源、种植、敌人、胜负、重开和三狗动作；结果写入 `docs/validation/007/playtest.md`

## Phase 5: User Story 3 - 快速获得精简的可玩版本 (P2)

**Goal**: 验证有据可查，临时测试产物清零。

**Independent Test**: 检查验收记录及本轮临时 EXE/ZIP 清单，确认没有残留。

- [X] T013 [US3] 汇总本轮实际执行、通过、失败及未执行的检查到 `docs/validation/007/release-report.md`，避免重复或无关测试
- [X] T014 [US3] 核对本轮生成的临时测试 EXE/ZIP 的明确路径并删除，保留正式交付物和既有用户文件；清理前后清单写入 `docs/validation/007/release-report.md`

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T015 检查 `specs/007-dog-assets-smooth-play/spec.md` 的 SC-001 至 SC-004 与 `docs/validation/007/release-report.md` 的实际证据逐项对应，并报告未达标项

## Dependencies & Execution Order

`T001–T002 → T003 → T004–T008 (US1) → T009–T012 (US2) → T013–T015 (US3/收尾)`。US2 的计时定位可在素材核对后开始；最终试玩须使用本轮导入素材。T014 必须在验证结束后执行。

## Parallel Opportunities

T003 可与 T001–T002 的素材核对并行。T001 和 T002 共用 `docs/validation/007/source-intake.md`，顺序写入。T008 和 T011 的记录文件不同，但最终真实窗口验证需顺序进行以保持结果可复现。其余任务按依赖顺序执行。

## Implementation Strategy

先完成 T001–T008，得到三狗可显示的增量；随后完成开始切换和整局体验；最后只做必要验证、清理及验收记录。第一阶段可独立展示三狗素材，第二阶段形成完整可玩版本。


