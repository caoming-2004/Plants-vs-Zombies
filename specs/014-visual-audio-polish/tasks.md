# Tasks: 字体、场景背景与游戏音乐优化

**Input**: Design documents from `/specs/014-visual-audio-polish/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/visual-audio-presentation.md`, `quickstart.md`

**Tests**: 保留直接覆盖新偏好、音乐场景切换、背景 manifest 和窗口渲染性能的定向检查；不执行全量测试，不为稳定的玩法规则增加回归套件。

## Phase 1: Setup

**Purpose**: 复用现有 Pygame/Windows 打包结构，无额外项目初始化。

- 本阶段无单独初始化任务；现有代码、资产目录、测试环境与 Windows 目录打包器均可复用。

## Phase 2: Foundational

**Purpose**: 不引入阻塞所有用户故事的新框架或依赖。

- 本阶段无额外基础设施任务；各故事按现有资源目录独立实施。

## Phase 3: User Story 1 - 清晰易读的游戏文字 (Priority: P1)

**Goal**: 在主要界面及常用窗口缩放下提高文字边缘清晰度，同时保持现有布局、字号层级和缓存行为。

**Independent Test**: 显示菜单、HUD、卡片、提示和结算界面并切换窗口尺寸，确认中文/数字清楚且不裁切；最终性能检查确认标准对局依旧流畅。

- [X] T001 [US1] 保留 `src/pvz_game/presentation/prototype_renderer.py` 中的抗锯齿字体渲染，并在 `src/pvz_game/presentation/window_scaling.py` 与 `src/pvz_game/app.py` 统一应用和 `tools/benchmark.py` 的平滑窗口合成路径；保留 1050×600 逻辑画布和 60 FPS 运行目标，不替换 Noto Sans SC 或逐界面重写。

**Checkpoint**: 主要画面文字可读，关卡坐标与鼠标映射不变。

## Phase 4: User Story 2 - 符合战斗场景的成熟背景 (Priority: P1)

**Goal**: 使用成熟写实且符合庭院防守场景的背景，并保留日间/夜间/黄昏选择、离线运行和来源记录。

**Independent Test**: 检查三个背景在菜单/战斗中的呈现、图像清晰度和对象对比度；背景 manifest 校验通过且断网可读取。

- [X] T002 [US2] 在 `assets/backgrounds/source/yard-defense-master.png` 生成并保存高分辨率、成熟写实的草坪防守场景主图，避开低龄卡通风格、拥挤细节和与游戏无关的道路主体，并在 `assets/backgrounds/source/provenance.json` 记录生成方式及内容哈希。
- [X] T003 [US2] 更新 `tools/generate_backgrounds.py`、`assets/backgrounds/manifest.json` 和 `assets/backgrounds/thumbs/`，以新主图生成/登记日间、夜间、黄昏三种 2560×1440 变体；保留 `day`/`night`/`dusk` ID、缩略图、哈希校验和默认背景回退，禁止运行时联网加载。

**Checkpoint**: 既有背景选择器能切换新背景，旧存档选项继续有效。

## Phase 5: User Story 3 - 有氛围且不干扰操作的音乐 (Priority: P2)

**Goal**: 提供离线菜单/对局音乐、胜利提示、简洁的开关/音量设置和无音频设备时的静音降级。

**Independent Test**: 验证音乐随菜单、对局、暂停、胜利、失败状态变化；设置持久化；缺少音频设备/资源时仍可启动并游玩。

- [X] T004 [US3] 将来源和可再分发许可明确的菜单循环曲、对局循环曲及短胜利提示加入 `assets/music/`，在 `assets/music/provenance.json` 记录来源、许可、主题和文件哈希；未收到用户提供或授权录音时不得加入俊良或狗狗声音。
- [X] T005 [P] [US3] 在 `src/pvz_game/progress.py` 为现有 `settings` 添加 `music_enabled` 默认 `true` 和 `music_volume` 默认 `0.55`（数值严格限制在 0.0–1.0）；旧版存档缺字段时使用默认值，非法值安全回退并保留关卡进度及背景选择。
- [X] T006 [P] [US3] 在 `src/pvz_game/presentation/audio.py` 添加轻量音乐控制器，使用 pygame-ce 现有音频能力驱动菜单/对局循环、暂停/恢复、失败停止和单次胜利提示；避免重复叠播，并将 mixer/设备/解码错误降级为静音而不抛出到游戏主循环。
- [X] T007 [US3] 在 `src/pvz_game/presentation/scenes.py`、`src/pvz_game/presentation/renderer.py` 和 `src/pvz_game/app.py` 增加主菜单音乐开关/音量控制，并按菜单、对局、暂停、胜利、失败状态更新 `audio.py` 控制器；保存音乐偏好且不得改动 Simulation 或玩法规则（依赖 T005、T006）。
- [X] T008 [US3] 在 `tests/unit/test_progress_settings.py` 和 `tests/unit/test_audio_controller.py` 增加最少量定向检查，覆盖旧存档默认值/保存恢复、音量边界、场景转移、胜利 cue 单次触发及无设备静音降级。

**Checkpoint**: 玩家可关闭或调节音乐，核心游戏在没有音频设备时仍然可玩。

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 用最少必要验收确认素材、性能和 Windows 可玩交付。

- [X] T009 执行 `tools/validate_assets.py`，并只运行 `tests/unit/test_backgrounds.py`、`tests/integration/test_background_layout.py`、`tests/unit/test_progress_settings.py`、`tests/unit/test_audio_controller.py`；修复本功能涉及的素材/设置/音频错误，不运行完整 pytest 套件。
- [X] T010 在 `tools/benchmark.py` 的标准窗口场景调用与 `src/pvz_game/app.py` 相同的窗口缩放函数并运行 15 秒，保存 `docs/validation/014/standard-performance.json`；确认平均帧率至少 58 FPS、P95 帧间隔不超过 18 ms 且无连续慢帧回归。
- [X] T011 使用 `packaging/windows/build.ps1` 生成唯一命名的目录包 `dist/windows/PvzMiniGame-visual-audio-release/`，核对字体许可、背景/音乐和来源说明随包存在，并用 `packaging/windows/verify_bundle.py` 做一次短核心循环冒烟（截图记录到 `docs/validation/014/windows/desktop-smoke.png`）。
- [ ] T012 从新 Windows 目录包完成一次简短人工验收并记录到 `docs/validation/014/windows/desktop-smoke.md`：分别在最小窗口 1050×600 和 1920×1080 检查文字、布局及三个背景；设置音乐开/关与音量；开始、暂停/恢复并完成胜利结算；重启后确认偏好保留。若音频设备不可用，记录静音降级结果。

**T012 验收记录**：自动生成 1050×600 和 1920×1080 菜单截图，并完成 Windows 包的离线核心循环冒烟；交互式窗口验收因用户按 Esc 停止 Computer Use 而未执行，详见 `docs/validation/014/windows/desktop-smoke.md`。

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: 无工作项；项目初始化与音频框架均复用现状。
- **US1**: T001 可先独立完成。
- **US2**: T002 生成主图后执行 T003 背景构建/清单更新。
- **US3**: T004 准备音乐素材；T005 与 T006 可并行；T007 依赖 T005/T006；T008 依赖 T005–T007。
- **Final validation**: T009 在全部故事实现后执行；T010 在文字缩放变更后执行；T011/T012 依赖素材、代码和必要检查完成。

### User Story Dependencies

- **US1 (P1)**、**US2 (P1)** 可独立实现；US3 可与两个 P1 故事并行开发，但音乐控制 UI 集成依赖偏好与控制器。
- 三个故事都不依赖 Android 打包或改动模拟规则。

## Parallel Opportunities

- 在资源目录分离且不修改共享文件时，T002 背景素材生成与 T004 音乐素材准备可并行。
- T005 只修改进度设置，T006 只新增音乐控制器文件，可并行。
- T001、T003、T007 均会改动 `app.py` 或 renderer 呈现路径，应分开合并实施，避免共享文件冲突。

## Implementation Strategy

### Fast Playable Delivery

1. 完成 T001 文字清晰度和 T002–T003 场景背景；这些视觉更改不碰玩法。
2. 准备轻量音乐素材，完成 T005–T008 的设置、控制器和主菜单集成。
3. 执行 T009 定向测试与资产校验；T010 仅做一次 15 秒标准性能检查。
4. 构建一个新的 Windows 目录包并执行 T011/T012，形成可直接运行的可玩版本。

全量测试、Android 构建、额外视觉框架和核心玩法重构均不属于本 feature 的必要交付步骤。
