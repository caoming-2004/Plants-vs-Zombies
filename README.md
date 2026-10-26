# 植物大战僵尸小游戏 · v0.2.0

离线草坪防守游戏，提供经典素材、狗狗卡通和狗狗照片三种植物外观。支持鼠标拖放、暂停、重开和 60Hz 固定逻辑模拟。

## 运行

完整解压 `dist/PvzMiniGame-windows-x64.zip`，打开 `PvzMiniGame-v0.2.0`，双击 `PvzMiniGame.exe`。
保留 `_internal` 和所有资源。无需Python、管理员权限或联网下载。
版本化历史包 `dist/PvzMiniGame-v0.2.0-windows-x64.zip` 保留；执行最终构建时会更新通用发行包。

主菜单“选择外观”可为植物方选择经典、狗狗卡通或狗狗照片；进攻方可选择经典或狗狗卡通。
狗狗植物映射为向日葵→被窝（金围巾）、豌豆射手→好孩子、坚果墙→小宝、火爆辣椒→小杜；
照片版被窝和僵尸嗷嗷嗷复用原卡通素材。角色和来源详情见[角色映射](docs/art/dog-mapping.md)及素材清单 `assets/sources.json`。
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
在真实窗口测固定负载可用 `.venv/Scripts/python.exe tools/benchmark.py --window --scene standard --seconds 60`；
将植物外观设为 `dogs_photo` 可测照片版资源。阶段帧间隔和设备信息写入 `--output` 指定的 JSON。

动画预览按空格换外观，Esc退出；`--export docs/validation/animations` 导出动作条带。
逐帧图集、原始生成图、来源清单都随包保留，运行不读取网络。

高清背景与照片/卡通皮肤的本地生成器分别为 `tools/generate_background.py` 和 `tools/import_dog_assets.py`；
两者都只使用仓库本地素材，不在运行时联网。Windows 实机性能、真实交互反馈、构建发行和人工视觉验收仍须按
[005 背景验收](docs/validation/005/background.md)、[狗狗素材验收](docs/validation/005/dogs.md)及
[性能验收](docs/validation/005/performance.md)记录，不能将自动测试视为这些实机项目已通过。
详见 [默认视觉记录](docs/validation/default-visuals.md)、[小狗验证记录](docs/validation/dog-visuals.md)、
[角色映射](docs/art/dog-mapping.md) 与 [生成提示词](docs/art/generation-prompts.md)。

实现、测试证据与未完成验收汇总见[本次功能发布验收报告](docs/validation/release-report-002.md)。

开发环境见 [开发说明](docs/development.md)。
