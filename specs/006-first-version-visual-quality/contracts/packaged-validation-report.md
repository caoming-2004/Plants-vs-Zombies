# 打包实机验收报告契约

此为项目内部诊断 CLI 的稳定验证输出约定，不是对外网络 API。数据写入 docs/validation/006/ 并可从命令行输出 JSON。

## Performance report

入口：

~~~powershell
dist/PvzMiniGame-visual-quality/PvzMiniGame.exe --benchmark-scene standard --seconds 60 --baseline-average-fps 62.42 --benchmark-output docs/validation/006/packaged-standard.json
dist/PvzMiniGame-visual-quality/PvzMiniGame.exe --benchmark-scene pressure --seconds 60 --benchmark-output docs/validation/006/packaged-pressure.json
~~~

标准场景的 baseline-average-fps 参数必须替换为 docs/validation/006/baseline-standard.json 中第一版同条件平均循环帧率；示例数值仅说明参数位置。

必需字段：

- scene、load、machine、os、display_driver、refresh_rate_hz、window_size、measured_at
- frames、elapsed_seconds、average_fps、p95_frame_ms、frame_intervals_ms
- baseline_average_fps、average_fps_vs_baseline_pct
- over_33ms_frames、longest_over_33ms_run、acceptance.status
- acceptance 所用阈值与失败原因；不得只返回 PASS/FAIL 而不返回实际测量值

average_fps 是渲染循环采样率，不是物理显示器刷新计数，不将值截断到60。通过条件：standard 平均≥58 FPS且不低于同条件第一版基线的97%、P95≤18ms；pressure P95≤20ms；两场景 longest_over_33ms_run < 2。baseline-average-fps 从第一版 standard 报告读取；缺失基线时 status 必须为 INCONCLUSIVE，不能自动 PASS。报告同时列出显示器刷新率和渲染循环采样率；显示器刷新率低于60Hz时注明外部限制。

## Human input feedback report

入口：

~~~powershell
dist/PvzMiniGame-visual-quality/PvzMiniGame.exe --input-latency --seconds 60
~~~

测量期间，测试者在可见打包窗口内完成至少20次有效的植物拖放、铲除和阳光收集。每条样本必须关联实际游戏接受事件与后续显示交换时间，不能用合成鼠标事件代替。必需结果包括有效样本数、操作种类计数、延迟P95、漏操作、重复操作、窗口、刷新率、设备和时间；通过标准为有效操作数≥20、漏/重复均为0且P95≤100ms。

## Visual evidence

- background-1050.png、background-1260.png、background-1920.png：同一关卡状态和同一构图。
- dogs-actions.png 与按皮肤/角色/动作命名的姿势条：覆盖照片和卡通分支、必要动作及三档目标尺寸。
- 报告附人工核对记录：布局、清晰度/边缘、身份、裁切、网格输入命中、遮挡率、外部素材许可/哈希。

## Deterministic replay comparison

用相同输入分别运行第一版和最终版，保存事件类型/tick与最终胜负、阳光、击杀数、割草机状态的对照及差异到 docs/validation/006/replay.md。结果完全一致时 differences 为空；不得只记录“通过”而省略对照字段。冻结基准或任一版本回放不可用时，status 必须为 INCONCLUSIVE，不能自动 PASS。
