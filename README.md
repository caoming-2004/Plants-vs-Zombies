# 植物大战僵尸小游戏 · v0.2.0 换肤试玩

当前已实现默认角色帧与门头沟小狗外观。本次更新将阳光余额移到左上角，支持植物卡/铲子拖放，并接入用户提供的小宝、小杜60帧动作图。

## 运行

完整解压 `dist/PvzMiniGame-windows-x64.zip`，打开 `PvzMiniGame-v0.2.0`，双击 `PvzMiniGame.exe`。
保留 `_internal` 和所有资源。无需Python、管理员权限或联网下载。
版本化历史包 `dist/PvzMiniGame-v0.2.0-windows-x64.zip` 保留；执行最终构建时会更新通用发行包。

主菜单“选择外观”可分别为植物方和进攻方切换经典/小狗模式：
向日葵→被窝（金围巾），射手→黄黄（绿背心），坚果墙→小宝，火爆辣椒→小杜，进攻方→嗷嗷嗷（红背心）。
仅开局前切换，重开保留选择，关闭游戏后不保存。损坏小狗资源会提示并整套回退对应阵营。

玩法：左上角查看阳光余额，点击草坪金色阳光收集；点击或拖动四张植物卡种植；点击铲子再点植物，或直接将铲子拖到植物上移除（不退款）；右键/Esc取消拖动或选择；空格暂停/继续。坚果墙阻挡僵尸，火爆辣椒清除本行现存僵尸。
每行割草机可救场一次，之后再次突破该行则失败；清除12只僵尸获胜，可重开。
战斗画布为1050×600逻辑像素，完整显示五行十二列；窗口最小客户区1050×600。

## 开发与验证

```powershell
.venv/Scripts/python.exe -m pvz_game
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe tools/validate_assets.py
.venv/Scripts/python.exe tools/preview_animations.py
.venv/Scripts/python.exe tools/benchmark.py
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
.venv/Scripts/python.exe tools/verify_bundle.py
```

`tools/benchmark.py` 默认测量60秒压力场景；SDL dummy数据不能替代Windows实机性能与发行验收。拖放P95需在真实窗口执行`.venv/Scripts/python.exe tools/benchmark.py --input-latency --seconds 60`，并在测量期间实际拖动。

动画预览按空格换外观，Esc退出；`--export docs/validation/animations` 导出动作条带。
逐帧图集、原始生成图、来源清单都随包保留，运行不读取网络。

原版布局/节奏的严格一致性与小狗最终造型审核仍未通过全部验收，不将功能可用或测试通过等同这些要求已完成。Windows实机、持续运行与新手试玩尚未全部执行。
详见 [默认视觉记录](docs/validation/default-visuals.md)、[小狗验证记录](docs/validation/dog-visuals.md)、
[角色映射](docs/art/dog-mapping.md) 与 [生成提示词](docs/art/generation-prompts.md)。

实现、测试证据与未完成验收汇总见[本次功能发布验收报告](docs/validation/release-report-002.md)。

开发环境见 [开发说明](docs/development.md)。
