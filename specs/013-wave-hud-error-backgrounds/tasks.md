# Tasks: 波次 HUD 修复、通关稳定性与高清可切换背景

**Input**: Design documents from `/specs/013-wave-hud-error-backgrounds/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 只保留本次必要检查：HUD 几何、第一关 20 次结算流程、背景清单/回退/偏好迁移、一次性能和 Windows 包冒烟。不跑全量 pytest、外观矩阵或安卓。

**Organization**: 按规格的 3 个用户故事分阶段。US1/US2 是可玩性修复（Milestone A）；US3 是高清背景与切换（Milestone B）。US1/US2/US3 都改 `renderer.py`/`app.py`，实现按 US1 → US2 → US3 顺序执行。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 不同文件、且不依赖未完成任务，可以并行
- **[Story]**: 所属用户故事（US1/US2/US3）；Setup/Foundational/Polish 不带故事标签
- 每个任务包含明确文件路径和可执行动作

## Path Conventions

单项目：`src/`、`assets/`、`tools/`、`tests/`、`packaging/`、`docs/validation/013/`。

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 准备 HUD 几何、背景资源目录与清单骨架。

- [X] T001 [P] 在 `src/pvz_game/presentation/scenes.py` 增加顶部 HUD 状态条常量：约 `(160,114,680,14)`，下边缘 ≤128；同时增加“更换背景”按钮/背景缩略图/返回按钮的几何常量，保持现有 `BUTTONS` 键不变
- [X] T002 [P] 新建 `assets/backgrounds/` 目录与 `assets/backgrounds/manifest.json`：schema_version=1、default=day、至少 day/night/dusk 三项、每项含 id/name/file/thumb/width/height/theme/source/sha256/license；同时创建 `thumbs/`、`source/`
- [X] T003 [P] 新建 `src/pvz_game/presentation/backgrounds.py` 骨架：清单加载、字段/分辨率/SHA 校验、未知/缺失回退 default 的接口；暂不接渲染

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 进度设置迁移和错误日志是所有后续故事共用的底层能力。

**⚠️ CRITICAL**: 本阶段完成后再开始用户故事。

- [X] T004 [P] 扩展 `src/pvz_game/progress.py` 到 schema v2：增加 `settings.background_id`；读取 v1 时补默认 `day` 并保留 unlocked/levels/endless；未知背景 ID 回退 manifest default；保存失败不抛出到界面
- [X] T005 [P] 扩展 `src/pvz_game/resources.py` 的错误日志接口：提供可记录完整 traceback 的 helper（仍写本机日志），供第一关结算/背景加载失败使用；不改变默认日志路径
- [X] T006 [P] 在 `tools/validate_assets.py` 只建立背景 manifest 结构/字段校验入口，暂不要求背景图片已存在；文件/分辨率/SHA 的强制门禁留到 T022（T017 生成素材后），避免 US1/US2 阶段误报

---

## Phase 3: User Story 1 - 波次与关卡文字不再遮挡草坪 (Priority: P1) 🎯 可玩性修复

**Goal**: 波次、下一波预告和关卡名只在顶部 HUD 状态条显示，不覆盖 5×12 草坪和角色。

**Independent Test**: 在 1050×600 和 1920×1080 下分别截取第 1 波前、波次进行中、最后一波前和暂停；状态条与草坪/HUD 控件不相交，文字不裁切。

### Tests for User Story 1（必要且定向）

- [X] T007 [P] [US1] 新建 `tests/integration/test_hud_layout.py`：断言状态条矩形与草坪 `(105,160,864,380)`、卡片/铲子/暂停/阳光框无交集；长标题不会越出状态条；断言下一波预告与实际出怪（类型/数量/主要行）一致、提前 ≥2 秒且切换后无旧预告；测试先在当前浮动面板上失败

### Implementation for User Story 1

- [X] T008 [US1] 在 `src/pvz_game/presentation/renderer.py` 实现顶部状态条：显示关卡名、当前波次/出怪进度、下一波预告；移除 `(650,166)` 的草坪内预告面板和覆盖草坪的浮动波次公告；`wave_announcement` 不再创建草坪内矩形
- [X] T009 [US1] 调整 `draw_hud`/状态条文字截断和两行布局；把原 `(880,78)` 关卡名移入状态条；确保卡片、阳光、暂停、铲子区域不被占用；`Renderer.draw` 新参数带默认值，兼容基准/旧调用
- [X] T010 [US1] 在 `src/pvz_game/presentation/input.py` 如有 HUD 命中调整，确保状态条不属于可点击草坪；不改变植物/阳光/按钮点击逻辑
- [X] T011 [US1] 在 1050×600/1920×1080 生成截图，运行 `pytest tests/integration/test_hud_layout.py -q`，检查预告/最后一波/暂停；记录到 `docs/validation/013/hud.md`

**Checkpoint**: 波次/关卡文字完全移出草坪，双分辨率无遮挡。

---

## Phase 4: User Story 2 - 通关第一关后流程稳定 (Priority: P1)

**Goal**: 第一关结算、下一关、重试、返回菜单和进度保存不出现未处理异常；day_02 正确解锁。

**Independent Test**: 20 次第一关清空→结算→各操作；0 未处理异常、day_02 解锁 100%、只保存一次；只读/损坏进度可恢复。

### Tests for User Story 2（必要且定向）

- [X] T012 [P] [US2] 新建 `tests/integration/test_result_flow.py`：必须用真实 day_01 胜利路径（复用 replay 策略/实际 `systems.advance`，不允许只强制 `phase='won'`）连续 20 次清空→结算，验证下一关/重试/返回/退出、只保存一次、day_02 解锁；覆盖只读/损坏 progress 与 day_02 缺失；测试应先复现当前问题

### Implementation for User Story 2

- [X] T013 [US2] 使用 T012/真实窗口复现第一关结算报错并记录完整 traceback；定位并修复 `src/pvz_game/app.py` 的结果/下一关路径（结算只记录一次、next/retry/menu 状态重置），必要时修正 `src/pvz_game/progress.py` 的保存/迁移边界
- [X] T014 [US2] 在 `src/pvz_game/app.py`/`src/pvz_game/presentation/renderer.py` 增加可恢复错误提示和防护：结算/进度/下一关加载异常时显示提示、保留返回菜单/重试；不得重复结算或卡死
- [X] T015 [US2] 运行 `pytest tests/integration/test_result_flow.py -q` 与一次真实窗口通关→下一关；记录到 `docs/validation/013/result-flow.md`

**Checkpoint**: 第一关通关及后续操作稳定，day_02 解锁/重启保留。

---

## Phase 5: User Story 3 - 高清且可切换的背景 (Priority: P2)

**Goal**: 三套日间/夜间/黄昏高清背景，主菜单可切换，立即生效并跨重启保留；缺失回退默认。

**Independent Test**: 三套背景在 1050×600/1920×1080 清晰可读；切换/重启/损坏回退正常；运行期离线。

### Tests for User Story 3（必要且定向）

- [X] T016 [P] [US3] 新建 `tests/unit/test_backgrounds.py`：清单至少 3 项/day/night/dusk、default 存在、源图≥2560×1440、SHA 匹配、未知 ID/缺失文件回退、v1 progress→v2 settings 迁移

### Implementation for User Story 3

- [X] T017 [P] [US3] 新建 `tools/generate_backgrounds.py` 并生成/整理 `assets/backgrounds/{day,night,dusk}.png` 与 `thumbs/*.png`：使用授权的高端真实感摄影/写实渲染（可联网检索），禁止幼稚卡通/低龄插画；源图≥2560×1440，记录作者/下载 URL、日期、SHA-256、授权到 `assets/backgrounds/source/provenance.json` 和 manifest
- [X] T018 [US3] 完成 `src/pvz_game/presentation/backgrounds.py`：加载/校验三套背景，按 1050×600 预缩放/裁切并缓存；缺失/损坏回退默认；不每帧缩放大图
- [X] T019 [US3] 在 `src/pvz_game/presentation/renderer.py` 用当前背景 surface 替换 `background()` 的默认底图，保持草坪格、HUD、角色、点击区域和背景层顺序不变
- [X] T020 [US3] 在 `src/pvz_game/presentation/scenes.py`/`input.py`/`renderer.py` 增加主菜单“更换背景”页：三张缩略图/名称/当前标记/返回；`click` 新参数带默认值
- [X] T021 [US3] 在 `src/pvz_game/app.py` 接入背景选择：启动读取 `progress.settings.background_id`，切换立即应用并保存，缺失/未知回退默认并提示；外观选择不变
- [X] T022 [US3] 在 T006 的 manifest 结构校验之上，补全三套文件/分辨率/SHA/缩略图的强制校验；构建前必须拦截坏背景
- [X] T023 [US3] 在 1050×600/1920×1080 截图三套背景，验证切换/重启/临时移除文件回退、HUD/角色可读；运行标准场景基准记录切换前后 FPS/p95；断网启动/切换确认 0 网络请求；记录到 `docs/validation/013/backgrounds.md`

**Checkpoint**: 三套高清背景可切换、可保存、可回退，运行期离线。

**完成备注（2026-10-31）**: T013 未复现用户原始异常文本；已用真实 day_01 胜利路径 20 次 + 结果/保存/下一关错误边界覆盖。T023 性能为 SDL dummy 快速验证，离线为运行时路径检查而非抓包。T028 的自动命令与 Windows 包冒烟已完成，真实鼠标逐项点击建议实机补做。

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T024 [P] 更新 `README.md`、`docs/development.md` 和游戏内帮助：顶部 HUD 状态条、第一关结算修复、背景选择/保存位置
- [X] T025 新增 `docs/validation/013/release.md`：汇总 HUD 截图、20 次结算、背景切换/回退、性能基准、Windows 包和未执行项
- [X] T026 运行定向回归：`pytest tests/integration/test_hud_layout.py tests/integration/test_result_flow.py tests/unit/test_backgrounds.py -q`、既有战役/进度/无尽/狗狗定向用例；不跑全量 pytest
- [X] T027 构建 `PvzMiniGame-v0.7.1` Windows 包并启动：完成第一关结算→下一关、切换一次背景、重启恢复；确认 `_internal/pvz_game/assets/backgrounds/` 随包
- [X] T028 按 `quickstart.md` 执行最终最小验收，只在 `docs/validation/013/release.md` 勾选实际通过项

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001–T003 无依赖，可并行。
- **Foundational (Phase 2)**: T004–T006 在 Setup 后执行；T004/T005 可并行，T006 依赖 T002/T003。
- **US1 (Phase 3)**: 依赖 Setup/Foundational；先 T007 测试，再 T008–T010 实现，T011 验收。
- **US2 (Phase 4)**: 依赖 US1 的 renderer 改动（避免同文件冲突）；T012 先复现，T013–T014 修复，T015 验收。
- **US3 (Phase 5)**: 依赖 US2 的 app/renderer 稳定；T016 测试，T017 素材可并行，T018–T021 接入，T022 校验，T023 验收。
- **Polish (Phase 6)**: 依赖所需故事完成；T024 可并行，T025–T028 顺序执行。

### User Story Dependencies

- **US1**: 可独立验收 HUD 不遮挡；不依赖 US2/US3。
- **US2**: 依赖 US1 后的 renderer 现状；不依赖背景。
- **US3**: 依赖 US1/US2 的 renderer/app 基线，避免同文件冲突。

### Within Each User Story

- 先写定向测试并确认失败，再实现；数据/清单 → 表现/流程 → 验证。
- `renderer.py`/`app.py` 的连续任务按 ID 顺序执行，不并行编辑。
- 每个 Checkpoint 后运行对应定向检查，不把未执行/失败项标为通过。

### Parallel Opportunities

- Setup T001/T002/T003 可并行（不同文件/目录）。
- Foundational T004/T005 可并行；T006 在 T002/T003 后。
- US1 T007 测试可与 T008 的布局设计并行编写。
- US3 T016 测试与 T017 背景素材获取/生成可并行；T018 依赖 T002/T017。
- T024 文档可与实现并行起草，最终按实际结果更新。

---

## Parallel Example: US1

```text
Task: "T007 [P] [US1] 新建 tests/integration/test_hud_layout.py"
Task: "T001 [P] 在 src/pvz_game/presentation/scenes.py 增加 HUD 状态条常量"
```

## Parallel Example: US3

```text
Task: "T016 [P] [US3] 新建 tests/unit/test_backgrounds.py"
Task: "T017 [P] [US3] 新建 tools/generate_backgrounds.py 并生成三套材质"
```

---

## Implementation Strategy

### Milestone A - 可玩性修复（优先）

1. 完成 Setup/Foundational。
2. 先做 US1（HUD 状态条，解决文字压地图），再做 US2（第一关结算/下一关/进度）。
3. 运行 HUD 双分辨率截图、20 次结算 harness 和一次真实窗口试玩；这是本轮可交付的最小可玩版本。

### Milestone B - 高清背景

1. 生成/整理三套高清背景与 manifest。
2. 接入背景加载、预缩放缓存、主菜单切换、进度保存/回退。
3. 完成三套切换、重启恢复、损坏回退和性能检查。

### MVP 范围

- **可玩 MVP**: US1 + US2（修复遮挡与第一关流程）。
- US3 是 P2 视觉增强，不阻塞可玩版本交付。
- 不把全量 pytest、外观矩阵、安卓或长时压力作为完成条件。

## Notes

- `[P]` 仅表示不同文件、无未完成依赖；`renderer.py` 和 `app.py` 上的任务不要并行。
- 背景素材允许开发期联网获取/生成，但运行期不得联网；manifest/来源/授权必须可追溯。
- 第一关报错未提供具体异常文本，T013 必须先复现并记录 traceback，不能只用 try/except 吞异常。
