# 004 动画预览与性能基准

运行环境：Windows 11 x64、Python 3.12.15、pygame-ce 2.5.8；日期 2026-10-26。

- 动作预览导出命令：`.venv/Scripts/python.exe tools/preview_animations.py --export docs/validation/animations/004-preview --frames 1`（退出码 0）。该目录包含 default/dogs 各必需动作按序的全帧 strips 及角色总览图。
- 压力场景：1050×600，45 plants、30 zombies、100 projectiles、20 suns；SDL dummy；8 秒。
- 结果：480 frames；平均 59.98 FPS；P95 frame 17.54 ms；动画采样 59.6/s；simulation 60Hz；cold startup 1.855 s。
- 达成既有基准门槛：平均 FPS ≥55、P95 ≤33 ms、启动 <10s。
- 性能命令：`.venv/Scripts/python.exe tools/benchmark.py --seconds 8`（退出码 0）。基准脚本压力场景耐久值读取已修正：使用配置 HP，缺失 HP 时采用显示基准默认值，不改变游戏 Simulation 规则。
- SDL dummy 结果用于可重复软件渲染比较；不等价于真实显示器输入延迟或不同硬件上的帧率保证。

## 核心动作预览

![default 全部动作](004-preview/default-actions.png)

![dogs 全部动作](004-preview/dogs-actions.png)
