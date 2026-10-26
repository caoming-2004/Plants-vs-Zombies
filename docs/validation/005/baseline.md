# 005 改动前画面和规则基线

日期：2026-10-26；分支：`version1`。截图采样时尚未替换背景或狗狗素材；仅增加性能采样入口和可选窗口尺寸，游戏规则未改。

## 画面

同一固定 smoke 对局、`default` 背景与 `dogs` 植物/僵尸外观，8 帧后保存窗口内容：

| 窗口 | 截图 |
|---|---|
| 1050×600 | [baseline-1050.png](baseline-1050.png) |
| 1260×720 | [baseline-1260.png](baseline-1260.png) |
| 1920×1080 | [baseline-1920.png](baseline-1920.png) |

截图命令：`SDL_VIDEODRIVER=dummy .venv/Scripts/python.exe -m pvz_game --smoke-frames 8 --smoke-play --plant-skin dogs --zombie-skin dogs --window-size WIDTHxHEIGHT --screenshot docs/validation/005/baseline-WIDTH.png`。此处 dummy 仅用于稳定截图，不作为帧率证据。

逻辑画布1050×600；草坪网格原点(105,160)，12列×5行，每格72×76。新背景必须保持这些坐标和输入命中关系。

## 规则回放

`.venv/Scripts/python.exe -m pytest -q tests/replay/test_base_replay.py tests/replay/test_skin_invariance.py`：6 passed in 72.19s。现有 `default`/`dogs` 固定输入的事件和结局一致；`tests/replay/fixtures/004-baseline.json` 的旧基准在当前代码仍通过。

## 真实窗口性能

待 T004：用仅增加采样入口、尚未替换背景/狗狗素材的打包版，在用户当前电脑的真实显示窗口对标准/压力场景各测60秒，记录构建标识、驱动、窗口、帧间隔、平均FPS、P95及连续慢帧。不得填入 SDL dummy 诊断数据。
