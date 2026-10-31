# 006 打包版性能验收

## 环境与口径

当前 Windows 11 x64 电脑，Pygame SDL `windows` 显示驱动，1600×1000 桌面、90Hz 刷新率；目标窗口1260×720。诊断发行目录中的 exe 实测，每场景60秒，使用 dogs plant/zombie 皮肤；固定场景负载见原始 JSON。FPS 是窗口呈现帧率，玩法模拟仍以60Hz固定步进。

## 首版与新包对照

| 版本/场景 | 平均FPS | P95帧间隔 | >33ms帧数 | 最长连续>33ms | 结果 |
|---|---:|---:|---:|---:|---|
| 7305e3d 首版 standard | 60.35 | 17.48ms | 1 | 1 | 基线 |
| 新诊断包 standard | 62.30 | 16.01ms | 4 | 1 | PASS |
| 7305e3d 首版 pressure | 59.99 | 17.54ms | 3 | 2 | 基线 |
| 新诊断包 pressure | 62.42 | 16.01ms | 1 | 1 | PASS |

standard 新包达到首版的 103.23%，超过58FPS、基线97%和P95≤18ms门槛。pressure P95≤20ms。两场景均无两帧连续>33ms。新样本中孤立慢帧数包括操作系统偶发调度，不形成持续卡顿。

- [首版 standard](baseline-standard.json) / [首版 pressure](baseline-pressure.json)
- [新版 standard完整样本](packaged-standard.json) / [新版 pressure完整样本](packaged-pressure.json)

## 真人交互输入延迟

状态：待在可见打包窗口完成至少20次有效种植、铲除和阳光收集。指标要求 action-to-visible-flip P95≤100ms，漏操作/重复事件均为0。结果与样本详情待补充。
