# Research: 狗狗素材修复、倭瓜职责与双平台发行

**Date**: 2026-10-30  
**Feature**: [spec.md](spec.md)

## Current Project Findings

- 游戏核心是 Python 3.12、pygame-ce 2.5.8 单项目，领域规则在 `src/pvz_game/domain/`，Pygame 输入/渲染在 `src/pvz_game/presentation/`，数值和关卡在 `assets/config/` 与 `assets/levels/`。
- 现有 Windows builder 是 `tools/build.ps1`，PyInstaller 配置是 `packaging/pvz_game.spec`，启动器和 bundle helpers 位于同一个混用目录；builder 当前写到根 `build/`、根 `dist/`，且默认生成 ZIP。
- `.gitignore` 已忽略根 `build/`、`dist/`、`.tools/`。新计划在这些目录内再按平台分开，便于各自清理，不改变共享游戏源文件的权威位置。
- `src/pvz_game/app.py` 当前只处理鼠标按下、移动、抬起；Android 需要明确处理 SDL 触控事件并归一化到已有逻辑指针输入。现有连续拖动和最近格拒绝规则可以复用。
- `assets/config/balance.json` 当前把胖宝宝定义为 `potato_mine`；config 校验、模拟和系统推进均有该规则分支，必须按胖宝宝角色 ID 改为倭瓜，不可只改名称/卡片文案。
- 被窝、嗷嗷嗷原始源图与对应 atlas/manifest/source records 都在 `assets/skins/dogs/`。素材源继续共用，只更新派生帧和元数据。
- 当前 Windows 工具链可看到项目 `.venv` 的 pygame-ce 2.5.8 与 Java、WSL 命令入口；PATH 中未发现 `adb`、Gradle、Buildozer 或 Briefcase。WSL distro listing 在本执行环境返回 `ACCESS_DENIED`，因此后续 APK 构建前需要确认可用的 Linux/WSL Android 工具链；此次计划阶段不安装系统级 SDK/NDK。

## Decisions

### 1. 保持一个游戏核心，不复制两套源码

**Decision**: 共用 `src/pvz_game/domain/`、通用表现和 `assets/`；确有系统差异时只新增 `src/pvz_game/platforms/android/` 或 `windows/` 小型适配模块。平台入口、打包配置、缓存、中间产物、测试证据和最终交付物单独放在各自目录。

**Rationale**: 用户要求隔离以避免一端构建/清理干扰另一端，隔离范围落实为平台专属文件和所有生成文件；复制相同玩法和素材会新增漂移来源，违背复用架构和快速交付目标。

**Alternatives considered**: 把全部 `src/` 和 `assets/` 复制成 Windows 与 Android 两份。拒绝，因为每次修复都需重复同步，并不能减少构建输出相互覆盖的风险。只把 APK 与 EXE 分开、但共用 build 缓存。拒绝，因为中间文件和清理脚本仍可能交叉写入。

### 2. Android 封装复用 SDL2/Pygame 的兼容路线

**Decision**: 以 python-for-android 的 SDL2 bootstrap 生成 arm64 APK；使用 Android 专属私有 `pygame-ce` recipe，将构建版本固定到项目 pygame-ce 2.5.8，并在玩法/界面改造前做一次最小 native APK 兼容验证。Windows 仍用 PyInstaller，不使用 Android builder 对 Windows Python 环境做安装或升级。

**Rationale**: python-for-android 官方 quickstart 描述 SDL2 应用可生成 APK、按 recipes 构建 native 依赖，并允许项目私有 recipe 和固定 distribution 名。Pygame CE 建立在 SDL 之上，因此此路线保持现有游戏架构，代价是需适配其 Android 编译配方。

**Risk and mitigation**: 当前官方 p4a 的 pygame-ce recipe PR #2971 仍是开放 PR，配方基于 2.4.0，并说明部分功能和依赖未经验证；本项目依赖 2.5.8。第一项实现任务必须先构建最小 APK、在魅族 20 安装启动并核对输入/资源；不通过时暂停共享代码改动，修复配方或工具链后再继续。

**Alternatives considered**:

- Briefcase 的通用 Pygame 模板：不采用。Briefcase 当前文档对 Pygame 标注不支持 Android/iOS/Web 部署；项目现有 pygame-ce/Windows 打包也不等于 Android bootstrap 已可用。
- 完整改写为 Kivy/原生 Android：不采用。会重写 Renderer、输入、动画与核心循环，超出快速可玩版本范围且增加规则分叉。
- 仅打包成浏览器 Web 页面：不采用。当前验收要求是在魅族 20 上直接安装和离线运行 APK。

### 3. 使用触控适配而不复制拖放规则

**Decision**: 将 SDL `FINGERDOWN/FINGERMOTION/FINGERUP` 的主触点转换为现有逻辑屏幕坐标和指针生命周期；与平台可能发出的合成鼠标事件去重。最近格计算、占格拒绝、阳光扣除仍走既有公共路径。

**Rationale**: 复用已有连续拖动与规则命令可让两端逻辑一致，只需新增 Android 输入边界和触屏回归。

**Alternatives considered**: Android 单独实现一套种植判定；拒绝，因为会出现平台间规则分叉。

### 4. Windows/Android 文件边界

**Decision**:

| 类型 | Windows | Android |
|---|---|---|
| 平台打包入口与配置 | `packaging/windows/` | `packaging/android/` |
| 平台 staging/中间产物 | `build/windows/` | `build/android/` |
| 最终交付物 | `dist/windows/` | `dist/android/` |
| 验收材料 | `docs/validation/011/windows/` | `docs/validation/011/android/` |
| 运行数据 | Windows 用户数据目录 | Android app-private 数据目录 |
| 游戏规则和相同原始素材 | 仓库共享 `src/`、`assets/` 一份 | 同一共享源，不由 Android 构建脚本写回 |

Windows Builder 必须显式将 PyInstaller `--workpath` 指向 `build/windows/`，`--distpath` 指向 `dist/windows/`。Android Builder 使用独立 Linux/WSL Android SDK/NDK、p4a distribution 和 storage/build 目录，APK 最后复制到 `dist/android/`。清理命令只接受调用端的专属子目录；禁止 `Remove-Item build`、`Remove-Item dist`、`p4a clean_all` 后接通用根清理一类宽泛操作。

**Rationale**: 当前 Windows 打包写根 `build/`、`dist/`，Android p4a 有自己的全局构建分发和清理命令；把路径、环境和清理责任显式划开，才能防止共享缓存/路径导致意外覆盖。校验由另一端预先记录的路径清单与 SHA256 验证。

### 5. 狗狗图集和胖宝宝规则

**Decision**: 原图只读，重新按每个实际姿态的 alpha-visible bounds 建帧并留透明 padding；更新现有 atlas/manifest/provenance。胖宝宝从 `potato_mine` 的武装状态彻底改为 `squash` 一次性近距离重击，`balance.json` 是费用、范围、伤害和动作时间的唯一来源。

**Rationale**: 单纯放大/平移无法补回被裁肢体；只改卡片名称也不会移除土豆雷的埋地与踩踏分支。现有 `Animator`、配置校验和 Simulation 生命周期可以延伸使用。

## Official References

- [python-for-android Getting Started](https://python-for-android.readthedocs.io/en/latest/quickstart.html)：SDL2 可生成 APK；Android SDK/NDK 与 JDK 依赖；APK 与 ABI 构建参数；项目私有 recipes、distribution 命名和清理命令。
- [python-for-android Build Options](https://python-for-android.readthedocs.io/en/latest/buildoptions.html)：SDL2 bootstrap 是游戏/SDL 应用入口，支持横屏与 cutout 配置；触摸生命周期需由应用显式适配。
- [python-for-android Recipes](https://python-for-android.readthedocs.io/en/latest/recipes.html)：native Python 扩展需要编译 recipe，recipe build 使用独立构建目录。
- [Pygame CE on Android PR #2971](https://github.com/kivy/python-for-android/pull/2971)：目前可参考的 pygame-ce Android recipe 仍未合并，且文档声明部分模块/依赖未完整验证。
- [pygame-ce repository](https://github.com/pygame-community/pygame-ce)：pygame-ce 基于 SDL；本地项目当前固定 2.5.8。
- [Briefcase platform support](https://briefcase.readthedocs.io/_/downloads/en/v0.3.24/pdf/)：Briefcase Pygame 模板不支持 Android/iOS/Web 部署，故不选它包装现有应用。

## Open Questions

没有产品问题待澄清。唯一的工程风险为 pygame-ce 2.5.8 在 p4a/SDL2 下的 native 编译兼容性；以最小 Android APK 构建与魅族 20 安装启动作为早期实现门槛，不扩展为全框架比较或重复试包矩阵。
