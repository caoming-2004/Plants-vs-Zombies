# 植物大战僵尸小游戏 · v0.7.1

离线草坪防守游戏，提供经典、狗狗卡通和狗狗照片植物外观，以及日间/夜间/黄昏三套高清真实感草坪背景。支持 5 关战役、关卡选择、星级挑战、通关后的无尽模式、本机进度保存、鼠标连续拖放、暂停、重开和 60Hz 固定逻辑模拟；狗狗动作在约 12 个源姿态/秒的基础上叠加 60Hz 程序化次级动作。

## 运行

从 `dist/windows/PvzMiniGame-v0.7.1/` 启动 `PvzMiniGame.exe`；保留同目录 `_internal`、游戏说明和字体许可。无需 Python、管理员权限或联网下载。

主菜单“选择外观”可为植物方选择经典、狗狗卡通或狗狗照片；进攻方可选择经典或狗狗卡通。主菜单“更换背景”可切换日间/夜间/黄昏三套高清背景，选择立即生效并保存到本机 progress.json；外观选择仍只在本次运行内有效。
狗狗植物映射为向日葵→被窝（金围巾）、豌豆射手→好孩子、坚果墙→小宝、火爆辣椒→小杜；
狗狗外观另外提供胖宝宝倭瓜和黄黄寒冰射手，独立于其他植物卡片。
照片版被窝和僵尸嗷嗷嗷复用原卡通素材。角色和来源详情见[角色映射](docs/art/dog-mapping.md)及素材清单 `assets/sources.json`。
仅开局前切换，重开保留选择，关闭游戏后不保存。损坏小狗资源会提示并整套回退对应阵营。

玩法：主菜单“开始游戏”进入关卡选择；第 1 关默认解锁，通关后依次解锁第 2～5 关并自动保存到 `%LOCALAPPDATA%\PvzMiniGame\progress.json`。波次、出怪进度和下一波预告显示在顶部 HUD 单行状态条，不覆盖草坪。背景选择也保存在同一文件的独立 settings 字段，旧存档自动迁移。每关有不同波次和压力条件，结算显示星级；通关第 5 关后解锁无尽模式，敌人会持续增强直到防线突破。
战斗中：左上角查看阳光余额，点击草坪金色阳光收集；点击或拖动植物卡种植；点击铲子再点植物，或直接将铲子拖到植物上移除（不退款）；右键/Esc取消拖动或选择；空格暂停/继续。坚果墙阻挡僵尸，胖宝宝倭瓜会对近距离目标蓄势重击一次，黄黄继续担任寒冰射手，火爆辣椒清除本行现存僵尸。
每行割草机可救场一次，之后再次突破该行则失败；每个战役关卡至少包含三个波次和最终波，通关后解锁下一关。
战斗画布为1050×600逻辑像素，完整显示五行十二列；窗口最小客户区1050×600。

## 开发与验证

```powershell
.venv/Scripts/python.exe -m pvz_game
.venv/Scripts/python.exe tools/validate_assets.py
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/windows/build.ps1
.venv/Scripts/python.exe packaging/windows/verify_bundle.py
```

构建脚本只校验资源并生成 Windows 目录包，不生成 ZIP，也不自动运行全量测试。日常反馈和 Windows 包验收使用与改动直接相关的定向检查。
在真实窗口测固定负载可用 `.venv/Scripts/python.exe tools/benchmark.py --window --scene standard --seconds 60`；
将植物外观设为 `dogs_photo` 可测照片版资源。阶段帧间隔和设备信息写入 `--output` 指定的 JSON。

动画预览按空格换外观，Esc退出；`--export docs/validation/animations` 导出动作条带。
逐帧图集、原始生成图、来源清单都随包保留，运行不读取网络。

高清背景构建器为 `tools/generate_backgrounds.py`，以 Wikimedia Commons 的授权真实照片（Mona lawn，作者 Wiki ian，CC BY-SA 3.0）为基础做裁切和光照分级；照片/卡通皮肤构建器为 `tools/import_dog_assets.py`。
两者都只使用仓库本地素材，不在运行时联网。背景来源、作者、授权和 SHA-256 记录在 `assets/backgrounds/source/provenance.json` 与 manifest 中。Windows 实机性能、真实交互反馈、构建发行和人工视觉验收仍须按
[005 背景验收](docs/validation/005/background.md)、[狗狗素材验收](docs/validation/005/dogs.md)及
[性能验收](docs/validation/005/performance.md)记录，不能将自动测试视为这些实机项目已通过。
详见 [默认视觉记录](docs/validation/default-visuals.md)、[小狗验证记录](docs/validation/dog-visuals.md)、
[角色映射](docs/art/dog-mapping.md) 与 [生成提示词](docs/art/generation-prompts.md)。

实现、测试证据与未完成验收汇总见[本次功能发布验收报告](docs/validation/release-report-002.md)。

开发环境见 [开发说明](docs/development.md)。
