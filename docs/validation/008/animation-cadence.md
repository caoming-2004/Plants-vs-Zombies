# 12 fps 动作与窗口观察

结果：通过。所有循环植物 clip 的不同姿态速率均为 12.00 姿态/秒；见下表。非循环动作沿用原有动作时长采样，玩法 tick 仍为 60 Hz。

| 外观 | 角色 | 循环动作 | 不同姿态 | 总tick | 姿态/秒 |
|---|---|---|---:|---:|---:|
| default | sunflower | idle | 54 | 270 | 12.00 |
| default | sunflower | produce | 54 | 270 | 12.00 |
| default | peashooter | idle | 39 | 195 | 12.00 |
| default | peashooter | attack | 39 | 195 | 12.00 |
| default | wallnut | idle | 24 | 120 | 12.00 |
| default | jalapeno | idle | 24 | 120 | 12.00 |
| dogs | sunflower | idle | 13 | 65 | 12.00 |
| dogs | peashooter | idle | 13 | 65 | 12.00 |
| dogs | wallnut | idle | 13 | 65 | 12.00 |
| dogs | jalapeno | plant | 13 | 65 | 12.00 |
| dogs | pangbaobao | idle | 13 | 65 | 12.00 |
| dogs | huanghuang | idle | 13 | 65 | 12.00 |
| dogs_photo | sunflower | idle | 13 | 65 | 12.00 |
| dogs_photo | peashooter | idle | 13 | 65 | 12.00 |
| dogs_photo | wallnut | idle | 13 | 65 | 12.00 |
| dogs_photo | jalapeno | plant | 13 | 65 | 12.00 |

实际显示窗口标准场景观察 10 秒（狗狗植物与敌方外观）：

- 10.007 秒，623 帧，平均 62.26 FPS；P95 帧间隔 16.03 ms。
- >33ms 帧 1 次，最长连续 1 帧；模拟更新仍为 60 Hz。
- 渲染阶段均值 2.55 ms、P95 3.71 ms；窗口缩放均值 2.45 ms。
- 观测中发现绘制路径逐帧对每个单位查询皮肤文件时间戳，已将外部文件变更检查节流为每秒一次；姿态和输入路径仍使用同一缓存资源。
- 自动化卡片输入、拖放、阳光/冷却规则检查 60 项通过；真实窗口 benchmark 用于帧时间观察，未进行人工鼠标延迟采样。

详细窗口样本见 [window-benchmark.json](window-benchmark.json)。
