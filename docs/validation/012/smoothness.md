# 012 流畅表现验收

**结果：部分通过（基准/截图；帧级观察待补）**

- 狗狗动作：在约 12 个源姿态/秒之上增加确定性 60Hz 次级动作（行走起伏、呼吸、受击回弹），不改变模拟 tick；没有使用 alpha 整帧交叉淡化。
- 阳光：增加呼吸光晕；收集仍由现有 collected 事件驱动。
- 子弹：增加最多 3 点尾迹、枪口闪光和投射物消失位置的命中特效；不新增模拟事件，不修改快照。
- 标准场景基准（dummy 显示，10 秒）：平均 **62.06 fps**，p95 **16.01 ms**，最长 >33ms 单帧 1 次，最长 >50ms 连续帧 0；输出 `docs/validation/012/benchmark.json`。
- 狗狗外观 smoke 截图 `play-smoke.png`，确认完整角色与 HUD/预告显示。
- 现有 `tests/integration/test_animation.py` 17 passed；`tests/replay/test_skin_invariance.py` 3 passed；`test_playable_loop.py` + `test_drag_input.py` 24 passed（排除依赖 tmp_path 的环境用例）。

**未完成/限制**：没有完成 10 秒逐帧录屏核对“无重影/每帧变化”；没有在真实窗口测得 60 秒标准基准。以上两项需在 Windows 实机补做。
