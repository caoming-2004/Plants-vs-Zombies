# 开发与构建（US1）

玩家无需本节工具，完整解压试玩包后双击exe即可。

已验证环境：Windows x64，Python3.12.15，pygame-ce2.5.8；全部精确依赖见requirements.lock.txt。
使用独立.venv，不修改系统解释器，不混装pygame和pygame-ce。

```powershell
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.lock.txt
uv pip install --python .venv/Scripts/python.exe --no-deps -e .
.venv/Scripts/python.exe -m pvz_game
.venv/Scripts/python.exe -m pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/windows/build.ps1 -Diagnostic
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/windows/build.ps1
```

沙箱环境可以将UV_CACHE_DIR和UV_PYTHON_INSTALL_DIR设为项目.tools/内目录。
锁定文件不包含本项目的本机editable绝对路径；项目本身单独安装。
测试临时目录在.tools/pytest-temp，避免依赖不可写的系统临时目录。

默认构建仅用于US1原型，使用代码绘制美术与随包Noto中文字体。
US2图集、原版对照和US3小狗外观没有在本阶段实现，不能将本构建当作完整首版。

逻辑层不导入pygame。Simulation是GameSession的权威容器，快照递归冻结；GridCell占用由
存活Plant的唯一(row,col)派生，避免维护第二份易失同步的格子映射。
模拟动作与计时、阳光到期和投射物顺序遵循specs/001-pvz-mini-game/contracts/simulation.md。

真实窗口冒烟检查：

```powershell
.venv/Scripts/python.exe -m pvz_game --smoke-frames 60 --screenshot docs/validation/menu.png
.venv/Scripts/python.exe -m pvz_game --smoke-frames 60 --smoke-play --screenshot docs/validation/play.png
```

smoke-play仅为开发验证创建展示局，普通启动没有调试资源或额外阳光。

## v0.2.0 后续阶段

当前默认入口使用经过校验的经典图集与小狗皮肤清单；旧prototype_renderer只保留公共文字/按钮基础与US1参考，不再用于角色或场景绘制。
新增skin_catalog.py、animation.py，以及独立于模拟的AppearanceController；所有选择只改变展示层。
模拟层仅增加source动作事件，未更改平衡配置、碰撞或伤害周期。

素材开发工具：

```powershell
.venv/Scripts/python.exe tools/import_classic_assets.py
.venv/Scripts/python.exe tools/import_dog_assets.py
.venv/Scripts/python.exe tools/generate_backgrounds.py
.venv/Scripts/python.exe tools/validate_assets.py
.venv/Scripts/python.exe tools/preview_animations.py --export docs/validation/animations
.venv/Scripts/python.exe tools/benchmark.py
```

classic导入器需要.tools/references/中已下载并记录提交的原始参考，运行时与打包不依赖该目录。
AI源图位于assets/skins/dogs/source，最终提示词与用户确认见docs/art。
运行时只读取assets/skins/default与dogs，不需要AI工具或网络。

当前 Windows 构建输出为 `dist/windows/<版本目录>/`，中间文件位于 `build/windows/`，不会生成 ZIP。构建使用 `packaging/windows/` 中专属 spec、启动器和发行辅助文件；Android 文件在各自的 Android 目录。

`tools/benchmark.py` 默认运行60秒，测量45植物、30僵尸、100投射物和20阳光的
1050×600压力画面及冷启动时间。其SDL dummy帧率适合复现本机软件渲染负载，
不能代替真实显示驱动及最终exe上的Windows验收。

## v0.7.1 顶部 HUD、结算稳定与高清背景

- 波次/关卡/下一波预告改为顶部 HUD 单行状态条，位于卡片下方、草坪上边界之前；移除草坪内预告面板和浮动公告。
- 新增 `assets/backgrounds/`：日间/夜间/黄昏三套 2560×1440 真实感照片背景，主菜单“更换背景”立即应用；选择写入 progress 的 `settings.background_id`，旧 v1 自动迁移。
- 背景源为 Wikimedia Commons 的 “Mona-lawn-dusk-Panorama1.jpg”（作者 Wiki ian，CC BY-SA 3.0），仅做裁切/色彩分级；作者、来源、授权、SHA-256 见 `assets/backgrounds/source/provenance.json`。运行时不联网。
- 第一关结算增加真实胜利回归（20 次）和错误边界；结果/保存/下一关异常显示可恢复提示并保留返回菜单/重试。
- 定向检查：`pytest tests/integration/test_hud_layout.py tests/integration/test_result_flow.py tests/unit/test_backgrounds.py tests/unit/test_campaign_progress.py -q`。
- 背景构建：`.venv/Scripts/python.exe tools/generate_backgrounds.py`；资源校验：`.venv/Scripts/python.exe tools/validate_assets.py`。

## v0.7.0 战役、无尽与流畅表现

- 关卡数据在 `assets/levels/campaign.json` 与 `day_01.json`～`day_05.json`；`config.load()` 仍返回 day_01，`config.load_campaign()` 返回完整战役。
- 进度写入 `%LOCALAPPDATA%\PvzMiniGame\progress.json`；损坏时回退 day_01。只保存解锁、最佳星级/时间和无尽记录，不保存外观。
- 无尽模式由 `domain/endless.py` 的确定性导演追加波次，并限制同屏僵尸；通关 day_05 后解锁。
- 狗狗完整轮廓由 `tools/import_dog_assets.py` 的整图连通轮廓路径生成；动作帧仍约 12 姿态/秒，表现层叠加 60Hz 次级动作。
- 定向检查：`pytest tests/unit/test_campaign_config.py tests/unit/test_campaign_progress.py tests/unit/test_endless.py tests/integration/test_campaign_flow.py -q`；狗狗边界见 `quickstart.md`。
