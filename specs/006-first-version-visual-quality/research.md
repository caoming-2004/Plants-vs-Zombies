# Research: 第一版背景与角色画质、流畅度恢复

## Decision 1: 背景采用重绘与分层合成，而不是换一张完整背景

**Decision**: 保留第一版背景中的房屋、道路、视角和整体布局，将它作为构图母版；用项目生成的高细节重绘图输出至少 2800×1200 的静态主图，离线随包加载。已核验的网络素材仅作候选评估，不满足风格/构图时不下载、不打包。

**Rationale**: 当前窗口逻辑区域约为 1050×600，首版背景为 1400×600 的横向构图。搜索候选中没有同时带有首版房屋和道路布局、且画风一致的场景；直接替换会破坏用户要求的构图。按原图重绘可增加细节，同时避免把无关的网络场景拼接进来。静态化并缓存也能避免额外帧处理成本。

**Research sources**:

- [High res animated grass for fixed background (1920×1080) — OpenGameArt](https://opengameart.org/content/high-res-animated-grass-for-fixed-background-1920x1080)：页面标注 Puffolotti、CC0 与 1920×1080；素材为可组合的分层草地，作者指出草地需要前景或类似道路/平台的前层。适合作为草坪绘制参考，不是可直接替换的整张首版背景。
- [Grass — OpenGameArt](https://opengameart.org/content/grass-9)：页面列出 1024×1024、CC0 草地纹理。作为细节候选，因偏地面纹理，须检查与首版绘画风格是否协调。
- [Grassy Plains Background — OpenGameArt](https://opengameart.org/content/grassy-plains-background)：页面列出作者 Theoden 和 CC0，但页面未说明分辨率，也不含首版房屋/道路，因此只作为风格参考候选。
- [Ground Textures Free — OpenGameArt](https://opengameart.org/content/ground-textures-free)：页面列有多张无缝 1024×1024 CC0 地表纹理；绘制风格与游戏可能不一致，优先级低于分层草地图。

**Alternatives considered**:

- 原样保留 005 的 1915×821 背景：分辨率低于本方案建议的 2× 首版尺寸，且不是用户指定的第一版图像细节重绘结果。
- 直接采用 OpenGameArt 整张草地场景：没有首版房屋与道路布局，违反构图约束。
- 运行时加载网络图片或实时图层动画：离线不可控并增加渲染成本，不符合产品约束。

**Asset intake rule**: 下载/嵌入前在站点核实授权、作者、原始文件和文件尺寸；最终采用的具体文件、URL、作者、许可、尺寸、哈希及必要署名写入 assets/sources.json。只保存确认用于最终重绘的来源，未采用候选不进发行清单。

## Decision 2: 沿用动作表导入与皮肤架构，移除卡通低分辨率预缩放

**Decision**: 扩展 tools/import_dog_assets.py 的 cartoonize_frame()，直接从每只狗的原始 10×6 透明动作表帧制作 256×256 单元中的卡通动作，不再先压为 64×64 并放大。保留颜色归纳风格，但在高分辨率帧内处理轮廓与颜色，不改变照片分支。

**Rationale**: 当前导入器已有源帧记录、去杂点、帧锚点、动作片段、manifest 和来源/哈希生成逻辑；当前 64×64 降采样是可确认的卡通细节瓶颈。现有 Catalog、Animator、renderer 和遮挡校验可沿用，无新架构或依赖。

**Alternatives considered**:

- 仅把现有卡通图集平滑放大：无法恢复 64×64 步骤已丢失的脸部和毛色细节。
- 运行时高分辨率滤镜：每帧重复计算，增加帧率风险；应该在素材构建阶段完成。
- 重新设计一套选肤/动画模型：与当前 manifest、锚点、动作源记录重复。

**Source code evidence**: tools/import_dog_assets.py contains cartoonize_frame() with a 64×64 intermediate; assets/skins/dogs/manifest.json and assets/skins/dogs_photo/manifest.json hold clip/atlas data; src/pvz_game/presentation/skin_catalog.py, animation.py, renderer.py share frame/anchor/scale behavior; dog_validation.py measures minimum size and neighbor overlap.

## Decision 3: 保持固定步进，收紧真实窗口性能报告

**Decision**: 保持配置的 60Hz 玩法 tick 和第一版 60 FPS 节奏设定。复用 benchmark_window、SCENES、tools/benchmark.py --window 和 --input-latency，新增每轮 >33ms 慢帧总数和最长连续值。标准平均帧率至少58 FPS且不低于同条件第一版样本的97%；高于60的采样值如实记录，不单独判失败。对比 7305e3d 基线与最终发行包，并记录真人输入与确定性回放结果。

**Rationale**: 第一版 app.py 使用 clock.tick(60)，当前版本使用 clock.tick_busy_loop(60)；两者都以 60 FPS 显示为目标，固定玩法频率也为 60Hz。005最终包真实窗口采样约62.4 FPS/P95 16.0ms，说明采样值是渲染循环提交速率，不应被误作物理显示刷新计数而设置60的严格上限。新版至少保持58 FPS且与配对基线相差不超过3%，并满足帧间隔目标。报告必须以 display flip 窗口路径为准，并明确环境。

**Alternatives considered**:

- 提高规则 tick 或动画速度：与“回到第一版节奏”冲突。
- 仅使用 SDL dummy 或纯渲染快速基准：不能覆盖 Windows 显示呈现和实际输入反馈。
- 将循环平均帧率硬封顶为60：现有打包报告可测得约62.4FPS，硬封顶会让原本流畅的测量误失败；保留60FPS节奏设定，比较基线比值并以P95/慢帧判定卡顿。
- 单看平均 FPS 或 >50ms 连续帧：会隐藏 33–50ms 的可见长帧；增加 >33ms 统计。
- 用所有显示器统一 FPS 数字：用户已指定以当前电脑为目标；测试报告记录刷新率并把低刷新率等外部限制单独注明。

**Evidence**: 第一版和当前版本的主循环均使用60Hz显示节流及固定60Hz模拟；当前app.py已有真实窗口benchmark和真人input-latency采样入口。docs/validation/005/performance.md中最终打包版真实窗口样本标准/压力分别为62.42/62.40FPS，P95为16.02/16.03ms，但配对第一版基线、20次真人操作和固定回放对比证据缺失。

## Implementation Constraints Resolved

- Python 3.12 x64、pygame-ce 2.5、PyInstaller 6、pytest 8 已由项目元数据确认；使用现有依赖。
- 本地文件打包，无运行时联网或外部服务，无新增数据库/数据迁移。
- 用户提供的原始素材保留为源文件；卡通与照片派生图保留对来源帧的可追溯记录。
- 第一版基线缺少本轮规格所需的完整配对证据，因此从 7305e3d 重建并在同机同窗口同刷新率测量；只添加诊断采集，不改旧版玩法/渲染/帧等待行为。
