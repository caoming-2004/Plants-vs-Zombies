# 植物拖放与铲子拖放验收（003）

自动化：植物目标预览按当前快照检查阳光、冷却和占格；铲子目标预览检查释放格是否仍有植物。拖动释放在app路由中重新校验；有效释放提交既有`SelectPlant`+`PlantAt`或`SelectShovel`+`ShovelAt`命令，无效/取消不提交。旧点击路径保留。定向自动回归已通过，详见`feature-003-regression.md`。

| 验收项 | 结果 |
|---|---|
| 植物点击/拖放自动命令结果等价 | PASS |
| 植物拖放无效释放防误种/扣费 | PASS |
| 铲子有效/空格释放自动路径 | PASS |
| 真实Windows植物拖动≥20次 | NOT_RUN |
| 真实Windows铲子拖动≥20次 | NOT_RUN |
| 真实鼠标输入P95≥200样本 | NOT_RUN（实现`tools/benchmark.py --input-latency --seconds 60`测量入口；需要试玩时持续实际拖动） |

自动测试不冒充实际桌面输入样本。窗口验收会在当前可用的真实应用窗口中补做并更新本记录。
