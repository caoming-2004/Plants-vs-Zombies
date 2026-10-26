# Quickstart: 动画与角色显示验收

本指南面向实现与验收者。普通玩家仍从完整发行目录双击exe运行。

## Prerequisites

- Windows x64开发环境，Python 3.12项目环境位于.venv。
- 从项目根目录运行命令。
- 成功验收不得依赖网络或未随包素材。

## Automated checks

    .venv/Scripts/python.exe -m pytest -q
    .venv/Scripts/python.exe tools/validate_assets.py
    .venv/Scripts/python.exe tools/preview_animations.py --export docs/validation/animations/004-preview
    .venv/Scripts/python.exe tools/benchmark.py --seconds 60

Expected:

- pytest通过现有领域、输入、皮肤回放和本Feature动画集成检查。
- 素材验证器报告default/dogs全部必需clip在12–18姿势/s；小杜清行clip完整呈现35个源姿势并约120 tick结束；角色边界和锚点检查无错误。
- 自动姿势数以RGBA逐像素去重计算；同时检查导出接触表，排除只因非动作像素差异而被计为不同姿势的帧。
- 逐动作预览可核验帧序、底线和狗狗完整身体；可导出的验证图位于给定目录。
- 基准记录simulation 60Hz、目标绘制60FPS与最坏场景呈现时延，确认无明显退化。

## Repeatable runtime scenarios

1. **姿势节奏**: 在default与dogs两种外观逐一观察idle/walk、produce/attack/bite、hit、die及jalapeno plant/ignite；自动按RGBA唯一姿势数×balance.json.tick_hz/clip总tick验收12–18/s，并人工核验接触表。规则攻击间隔/僵尸推进仍按改动前回放基准一致。
2. **暂停/继续**: 在循环动作、受击动作和小杜爆炸中分别暂停至少一秒再继续；暂停阶段帧不变，恢复后继续原动作，不重播或跳到新动作。
3. **小杜清行**: 同行放入多个僵尸后种下小杜，计时清行表现从出现到消退，结果1.9–2.1秒。清行规则只触发一次，对局没有等待动画结束才继续。
4. **小宝与小杜尺寸**: 查看卡片、外观预览、草坪姿势及拖动预览；对所有必需帧确认全身完整，草坪可见高度较当前基线至少+15%，脚底逻辑位置偏差不超过2像素。覆盖相邻行/格和1050×600、1260×720、1920×1080逻辑画布/窗口场景。当前dogs manifest对小宝/小杜设置1.2倍角色倍率。
5. **核心循环与重开**: 开始对局、获取/花费阳光、种植、阻挡/攻击、结束胜负并重开。检查旧受击、死亡、清行效果不进入新session；default与dogs同输入结果一致。

## Packaging regression

    powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
    .venv/Scripts/python.exe tools/verify_bundle.py
    .venv/Scripts/python.exe -m pvz_game --smoke-frames 60 --screenshot docs/validation/animations/004-menu.png
    .venv/Scripts/python.exe -m pvz_game --smoke-frames 60 --smoke-play --plant-skin dogs --zombie-skin dogs --screenshot docs/validation/animations/004-play.png

Expected: build and bundle verification succeed; both menu and playable dog-skin smoke launches complete with included assets. Record any host-specific rendering/benchmark limitation rather than claiming it passed.
