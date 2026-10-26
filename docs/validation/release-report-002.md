# v0.2.0 动画、拖放与新增植物交付记录

日期：2026-10-26。当前工作分支：`version1`。

## 已交付

- 四张植物卡可点选或拖动；新植物为坚果墙和火爆辣椒。
- 僵尸/植物规则与表现分离；火爆辣椒按同排现存敌人清除一次，并播放不会改变模拟状态的整行火焰表现。
- 小狗映射：向日葵被窝、豌豆射手黄黄、坚果墙小宝、火爆辣椒小杜、普通僵尸嗷嗷嗷（红背心）。
- default/dogs两套5角色动作资源和动画验证；选肤菜单可同时查看五种角色。
- 双击入口为 PyInstaller onedir 包内的 `PvzMiniGame.exe`，运行不需要单独安装 Python或联网。请完整解压 ZIP 并保留 `_internal` 文件夹。

## 自动验证

- `.venv/Scripts/python.exe -m pytest -q`：100 passed。
- `.venv/Scripts/python.exe tools/validate_assets.py`：default 538、dogs 441引用帧通过；动作姿势采样率和循环时长检查通过。
- `.venv/Scripts/python.exe tools/verify_bundle.py`：ZIP移至中文/空格路径后，四种皮肤组合游戏场景以及小狗选肤菜单均以退出码0启动。子进程PATH不含Python，代理指向不可达本地端口；这仍是SDL dummy headless smoke，不代表系统断网或真实鼠标试玩。
- 包SHA256：`9488f9ae5fe51362226f4e88e1efb0e9c4f19d304b0e7b487e5ea36ca22a6df1`。

## 未执行的验收

- NOT_RUN：60秒标准设备/压力场景平均FPS、P95帧间隔和真实输入延迟。
- NOT_RUN：Windows 10/11标准用户、系统断网和真实桌面双击验收。
- NOT_RUN：20次真实鼠标拖放、连续30分钟稳定运行及新手试玩。
- NOT_RUN：门头沟每只狗的原型相似度与全部动作衔接目视审核。现有角色素材是按公开线索和用户指定名称生成的原创卡通解释；黄黄、小宝没有可验证的正面参考照片。

## 构建产物

- [游戏 EXE](../../dist/PvzMiniGame-v0.2.0/PvzMiniGame.exe)（需与同目录 `_internal` 一起使用）
- [Windows x64完整 ZIP](../../dist/PvzMiniGame-windows-x64.zip)
- [四组合及菜单 smoke 记录](./bundle-smoke.json)
- [五角色小狗场景预览](./final-play.png)
