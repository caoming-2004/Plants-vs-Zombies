# 013 发布验收记录

日期：2026-10-31  
版本：**v0.7.1**  
分支：`013-wave-hud-error-backgrounds`

## 交付

| 项目 | 结果 |
|---|---|
| 任务清单 | **28/28** 已勾选；T013/T023/T028 的实机/抓包边界见文末 |
| 顶部 HUD 单行状态条（关卡/波次/出怪/下一波） | 完成；不再覆盖草坪 |
| 第一关真实胜利 20 次 + 结算页/下一关/重试/菜单 | 完成；0 未处理异常 |
| 三套 2560×1440 真实感高清背景 | 完成；日间/夜间/黄昏 |
| 主菜单更换背景、立即应用、本机保存、旧存档迁移 | 完成 |
| Windows 包 | `dist/windows/PvzMiniGame-v0.7.1/` |

## 验证证据

- HUD 几何/预告一致性：`pytest tests/integration/test_hud_layout.py -q` → **2 passed**
- 第一关真实胜利流程：`pytest tests/integration/test_result_flow.py -q` → **2 passed**（约 53–67 秒）
- 背景清单/迁移/回退：`pytest tests/unit/test_backgrounds.py -q` → **4 passed**
- 战役/进度/无尽回归：**15 passed**
- 定向合计：**55 passed**；`test_playable_loop.py::test_resources_independent_of_cwd` 在 teardown 阶段因 `.tools/pytest-temp` 的 Windows `PermissionError` 报 1 个 error，**不是功能失败**，与既有临时目录权限问题一致。
- 资源校验：`tools/validate_assets.py` → campaign/backgrounds/3 套皮肤全部 valid。
- 性能：`tools/benchmark.py --window --scene standard --seconds 10` → **61.4 fps，p95 16.01 ms**（SDL dummy；无历史基线，状态 INCONCLUSIVE）。
- Windows 包冒烟：`PvzMiniGame.exe --smoke-play ...` → exit 0；`_internal/pvz_game/assets/backgrounds/` 含 manifest、三套 PNG、缩略图和来源记录。

截图：

- [顶部 HUD 1050×600](hud-1050.png)
- [顶部 HUD 1920×1080](hud-1920.png)
- [背景选择页](backgrounds.png)
- [真实结算页](result.png)
- [打包后游戏画面](exe-play.png)
- [打包后菜单](exe-smoke.png)

## 背景素材

- 原始照片：Wikimedia Commons “Mona-lawn-dusk-Panorama1.jpg”
- 作者：**Wiki ian**
- 授权：**CC BY-SA 3.0**（必须署名）
- 派生：裁切 16:9 + 日间/黄昏/夜间色彩分级
- 记录：`assets/backgrounds/source/provenance.json`、`manifest.json`
- 风格：真实感建筑/草坪摄影，非幼稚卡通。

## 已知限制 / 未执行

1. 用户报告的第一关报错没有提供具体异常文本；当前代码未能复现未处理异常。已用真实 replay 胜利路径 20 次 + 结果/保存/下一关错误边界覆盖，但不能证明已定位用户原始环境中的具体根因。
2. 未在真实鼠标窗口中手动完成一次“第一关→下一关”并点击所有结算按钮；自动测试和 exe 冒烟覆盖了逻辑/渲染路径，建议在 Windows 实机补做一次人工点击。
3. 未用真实鼠标逐一切换三套背景并重启 exe；自动测试覆盖清单/迁移/回退，截图覆盖选择页和游戏内画面。
4. 性能为 dummy 10 秒快速验证，不是真实显示驱动 60 秒基线。
5. 未抓包验证 0 网络请求；运行时路径只读本地 manifest/PNG，无网络代码。
6. 背景按 1050×600 画布缓存，1920×1080 窗口由现有游戏画布等比放大；源图 2560×1440 且未见像素块，但整体清晰度仍受画布放大影响，未做 1920 原生重绘。
7. 未跑全量 pytest、外观矩阵、长时压力或安卓；按规格本轮不需要。
