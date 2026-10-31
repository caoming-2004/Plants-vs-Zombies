# Implementation Plan: 狗狗素材修复、倭瓜职责与安卓版本

**Branch**: `011-dog-mobile-refresh` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-dog-mobile-refresh/spec.md`

## Summary

在现有 Python/Pygame 游戏上完成被窝和嗷嗷嗷图集的逐帧重新裁切、完整显示检查，将胖宝宝由土豆雷规则切换为倭瓜一次性近距离重击，并把同一核心游戏适配到用户指定的魅族 20，交付可直接安装的 Android APK。Windows 与 Android 的平台专属入口、配置、构建缓存、中间文件、日志和发行物严格分目录；现有游戏核心代码和相同的原始素材继续共用一份，避免两端复制后互相漂移。

Android 端沿用 Pygame/SDL2，不重写玩法系统。研究显示 python-for-android 的 SDL2 APK 流程适用，但它尚无已合并的 pygame-ce 2.5.8 配方；因此先做一次限范围构建兼容性验证，再推进触屏和整局适配。Windows 端继续用现有 PyInstaller 路径，迁入专属目录并保留当前可玩流程。

## Technical Context

**Language/Version**: 共用游戏 Python 3.12；Windows x64；Android 在 Linux/WSL 构建 arm64-v8a APK。

**Primary Dependencies**: pygame-ce 2.5.8 与 SDL2；Windows 使用 PyInstaller 6.x；Android 使用 python-for-android 的 SDL2 启动方式及项目内私有 pygame-ce 配方；不引入第二套游戏引擎。

**Storage**: 游戏配置、关卡、图集和来源记录仍位于仓库共享 `assets/`；Android 应用资源打入 APK。运行日志分别进入 Windows 用户数据目录与 Android 应用私有目录。

**Testing**: 少量已有 pytest 定向用例，覆盖素材帧边界、倭瓜规则和触屏映射；每个平台一次实际运行验收。Windows 发行包和 Android APK 分别在各自目录生成；不跑全量测试矩阵、不生成测试 ZIP。

**Target Platform**: Windows x64 桌面版；用户指定的魅族 20（横屏触控，Android arm64）。

**Project Type**: 单一离线 Python/Pygame 游戏，包含隔离的 Windows 和 Android 运行/发行入口。

**Performance Goals**: 沿用现有固定步进和植物动画每秒约 12 个不同姿态；在魅族 20 上完整一局无明显卡帧、输入可用，不能把植物动画频率误当作游戏整体刷新率。

**Constraints**: 保持单关完整胜负循环和既有 Windows 可玩能力；APK 可侧载安装且离线可玩；横屏界面适配；Windows/Android 的平台专属文件不得交叉读写或清理；共同核心代码与相同素材不重复维护；只执行验收必须的检查。

**Scale/Scope**: 两只既有狗狗图集修复、一个植物职责更换、一个 Android 机型、现有一关和双平台发行目录；不增加新关卡、联网服务或应用商店发布流程。

## Constitution Check

| 原则 | 状态 | 计划依据 |
|---|---|---|
| I. 完整可玩的核心循环优先 | PASS | 先保证现有关卡在两端都能进入、种植、战斗、产生胜负并重开；不扩展无关内容。 |
| II. 游戏规则与界面渲染分离 | PASS | 胖宝宝规则仍由领域逻辑判定；触屏输入仅映射为现有命令/逻辑坐标；渲染和平台启动适配不复制种植或战斗规则。 |
| III. 关键数值集中管理 | PASS | 倭瓜的费用、目标范围、伤害和动作时间统一放入现有玩法配置；模拟和表现引用同一规则定义。 |
| IV. 核心玩法修改必须验证 | PASS | 对倭瓜正常攻击、无目标/目标进入范围、消耗与重开执行针对性检查；再做两端各一次完整流程验收。 |
| V. 新增功能保持已有功能可运行 | PASS | 安卓适配复用共享核心；Windows 发行路径保留；最后分别启动 Windows 版和魅族 20 APK，核对核心胜负与重开。 |
| 开发约束：复用结构、职责和数值边界 | PASS | 保留 `Simulation`、`systems`、表现层和 `assets/config`；只新增必要的平台适配/私有打包配方，无第二游戏框架。 |

**Pre-Phase 0 Gate**: PASS。无宪章冲突或必须豁免的复杂抽象。

## Phase 0: Research Decisions

见 [research.md](research.md)。决策如下：

1. 复用 Pygame/SDL2 核心。用 python-for-android 的 SDL2 APK 管线；先在 Android 专属构建环境中适配并验证 pygame-ce 2.5.8 配方。若该最小构建失败，暂停大规模 Android 改造，先修正此配方，不进行游戏引擎重写。
2. Windows 构建继续 PyInstaller，但其配置和构建入口移入 `packaging/windows/`；Android 配置和 p4a 私有配方放入 `packaging/android/`。
3. 两端构建临时目录和最终交付物分别使用 `build/windows/`、`build/android/`、`dist/windows/`、`dist/android/`。各自清理脚本只接受本平台目录，不对 `build/` 或 `dist/` 根目录做宽泛递归删除。
4. 游戏规则、原图和通用素材仍在现有共享位置；Android 的触屏、生命周期或文件路径差异仅放在 Android 平台适配目录。

## Phase 1: Design & Contracts

- [data-model.md](data-model.md)：列出狗狗帧、植物职责、玩法配置及平台发行物的权威来源与不变量，不新增持久化游戏数据。
- [contracts/platform-file-isolation.md](contracts/platform-file-isolation.md)：定义共用源文件与 Windows/Android 专属配置、缓存、日志、测试输出和发行物的目录边界及清理规则。
- [quickstart.md](quickstart.md)：限定本轮必要的定向检查、兼容性构建小步验证、两端实际运行和文件隔离核验。

本应用没有外部 API 或联网服务，不产生网络接口 contract。

## Project Structure

### Documentation

```text
specs/011-dog-mobile-refresh/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── platform-file-isolation.md
├── checklists/
│   └── requirements.md
└── tasks.md                         # 后续由 $speckit-tasks 创建
```

### Source and platform files

```text
assets/                              # 共用权威来源；原图不按平台复制
├── config/balance.json
├── levels/day_01.json
└── skins/{dogs,dogs_photo,default}/
    ├── manifest.json
    ├── provenance.json
    ├── atlas*.png
    └── source/

src/pvz_game/                        # 共用领域和游戏表现
├── domain/{models.py,simulation.py,systems.py,plant_rules.py}
├── presentation/{animation.py,input.py,renderer.py,scenes.py}
└── platforms/                       # 仅需系统差异时增加，按端独立子目录
    ├── windows/
    └── android/

packaging/
├── windows/
│   ├── pvz_game.spec
│   ├── launcher.py
│   ├── build.ps1
│   ├── copy_release_files.py
│   ├── verify_bundle.py
│   └── user-docs/
└── android/
    ├── build.sh
    ├── app-config/
    └── p4a-recipes/pygame-ce/

tools/                               # 共用素材/JSON/测试辅助，不生成平台发行物
tests/{unit,integration,replay}/     # 继续验证共用领域和输入边界

build/
├── windows/                         # PyInstaller 专属 staging
└── android/                         # Android app staging/构建结果

dist/
├── windows/                         # Windows 最终可玩目录包
└── android/                         # 最终侧载 APK

docs/validation/011/
├── windows/
└── android/
```

**Structure Decision**: 不把玩法或原始素材复制成两套游戏。平台差异按专属目录隔离；Windows 构建只读共享 `src/`、`assets/` 并写 Windows 目录，Android 构建只从共享源生成 Android staging 并写 Android 目录。Windows 端现有 `.venv` 保留；Android SDK/NDK、p4a 环境和缓存使用独立 Linux/WSL 环境。任何平台的 build/clean 操作均不枚举、覆盖或删除另一端目录。

## Design Decisions

1. **原图裁切与可见边界**：将项目中的被窝、嗷嗷嗷原始高清图保留为不可变 source；依据各姿态的可见轮廓逐帧重新界定范围并保留透明缓冲，更新既有 atlas、manifest、provenance。复用 `animation.py` 的可见边界适配与缓存。验收所有实际使用姿态在菜单、卡片、地图展示时腿脚和尾巴完整；跨角色站立高度差控制在规格的 20% 内。源图出现透明或图像学边界时以实测 alpha/背景为准，不按文件总尺寸均分后直接裁切。
2. **胖宝宝改为倭瓜**：将 `assets/config/balance.json` 中胖宝宝角色由 `potato_mine` 切换到独立 `squash` 职责；在 `config.py`、`simulation.py`、`systems.py` 及必要的表现状态中移除该角色的布置埋地、武装计时和踩踏触发分支。复用通用扣费、放置和冷却管线；倭瓜攻击/消耗状态由模拟持有，费用、攻击距离、伤害、蓄势/重击时间只在平衡配置定义。只影响胖宝宝 ID，不改变其他植物/狗的角色职责。
3. **Android 触控和画面**：保持 1050×600 逻辑画布及 5×12 地块；将 SDL 触控事件显式转换到现有逻辑指针/拖放流程，限制一个主要触点，避免同一触摸再经合成鼠标事件重复操作。使用松手点做唯一最近格判定；占用格仍拒绝。横屏全屏绘制时保留安全边距，20:9 与 16:9 均完整显示关卡、HUD 和主操作。应用暂停/恢复以平台生命周期信号暂停/继续同一模拟状态，不重置关卡。
4. **平台资源与用户数据**：共用 `resources.py` 读取随包资源的通用接口，Android 只添加平台资源根定位和日志位置适配，不将可写文件放入 APK 安装资源目录。Windows 错误日志继续放在 Windows 用户数据路径；Android 运行日志放在应用私有目录。两端不共享或交叉访问可写用户数据。
5. **文件严格隔离**：将 PyInstaller spec、启动入口、Windows builder 和 Windows 专属发行辅助文件迁入 `packaging/windows/`；Android build 配置、p4a 私有 pygame-ce 配方和 Android builder 放 `packaging/android/`。所有构建脚本显式设置本平台 staging、缓存、测试和发行路径。PyInstaller 输出改为 `build/windows/` + `dist/windows/`；p4a storage/build 与最终 APK 使用 Android 专属位置，APK 归档到 `dist/android/`。Android 端不执行 Windows `build.ps1` 或 PyInstaller 清理；Windows build 不调用 p4a 清理。
6. **环境边界**：在 Linux/WSL 侧配置 Android 构建专用 Python、JDK、SDK、NDK 与 p4a；依照选定 p4a 版本锁定可构建的工具链/API，并仅构建魅族 20 所需 `arm64-v8a`。当前 Windows Python `.venv` 和 PyInstaller/pygame-ce 不被 Android 安装或升级。Android SDK/build 缓存置于 Android 专属 WSL 路径，输出 APK 再拷入 `dist/android/`；不把 p4a 的全局清理命令指向项目通用根目录。
7. **最小验收与清理**：运行新增/被影响的定向规则和输入检查、一次原图/atlas检查、一次 Android APK 构建兼容 smoke、魅族 20 上一次完整对局、一轮 Windows 完整流程和独立目录包 smoke。收集隔离前后文件清单/校验值。完成后只清理本轮 staging 与临时测试 APK/EXE；保留最终 `dist/windows/` 可玩版和 `dist/android/` APK，不生成测试 ZIP。

## Focused Validation Plan

1. **帧图像**：对被窝和嗷嗷嗷全部地图/卡片会用到的帧做资源校验及可见轮廓检查；人工检查待机、腿部变化最大、尾巴展开与卧倒姿态；确认没有切入邻帧、截掉脚尾，且站立高度尺度满足规格。
2. **倭瓜规则**：只运行胖宝宝配置校验、一次目标进入范围后重击消耗、无目标保持/失败路径、土豆雷埋地分支已无胖宝宝引用，以及重开状态归零对应的定向用例。
3. **Android 最小构建验证**：在独立 Android 环境先构建最小 SDL2/Pygame CE 2.5.8 启动包，确认私有 recipe、ARM64 native 库、资源访问和 SDL 触控事件可用；成功后只构建功能 APK 一次。若此步骤失败，保留日志到 `docs/validation/011/android/`，先修 recipe/工具链，不继续叠加玩法或 UI 测试。
4. **魅族 20 试玩**：离线安装 APK；横屏启动；触屏主菜单进入游戏，放置植物、拖动并遇占用格、收集资源、暂停/恢复，检查12姿态/秒观感，完成一局胜负与重开。保存一次短记录及 APK 哈希。
5. **Windows 回归与隔离**：以 Windows `.venv` 运行相关用例和一次核心循环；用专属 PyInstaller 配置生成正式 Windows 目录包并启动一次。记录构建前后 `build/android/`、`dist/android/` 文件哈希；针对 Android 的临时文件清理后，核对 `build/windows/`、`dist/windows/` 的哈希未变化，反向做一次。
6. **范围控制**：不跑全量 pytest，不做六套角色组合或长时压力矩阵，不生成测试 ZIP。只删除已确认由本轮产生的临时文件；正式 Windows 包和最终 Android APK 按用户交付保留。

**Post-design Constitution Check**: PASS。跨平台适配保留规则单一权威源和共用代码；发行/构建边界彼此隔离；没有引入未论证的第二引擎。

## Complexity Tracking

无宪章违规。Android 私有 pygame-ce 配方是构建复用所必需的窄适配，先以最小 APK smoke 验证，避免把平台不确定性扩散到共享游戏代码。
