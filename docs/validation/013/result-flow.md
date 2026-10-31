# 013 第一关结算验证

日期：2026-10-31

## 结果

| 检查 | 结果 | 证据 |
|---|---|---|
| 20 次真实 day_01 胜利 → 记录 → day_02 | PASS | `pytest tests/integration/test_result_flow.py -q`（2 passed，约 53–67 秒） |
| 结算只保存一次、day_02 解锁 | PASS | 测试循环断言；进度 schema v2 |
| 下一关为全新状态 | PASS | 测试断言无植物/僵尸 |
| 结算页渲染 | PASS | [result.png](result.png)；测试中实际调用 `Renderer.draw` 结算画面 |
| 下一关/重玩/返回/退出按钮命中 | PASS | 测试点击返回 `next_level`/`Restart`/`ReturnToMenu` |
| 损坏 progress 可恢复 | PASS | 测试写入 `{broken` 后 `Progress.load` 回退且保留 day_01 |
| 可恢复错误提示 | PASS（代码路径） | `app.refresh_result`/`start_level` 捕获异常，写完整 traceback，显示提示并保留菜单/重试 |

## 说明

- 用户报告的“通关第一关之后报错”未提供异常文本；本机当前代码无法复现未处理异常。已用真实 day_01 胜利路径（replay 策略，非强制 `phase='won'`）连续 20 次验证，并补上结果/保存/下一关错误边界。
- 未在真实鼠标窗口中手动通关一次并点“下一关”；自动测试和 exe 冒烟已覆盖加载/菜单/结算渲染路径。该人工点击仍建议在 Windows 实机验收时补做。
