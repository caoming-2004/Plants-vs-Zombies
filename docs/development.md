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
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Diagnostic
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
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
.venv/Scripts/python.exe tools/validate_assets.py
.venv/Scripts/python.exe tools/preview_animations.py --export docs/validation/animations
.venv/Scripts/python.exe tools/benchmark.py
```

classic导入器需要.tools/references/中已下载并记录提交的原始参考，运行时与打包不依赖该目录。
AI源图位于assets/skins/dogs/source，最终提示词与用户确认见docs/art。
运行时只读取assets/skins/default与dogs，不需要AI工具或网络。

最终构建输出版本化目录dist/PvzMiniGame-v0.2.0/与通用发行包dist/PvzMiniGame-windows-x64.zip；
历史版本化ZIP不作为当前构建结果。
构建前要求两套完整动作资源，不用prototype或缺失小狗资源通过构建。
Windows PowerShell5读取UTF8脚本需要BOM，tools/build.ps1保存为UTF8 BOM以确保中文启动说明文件名正确。

`tools/benchmark.py` 默认运行60秒，测量45植物、30僵尸、100投射物和20阳光的
1050×600压力画面及冷启动时间。其SDL dummy帧率适合复现本机软件渲染负载，
不能代替真实显示驱动及最终exe上的Windows验收。
