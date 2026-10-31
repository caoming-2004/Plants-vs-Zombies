# Tasks: 狗狗素材修复、倭瓜职责与安卓可玩版本

**Input**: Design documents from `specs/011-dog-mobile-refresh/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/platform-file-isolation.md`, `quickstart.md`

**Testing**: 只保留规格、宪章和 quickstart 要求的定向检查：狗狗帧边界、倭瓜生命周期、触控映射、Android 最小兼容构建、魅族 20 一局试玩、Windows 一局回归和平台文件哈希隔离。禁止全量 pytest、压力矩阵和重复打包。

**Organization**: 按规格中四个 P1 用户故事分阶段。Android 构建兼容性先作为仅阻塞 Android 故事的门槛验证。

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 为 Android 构建建立平台专属配置位置，并保留 Windows 当前 Python 环境。

- [X] T001 [P] 在 `packaging/android/app-config/.p4a` 固定 Android SDL2、横屏、ARM64 与应用包标识；将工具链参数与 Windows 构建配置分开。
- [X] T002 [P] 在 `packaging/android/p4a-recipes/pygame-ce/__init__.py` 建立只用于 Android 的 pygame-ce recipe，固定项目现用 2.5.8 源码及其 SDL2 原生依赖。
- [X] T003 在 `packaging/android/build.sh` 实现 Android 专属构建入口，将 `ANDROID_HOME`、`GRADLE_USER_HOME`、p4a recipe/storage、staging 和 APK 输出分别限定到 Android 路径（仓库内 SDK/cache 放入 `.tools/android/`，中间文件放入 `build/android/`），不读取或清理 Windows 目录。

## Phase 2: Foundational (Android Build Gate)

**Purpose**: 在 Android 游戏适配前验证现有 pygame-ce 是否能被目标打包管线编译；此门槛只阻塞 US3 的最终 APK，不阻塞 US1、US2 或 Windows 文件迁移。

- [ ] T004 使用 `packaging/android/build.sh` 构建一个最小 ARM64 SDL2/pygame-ce 2.5.8 APK，验证启动、单张打包图片读取和触控事件到达，并将结果或可复现错误记录到 `docs/validation/011/android/p4a-smoke.md`；失败时先修复 recipe/工具链，不扩大为全框架重写。

**Checkpoint**: Android recipe 可构建最小应用后，US3 可接入完整游戏；若环境不可用或构建失败，US1、US2 与 US4 可继续，Android 游戏代码暂缓集成。

## Phase 3: User Story 1 - 完整显示狗狗动作素材 (Priority: P1)

**Goal**: 从项目原始高清图集重新截取被窝和嗷嗷嗷动作帧，所有肢体、脚掌、尾巴完整显示；各狗狗地图尺寸相近。

**Independent Test**: 对照源图检查实际使用的全部姿态，再在菜单、卡片和地图尺寸下确认 0 帧误裁，并确认可游玩狗狗站立高度差不超过 20%。

- [X] T005 [P] [US1] 在 `tools/import_dog_assets.py` 为 `assets/skins/dogs/source/被窝.png` 与 `assets/skins/dogs/source/嗷嗷嗷.png` 定义逐姿态裁切边界和透明留白；以每个姿态的可见轮廓为准，不改写源图。
- [X] T006 [US1] 使用 `tools/import_dog_assets.py` 重新生成 `assets/skins/dogs/` 内相关 atlas、`manifest.json` 与 `provenance.json`，确保每帧只含对应狗狗且姿态顺序一致。
- [X] T007 [US1] 在 `assets/skins/dogs/manifest.json` 与 `src/pvz_game/presentation/animation.py` 校准显示比例和可见边界适配，确保菜单、卡片和地图均不裁掉身体、腿脚或尾巴，并满足规格的狗狗高度差约束。
- [X] T008 [P] [US1] 在 `tests/integration/test_animation.py` 增加必要断言，覆盖被窝/嗷嗷嗷实际使用帧的 alpha 可见边界、无相邻帧串入和狗狗站立显示高度差。
- [X] T009 [US1] 仅运行 `tests/integration/test_animation.py` 中狗狗帧边界用例（`-k dog_frame_bounds`）与 `tools/validate_assets.py`，人工检查待机、腿部变化最大、尾巴展开和卧倒姿态各一轮，并将一份结果记入 `docs/validation/011/dog-frames.md`。

**Checkpoint**: 两张原图的动作可连续显示，所有验收尺寸完整无裁切，站立尺度满足规格。

## Phase 4: User Story 2 - 使用胖宝宝作为倭瓜 (Priority: P1)

**Goal**: 胖宝宝保持独立狗狗外观，但使用倭瓜的一次性近距离重击规则，不再埋地或等待踩踏触发。

**Independent Test**: 在模拟中放置胖宝宝并令僵尸进入攻击范围，确认只重击/消耗一次；无目标与重开路径不遗留土豆雷武装状态。

- [X] T010 [US2] 在 `assets/config/balance.json` 将 `pangbaobao` 配置从 `potato_mine` 改为 `squash`，把价格、冷却、攻击距离、伤害和动作时长集中定义，并在 `src/pvz_game/config.py` 校验新职责字段。
- [X] T011 [US2] 在 `src/pvz_game/domain/plant_rules.py`、`src/pvz_game/domain/simulation.py` 与 `src/pvz_game/domain/systems.py` 实现胖宝宝倭瓜重击、单次伤害结算和攻击后消耗；移除该角色的埋地、武装计时及踩踏触发路径，保留其他植物规则。
- [X] T012 [US2] 在 `assets/skins/dogs/manifest.json` 与 `src/pvz_game/presentation/animation.py`/`renderer.py` 将胖宝宝已有狗狗姿态映射到倭瓜蓄势、重击和消耗反馈，并确认胖宝宝、黄黄仍是独立外观项且各自职责不被覆盖；不新增重复角色。
- [X] T013 [P] [US2] 在 `tests/unit/test_new_plant_rules.py` 与 `tests/unit/test_combat_and_lifecycle.py` 增加少量倭瓜用例，覆盖目标进入范围、一次命中并消耗、无目标和重开状态。
- [X] T014 [US2] 只运行 T013 新增用例及其配置校验依赖，并检查 `assets/config/balance.json` 中胖宝宝无 `potato_mine` 参数；将单次结果记录到 `docs/validation/011/squash.md`。

**Checkpoint**: 胖宝宝可在狗狗外观中独立选择并完成倭瓜重击，旧埋地行为不再触发。

## Phase 5: User Story 3 - 在安卓手机直接游玩 (Priority: P1)

**Goal**: 将完整游戏打包为可在魅族 20 侧载安装、离线运行的横屏触控 APK，沿用共享规则及约 12 姿态/秒植物动作。

**Independent Test**: 在魅族 20 离线安装 APK，只用触屏完成进入关卡、种植、收集资源、暂停/恢复、战斗、胜负与重开；地图/HUD 可见且动作无明显卡帧。

- [X] T015 [US3] 在 `src/pvz_game/presentation/animation.py` 保证植物循环动作按经过时间呈现约 12 个不同姿态/秒，避免把整体渲染刷新率误作动作帧率；在 `tests/integration/test_animation.py` 增加 `plant_pose_rate` 定向检查验证节奏。
- [X] T016 [US3] 在 `src/pvz_game/platforms/android/touch.py` 与 `src/pvz_game/presentation/input.py` 将 SDL 主触点坐标映射为现有逻辑指针事件，支持连续移动及松开点最近格判定，并过滤同一次触摸产生的合成鼠标事件。
- [X] T017 [US3] 在 `src/pvz_game/app.py` 接入 Android 触控事件和应用前后台生命周期；暂停/恢复保留当前模拟状态，触摸在占用格释放时复用现有拒绝流程。
- [ ] T018 [US3] 在 `src/pvz_game/platforms/android/display.py`、`src/pvz_game/presentation/coordinates.py` 与 `renderer.py` 适配横屏及 16:9/20:9 可视范围和安全边距，保证地图各行列、HUD 与主要控件均可见可触达。
- [X] T019 [US3] 在 `src/pvz_game/resources.py` 与 `src/pvz_game/platforms/android/runtime.py` 支持 APK 内只读素材定位、Android 应用私有日志路径及资源缺失中文提示；不得将运行文件写入 `assets/` 或 Windows 用户数据目录。
- [X] T020 [US3] 在 `packaging/android/` 接入共享 `src/pvz_game/` 和 `assets/` 到正式应用入口，沿用 T003 的独立构建缓存，并通过 `packaging/android/build.sh` 生成最终 APK 到 `dist/android/PvzMiniGame-meizu20-arm64.apk`。
- [ ] T021 [P] [US3] 在 `tests/integration/test_drag_input.py` 增加最少量触控归一化/合成事件去重用例；只运行 `-k android_touch`、对应现有拖放规则用例和 `tests/integration/test_animation.py -k plant_pose_rate`，不运行整个测试目录。
- [ ] T022 [US3] 将 `dist/android/PvzMiniGame-meizu20-arm64.apk` 离线安装到魅族 20，完成一次核心对局及 10 秒植物动作观察；记录 APK 哈希、安装/启动结果和任何剩余问题到 `docs/validation/011/android/device-smoke.md`。

**Checkpoint**: 魅族 20 可无电脑依赖安装 APK，并通过一次触屏完整对局。

## Phase 6: User Story 4 - 隔离 Windows 与 Android 文件 (Priority: P1)

**Goal**: 两端专属构建、缓存、临时文件、日志及交付物严格分目录；一端构建/清理不改变另一端文件。

**Independent Test**: 两端正式产物都存在时，分别记录文件清单和 SHA256；各运行一次平台专属构建或清理后，另一端路径和哈希不变。

- [X] T023 [US4] 将 Windows 专属 `packaging/pvz_game.spec`、`packaging/launcher.py`、`packaging/开始游戏.txt`、`tools/build.ps1`、`tools/copy_release_files.py` 和 `tools/verify_bundle.py` 迁至 `packaging/windows/`，同步更新 `README.md` 与本 feature 的构建说明。
- [X] T024 [US4] 修改 `packaging/windows/pvz_game.spec`、`packaging/windows/build.ps1` 与 Windows 发行辅助脚本，显式使用 `build/windows/` 和 `dist/windows/`，限制清理只作用于 Windows 子目录，并保持不生成测试 ZIP。
- [ ] T025 [US4] 使用 `packaging/windows/build.ps1` 构建一次最终 Windows 目录包到 `dist/windows/`，从目录包启动并完成一次核心循环；记录结果到 `docs/validation/011/windows/desktop-smoke.md`。
- [ ] T026 [US4] 在 `docs/validation/011/platform-isolation.md` 记录 `packaging/windows/`、`packaging/android/`、`.tools/android/`、`build/windows/`、`build/android/`、`dist/windows/` 与 `dist/android/` 的相对路径和 SHA256；分别执行两端专属清理前后核对，确认任一平台操作都未改变另一端配置、缓存或发行文件。
- [X] T027 按 `contracts/platform-file-isolation.md` 分别清理两端 staging 和临时测试 APK/EXE；保留最终 `dist/windows/` 目录包及 `dist/android/PvzMiniGame-meizu20-arm64.apk`，确认没有测试 ZIP。

**Checkpoint**: 双平台交付可分别启动，清理和构建彼此无副作用，临时包已清理。

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: T001、T002 可并行；T003 依赖 Android 配置与 recipe。
- **Phase 2 Android Gate**: T004 依赖 T003。它只阻塞 US3 的正式 Android 接入，不阻塞 US1、US2 或 Windows 打包隔离工作。
- **US1、US2**: 两个故事互不依赖；T005–T009 可与 T010–T014 并行推进。
- **US3**: 12 姿态/秒检查 T015 可在 Android Gate 通过后独立完成；触控代码随后接入。最终 APK T020 和设备验收 T022 依赖 T004、US1 素材与 US2 倭瓜完成。
- **US4**: T023–T024 的 Windows 目录迁移与 US1/US2/US3 的共享游戏逻辑工作互不修改同一文件，可并行；T025–T027 必须等最终 Android APK 存在。
- **Final cleanup**: T027 是最后一步；只能清理任务明确的 staging/临时文件，不得递归删除 `build/`、`dist/` 根目录。

### User Story Dependencies

- **US1 (P1)**: 依赖 Setup；可与 US2、Android Gate 和 Windows packaging migration 并行。
- **US2 (P1)**: 依赖 Setup；可与 US1 和 Windows packaging migration 并行。
- **US3 (P1)**: 依赖 Android Gate、US1 和 US2 的功能完成，最终可玩 APK 安装验收需魅族 20。
- **US4 (P1)**: 平台目录迁移可与 US1/US2/US3 代码工作并行；正式双端哈希核对依赖两端最终包。

## Parallel Opportunities

- Setup 阶段可并行准备 `packaging/android/app-config/.p4a`（T001）和本地 pygame-ce recipe（T002）。
- Android Gate 同时，US1 图集工作（T005–T009）和 US2 规则工作（T010–T014）可并行，因为修改目录互不重叠。
- Windows packaging 迁移（T023–T024）可与 US1/US2 实现并行；但正式 Windows 包与 Android APK 的交叉哈希核对必须等两端构建完成。
- 不并行运行多个 Android full builds，避免 p4a 使用同一 Android 专属缓存时发生竞争。

## Implementation Strategy

### Fast Playable MVP

1. 完成 Android recipe/config/build scaffold，并做一次最小 pygame-ce 2.5.8 APK 兼容构建（T001–T004）。失败先解决工具链门槛，暂停 Android UI 扩展。
2. 并行完成两项玩法增量：重新裁切/验收狗狗帧（US1）与胖宝宝倭瓜规则（US2）。
3. 在已有代码和素材上加入触屏/横屏/资源适配，构建一个正式 APK 并在魅族 20 完成一次离线对局（US3）。
4. 将现有 Windows builder/config 迁入隔离目录，构建并启动一次 Windows 目录版；记录双端文件校验值，清理临时测试产物（US4）。

完整可玩 MVP 需要 US1–US4：只完成素材显示或只完成 Android 空壳 APK 都不能满足用户可玩与平台隔离要求。

## 当前执行记录（2026-10-30）

- T005–T015 与 T023–T024 已完成；定向素材/倭瓜/动画检查和资源校验通过，Windows builder 已迁入隔离目录。
- Android 工具链已配置在 WSL Ubuntu 24.04 与 Android 专属 ext4 缓存；SDL2/pygame-ce ARM64 smoke 构建、Gradle 打包均通过。最终 APK 已产出，`aapt` 元数据检查通过；构建及隔离细节见 `docs/validation/011/android/`。
- T016、T017、T019、T020 已实施；T018 的横屏/可视安全边距仍需设备验收。T004 尚缺真实运行时图片读取和触控到达验证，T021 的定向 Android 触控测试未在本轮执行。
- T022 未完成：ADB 未连接魅族 20 或其他 Android 设备，尚不能声称安装或真实对局验收。按用户要求控制测试范围，本轮只进行必要的 smoke APK 构建与最终包检查。
- T025 Windows 目录包和离线 `--smoke-play` 已通过；真实窗口操作因用户物理 Escape 停止信号中止，因此菜单点击/鼠标种植验收仍未完成。
- T026 双端隔离清单/前后哈希记录仍未完成。本轮 Android 输出只写入 `dist/android/` 与 Android 专属 WSL 缓存；Windows 目录包保留。
- T027 本轮已移除 Android release staging 与临时旧 APK；Android 验证日志已精简为成功 smoke/release 两份。此前 Windows staging EXE、smoke 工作目录和遗留独立 ZIP 已清理；最终 Windows 目录包保留。
