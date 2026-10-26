# Quickstart: 阳光界面、拖铲操作与小狗动作素材

本文在功能实现后验证本Feature。命令以仓库根目录的Windows PowerShell为工作目录。

## 前置条件

- Windows 10/11 x64。
- 项目已有`.venv`及依赖；不需要新增运行时安装。
- 小宝和小杜原始60帧素材已放入`assets/skins/dogs/source/`；运行导入器前确认源图摘要与provenance一致。

## 自动验证

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe tools/validate_assets.py
```

**预期**：测试通过；默认和dogs清单的角色/action clips完整，帧矩形、来源、锚点、循环和独特姿势速率符合既有门槛。

## 启动与人工窗口检查

```powershell
.venv/Scripts/python.exe -m pvz_game
```

在真实窗口执行以下检查并记录结果：

1. 在1050×600、1260×720、1920×1080窗口观察左上角阳光面板；确认文字完整、在首张卡片左侧且不拦截草坪阳光拾取。
2. 点击每张卡选植物；再逐张卡分别拖到空格种植。每次确认只种一次、只扣对应费用并开始冷却。
3. 拖植物到占格、草坪外、留边和HUD/暂停控件上；再测试阳光不足、冷却以及右键/Esc、暂停/结束、失焦取消。确认失败不误种、不扣费、不穿透界面控件。
4. 用点击铲子后点击植物移除；再拖铲子到植物上释放。确认目标仅移除一次且不退阳光。
5. 将铲子拖到空格、草坪外和控件上，确认不误删；完成一次暂停/失焦/结算期间取消测试。
6. 选择小狗外观，检查坚果墙小宝、火爆辣椒小杜在卡片、预览和场上的身份；逐一检查其适用clip中的帧序、方向、锚点及状态切换。素材不齐时记录缺失，不标记通过。
7. 重开并完成完整对局循环；以相同场景对比default/dogs玩法状态结果。
8. 在Windows 60Hz设备的1260×720窗口和普通对局下，采集至少200个拖动中的真实鼠标移动样本；从程序取出事件到首次显示更新预览画面计时，并检查P95≤50ms。

**预期**：阳光余额正确；拖放/点击路径与同一玩法规则一致；无无效操作副作用；外观只改变图像，不改变玩法。素材和窗口视觉验收需截图/记录具体尺寸与结果。

## 拖动预览响应测量

在Windows 60Hz显示设备的1260×720真实窗口中，进入普通对局后执行：

```powershell
.venv/Scripts/python.exe tools/benchmark.py --input-latency --seconds 60
```

测量需要至少200个拖动期间的实际鼠标移动事件。计时从游戏程序取出鼠标移动事件开始，到首次显示包含新预览的画面结束。报告需记录设备、刷新率、窗口尺寸、样本数与P95；样本少于200时重测，SDL dummy结果不能作为实机通过证据。
## 发行包回归

实现和资源检查通过后：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
.venv/Scripts/python.exe tools/verify_bundle.py
```

**预期**：标准PyInstaller onedir ZIP包含dogs源素材导入后的运行资源；移动到中文/空格路径仍可启动并完成自动smoke。该smoke不替代真实Windows鼠标试玩。

## 相关契约

- 输入及界面行为：[contracts/interaction.md](./contracts/interaction.md)
- 数据边界：[data-model.md](./data-model.md)
- 调研决策：[research.md](./research.md)

