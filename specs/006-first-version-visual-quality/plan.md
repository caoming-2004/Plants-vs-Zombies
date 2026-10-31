# Implementation Plan: 第一版背景与角色画质、流畅度恢复

**Branch**: 006-first-version-visual-quality | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from specs/006-first-version-visual-quality/spec.md

## Summary

以第一版（提交 7305e3d）为背景和游戏节奏基线。保留其场景构图与玩法区域，重新绘制至少 2× 原背景尺寸（2800×1200）的背景主图；网络候选已核验但与首版构图/风格不适配，因此不引入第三方背景文件。修复卡通狗素材在 64×64 处理中丢失细节的问题，沿用现有动作表、图集、manifest、锚点和角色缩放管线。沿用 Windows/Pygame 的固定 60Hz 模拟和 60 FPS 显示循环，收紧打包实机报告的验收阈值，补齐第一版同机基线、慢帧分布和真人操作反馈证据。

## Technical Context

**Language/Version**: Python 3.12 x64

**Primary Dependencies**: pygame-ce 2.5.x; PyInstaller 6.x 仅用于现有 Windows 发行流程；不新增运行时依赖。

**Storage**: 仓库内 PNG、JSON 清单/来源记录和 Markdown 验收证据；不引入网络运行时资源。

**Testing**: pytest 8.x；tools/validate_assets.py、素材预览/遮挡验证；打包 Windows 实机显示与真人输入验收。

**Target Platform**: Windows 11 x64 离线打包游戏；基线和新版均在用户当前电脑与同刷新率/窗口条件下验收。

**Project Type**: 单一 Python/Pygame 桌面游戏，使用 src/pvz_game、本地素材管线和 PyInstaller 打包。

**Performance Goals**: 玩法更新与帧率设定沿用第一版的 60Hz/60 FPS；标准场景渲染循环平均值至少 58 FPS 且不低于同条件第一版基线的 97%、P95 帧间隔≤18ms；压力场景 P95≤20ms；两者不得连续两帧超过33ms；真实操作反馈 P95≤100ms。循环采样高于60时如实记录，不单独作为失败。

**Constraints**: 不改变模拟规则、动作节奏、角色尺寸/遮挡验收、输入坐标和第一版场景构图；最终游戏离线运行；外部素材须核实 CC0 或其他可再发行许可及来源；图像改善不应增加每帧图像处理。

**Scale/Scope**: 一张第一版风格白天背景；现有默认、狗狗卡通、狗狗照片素材；三档窗口截图；标准和固定压力场景各60秒；至少20次真实输入样本。

## Constitution Check

**Pre-Phase 0**

- I. 完整可玩的核心循环优先：PASS — 只调整背景、现有角色资源和显示节奏；开始、种植、战斗、胜负及重开流程保留并回归。
- II. 游戏规则与界面渲染分离：PASS — 背景/角色变化放在素材与渲染层；60Hz模拟权威仍位于配置和现有 Simulation 主循环，不以渲染补偿玩法速度。
- III. 关键数值集中管理：PASS — 保持 tick_hz=60；帧验收阈值集中在性能诊断定义，不散落到玩法逻辑或平衡参数。
- IV. 核心玩法修改必须验证：PASS — 不计划改变核心玩法；仍需重放既有输入并完成实机帧率、视觉和操作验证。
- V. 新增功能保持已有功能可运行：PASS — 沿用现有素材校验、皮肤回退、回放和打包流程，执行经典/卡通/照片外观及核心循环回归。
- 开发约束：PASS — 不加依赖、不新增服务/存储/项目结构；复用背景生成、导入、manifest、renderer、benchmark和release管线。

**Post-Phase 1**: PASS — 设计保持上述边界；指标、输入样本和素材来源以可读 JSON/Markdown 本地记录。没有新增架构层或宪章例外。

## Design Decisions

### 背景资源

1. 以历史第一版背景作为位置、视角、道路/房屋轮廓、光照和配色参照。高分辨率工作主图按其 7:3 构图输出至少 2800×1200，重新绘制细节而非插值放大第一版原图。
2. 已联网核验 OpenGameArt 的 1920×1080 CC0 分层草地组件（作者 Puffolotti）和 1024×1024 CC0 俯视草地纹理（作者 Starry Skydancer）。二者不含第一版房屋/道路且画风不匹配，未下载或纳入发行；最终背景用项目图像生成重绘，源图与派生关系记入 `assets/sources.json`。
3. 将完成的静态背景随游戏离线分发，沿用 assets/sources.json 来源记录、assets/skins/default/manifest.json UI 资源入口和 tools/generate_background.py 的可复建流程。静态画面在启动时装载、缓存到逻辑画布；不逐帧合成/动画网络素材。
4. 在 1050×600、1260×720、1920×1080 核对切片/布局；维持游戏现有逻辑画布、落点和坐标变换，不扩展或重排种植格。

### 狗狗清晰度

1. 保留三张用户原始动作表与 005 既定照片/卡通映射；沿用 tools/import_dog_assets.py 的 10×6 输入读取、锚点、帧时长、manifest/provenance 与可重复图集构建。
2. 对卡通分支删除 cartoonize_frame() 的 64×64 预缩小/量化再放大环节。在 256×256 姿势单元的原有效分辨率直接做色彩归纳和边缘清理，不改变源动作顺序、身份特征、帧持续时长、脚底基线和攻击锚点。照片分支继续使用原姿势的干净透明裁切，避免两个分支互相覆盖。
3. 沿用 skin_catalog.py、animation.py、renderer.py 的裁切、锚点和预览/游戏显示缩放路径。图像平滑或清理只在素材生成阶段做；运行时继续使用已有图集缓存和缩放缓存。
4. 用现有 dog_validation.py 遮挡检查和 preview_animations.py 导出预览；每种皮肤逐角色/逐必要动作目测，并核对三种窗口尺寸、轮廓杂边、裁切、身份与已有25%主体遮挡上限。

### 帧节奏及实机验收

1. 玩法更新与帧率设定保持第一版60Hz/60 FPS，不变更 tick_hz、角色速度、动作姿势速率或既有最多5个积压模拟步的处理策略；若有掉帧，仅优化实际 CPU/渲染/合成瓶颈。
2. 复用 src/pvz_game/app.py::benchmark_window、src/pvz_game/presentation/performance.py::SCENES 与 tools/benchmark.py --window。帧统计新增 >33ms 慢帧总数和最长连续数；环境元数据由 app.py 采集，interval 汇总函数只负责帧序列统计。
3. 在修改前用 7305e3d 版和当前用户电脑记录第一版/现状配对基线；如果历史二进制无法启动，则从该提交重建基线，并仅给基线加入不改变玩法、渲染或帧等待行为的采样输出。两版固定同一显示刷新率、1260×720窗口、皮肤、场景、60秒时长。标准场景新版平均循环帧率至少58 FPS且不低于第一版同条件值的97%；循环采样超过60时记录，不因其高于60判失败。
4. 发行版用 Windows display driver 实测标准和压力场景各60秒；除诊断自动样本外，手工完成至少20次有效的种植、铲除和收集操作。保存设备/刷新率/窗口、完整帧间隔、FPS/P95、>33ms 总数/最长连续值、操作分布/P95/漏事件和重复事件。
5. 使用第一版已有确定性回放入口，以相同指令运行基线与新版；比较事件类型/tick、最终胜负、阳光、击杀数和割草机状态，保存到 docs/validation/006/replay.md。
6. 新素材完成后重新打包，再对最终打包版采样；模拟显示/合成输入结果只作为诊断，不作为规格通过证据。

## Project Structure

### Documentation (this feature)

    specs/006-first-version-visual-quality/
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    ├── contracts/packaged-validation-report.md
    └── tasks.md               # Created by $speckit-tasks

### Source Code (repository root)

    assets/
    ├── skins/default/source/             # 保留原背景并加入高清重绘主图
    ├── skins/default/manifest.json       # 将默认背景资源指向高清图
    ├── skins/dogs/source/                # 保留原始用户动作表及可重建卡通源帧
    ├── skins/dogs/manifest.json          # 卡通图集帧/锚点/来源引用
    ├── skins/dogs_photo/manifest.json    # 照片图集帧/锚点/来源引用
    └── sources.json                      # 背景和用户狗动作表来源/哈希
    tools/                                # 背景生成、动作表导入、预览、验证、基准和打包
    src/pvz_game/
    ├── app.py                            # 60Hz更新、显示等待、真实窗口采样/输入
    ├── config.py                         # 玩法 tick_hz 校验
    ├── presentation/
    │   ├── renderer.py                   # 背景合成和缓存
    │   ├── skin_catalog.py               # manifest/图集/帧边界和锚点校验
    │   ├── animation.py                  # 动作时序、显示缩放和帧缓存
    │   ├── performance.py                # 标准/压力场景及帧间统计
    │   └── dog_validation.py             # 狗狗主体尺寸与邻格遮挡
    └── domain/simulation.py              # 保持现有规则，作为回放对照基线
    tests/
    ├── unit/test_performance.py
    ├── integration/test_asset_manifest.py
    ├── integration/test_animation.py
    ├── integration/test_background_layout.py
    ├── integration/test_skin_selection.py
    ├── integration/test_playable_loop.py
    ├── replay/test_base_replay.py        # 第一版冻结事件快照与帧率无关回放
    └── replay/test_skin_invariance.py
    docs/validation/006/                  # 第一版/新版截图、性能、交互和回放结果

**Structure Decision**: 单一 Python 项目。素材制作归 tools/，分发资产与来源记录归 assets/，游戏实时渲染归 src/pvz_game/presentation/，玩法状态留在 domain/。复用 005 已有素材、测量和验证入口；docs/validation/006/ 保留本轮与基线配对证据。

## Validation Gates

- **素材入口**：下载候选页面/原始文件核验许可、作者、分辨率与哈希；最终静态背景≥2800×1200，能在三档窗口重建，无联网运行依赖。
- **背景构图**：三档同场景截图核对房屋/道路/草坪/种植区，网格命中与交互区域不变。
- **狗狗动作**：默认/卡通/照片素材 manifest 校验；必要动作时序、12–18 distinct poses/s、被窝素材和已有遮挡规则无回归；预览逐动作检查。
- **性能自动门槛**：标准渲染循环平均值≥58 FPS且≥第一版同条件基线的97%、P95≤18ms；压力 P95≤20ms；两场景连续两帧以上>33ms计数必须为0；输出完整样本和设备/场景元数据。
- **实机与玩法**：第一版与最终打包版同条件对比；至少20次真人操作反馈 P95≤100ms；同输入回放规则/动作/胜负一致；最终包启动、离线、暂停/恢复和重开回归。

## Complexity Tracking

无宪章例外：未增加项目、服务、持久化层或运行时依赖。
