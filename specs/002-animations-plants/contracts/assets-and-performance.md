# Asset and Performance Contract

## 角色清单

| Role ID | 默认角色 | 狗狗角色 | Required clips |
|---|---|---|---|
| sunflower | 向日葵 | 被窝 | idle, produce, hit, die |
| peashooter | 豌豆射手 | 黄黄 | idle, attack, hit, die |
| wallnut | 坚果墙 | 小宝 | idle, hit, die |
| jalapeno | 火爆辣椒 | 小杜 | plant/ignite, hit (若场景允许受击), die/effect-end |
| zombie_basic | 普通僵尸 | 嗷嗷嗷（红背心） | walk, bite, hit, die |

一次性火爆辣椒的plant/ignite以事件row_clear_started启动，不能回调Simulate造成伤害。类别不适用的clip需在manifest明确标注，而不是缺失后静默取别的角色帧。

## Manifest / 帧条件

- default和dogs完整角色/卡片/预览均可在资源校验中解析；dogs缺任一必要资源时整套植物或敌方阵营回退default并显示中文提示。
- 所有manifest frame持有atlas rect、source_size、trim_offset、anchor、muzzle、contact和duration_ticks；坐标均使用源像素，manifest pixel_scale=2。
- 逐帧矩形必须在atlas边界内；trim及逻辑锚点复原后脚底基线稳定，发射/接触位置与相应玩法事件一致。
- 每个关键动作clip的规范化不同可见姿态数 / 持续秒数 ≥24；循环动作总时长≥60 tick。复制相同姿态、仅改duration、整图透明闪烁不可作为新增姿态。
- dog角色保持既有最小身高75%及相邻列轮廓不重叠要求。新角色加入完整的相邻角色配对检查。
- 所有艺术品记录来源、版本、动作表和适用许可；生成素材保存源sheet和prompt，最终裁剪/导入工具可重复运行。

## 显示与性能

- 玩法逻辑坐标固定1050×600；window及目标surface尺寸按实际窗口像素比例适配，输入逆变换回逻辑坐标。
- 不在每帧重复读取源PNG或执行未缓存的缩放；透明素材加载后转成alpha blit友好surface，按有限的显示比例缓存缩放版本。
- 标准Windows 60Hz显示设备：常规60秒画面平均≥58 FPS，95百分位帧间隔≤25 ms；画面/动画采样时钟≥60次/秒；动作clip素材姿态率≥24/s。
- SC-007固定压力场景为1050×600、45植物/30僵尸/100投射物/20阳光，连续60秒平均≥55 FPS、P95≤33 ms；输入事件到首个可见预览P95≤50 ms，20次操作无丢失/重复。记录环境与呈现驱动；SDL dummy仅作自动化/诊断，不替代Windows实机验收。
- 1050×600、1260×720与1920×1080窗口及四种外观组合逐项留证：非预期帧裁切为0、循环首尾锚点偏差≤2逻辑像素、卡片/HUD/交互区域互相遮挡为0、无闪烁或透明边缘异常。每项记录PASS/FAIL/NOT_RUN并附截图。

## 回归不变性

固定配置及同一命令序列在default/default、dogs/default、default/dogs、dogs/dogs四种组合运行。对比规则快照（忽略skin/render字段）、事件种类/目标/顺序/tick、阳光、扣费、击杀与胜负；须完全相同。Presentation帧数不允许增删模拟命令或修改event tick。
