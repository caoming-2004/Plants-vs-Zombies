# 012 发布与最小验收汇总

**日期**: 2026-10-31  
**版本**: v0.7.0  
**范围**: Windows 桌面版（安卓不在本轮范围）

## 实际完成

- 被窝/嗷嗷嗷从原始图片按完整连通轮廓重新提取，重建 dogs/dogs_photo 图集、清单和来源记录；脚掌/腿/尾巴不再被等分格线切掉。
- 5 关战役、关卡选择、逐关解锁、本机进度保存、星级目标和无尽模式已接入。
- 狗狗 60Hz 程序化次级动作、阳光呼吸光晕、子弹尾迹/枪口闪光/命中特效已接入；模拟仍按 60Hz 且规则未改。
- Windows 目录包已构建并启动冒烟：
  - `dist/windows/PvzMiniGame-v0.7.0/PvzMiniGame.exe`
  - 包内 `_internal/pvz_game/assets/levels/` 含 campaign.json 与 day_01～day_05。
  - 冒烟截图 `docs/validation/012/bundle-smoke.png`。

## 最小验证结果

| 检查 | 结果 |
|---|---|
| `tools/validate_assets.py` | PASS：campaign 5 关、default/dogs/dogs_photo 均 valid |
| 狗狗边界/完整轮廓 | PASS：`tests/integration/test_animation.py` 17 passed（含新增比例检查） |
| 战役配置/进度/无尽/流程 | PASS：15 passed |
| 可玩循环/拖放 | PASS：24 passed（排除依赖 tmp_path 的资源路径用例） |
| 皮肤不变性 | PASS：3 passed |
| 标准场景基准（dummy 10s） | PASS：平均 62.06 fps，p95 16.01 ms |
| Windows 包启动 | PASS：exit code 0，截图已生成 |

## 已知问题/未完成

1. `tests/replay/test_base_replay.py::test_feature_replay_matches_pre_change_gameplay_baseline` 仍失败：现有 004 基线早于工作区中的 011 波次/阳光事件改动，事件顺序与基线不一致；本次未重写 004 基线，避免掩盖既有变化。
2. 依赖 pytest `tmp_path` 的部分既有用例在当前沙箱的 `.tools/pytest-temp` 上因目录权限无法清理而报 ERROR；新增 012 测试已改用工作区临时文件，测试本身通过。
3. 未完成 10 秒逐帧录屏核对和真实窗口 60 秒标准基准；当前只有 dummy 10 秒基准与截图。
4. 5 关通关证据来自脚本化试玩（全部 won，12/15/18/21/24 击杀），尚缺人工逐关手感验收；无尽仅做 4 个定向测试和 600+ tick 脚本推进，未做真实窗口 10 波手动失败。
5. 安卓安装、触控和性能验收未执行（按已确认范围排除）。

## 产物

- [plan.md](../plan.md)
- [research.md](../research.md)
- [data-model.md](../data-model.md)
- [quickstart.md](../quickstart.md)
- [狗狗帧验收](dog-frames.md)
- [战役验收](campaign.md)
- [星级验收](stars.md)
- [无尽验收](endless.md)
- [流畅表现](smoothness.md)
