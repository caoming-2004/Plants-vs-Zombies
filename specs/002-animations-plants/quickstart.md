# Quickstart: 动画、拖放与新增植物验证

在Windows x64项目根目录执行。前提是已按docs/development.md配置项目本地Python环境。

## 1. 静态配置与角色资源

```powershell
.venv\Scripts\python.exe tools\validate_assets.py
```

预期：配置中存在sunflower、peashooter、wallnut、jalapeno；skin validator对default/dogs检查五个角色的卡片、预览、适用动作、帧率、帧边界和来源记录。任何必需帧缺失或动作少于24个不同姿势/秒都返回失败并标出role/clip。

## 2. 规则与回归

```powershell
.venv\Scripts\python.exe -m pytest -q
```

预期：producer/shooter旧行为、blocker受咬/死亡/释放格、row_clearer整行唯一击杀、未来spawn不受影响、火爆辣椒费用冷却、胜负单次、旧US1回归及四种外观规则摘要全部通过。

## 3. 拖放试玩

```powershell
.venv\Scripts\python.exe -m pvz_game
```

在主菜单开始游戏。分别点选和拖动四种卡片；查看半透明预览、目标格状态和即时反馈。拖到空格、占用格、草坪外、HUD，尝试资源不足/冷却；取消并失焦后确认鼠标预览清除。确认四卡同时可见、默认和狗狗卡片名称正确，并能继续铲子/阳光/暂停/重开。

## 4. 新植物边界

将普通僵尸放至坚果墙所在行，确认停步啃咬；坚果墙死亡后该僵尸恢复前行。将多个僵尸放同一行并在另行放一个，放置火爆辣椒：命令时已有的同排僵尸立即死亡并各计一次，其他行不变；下一个tick/之后波次才生成的同排僵尸存活。最后一只敌人被清除时确认胜负只结算一次。

## 5. 画面、动作与性能

```powershell
.venv\Scripts\python.exe tools\benchmark.py --seconds 60
```

先记录实际Windows物理显示设备、刷新率、窗口尺寸、驱动和外观。标准场景要求平均≥58FPS、P95≤25ms且60Hz显示支持。固定压力场景为1050×600、45株植物、30只僵尸、100枚投射物、20个阳光，要求平均≥55FPS、P95≤33ms；在该场景中记录输入事件至首个可见拖动预览的延迟，P95≤50ms，20次操作零丢失/重复。SDL dummy结果只能用于自动化，不能代替实机验收。

分别检查四种外观组合及1050×600、1260×720、1920×1080截图，并在 `docs/validation/visual-quality-v2.md` 逐项记录：非预期帧裁切为0；循环首尾锚点差≤2逻辑像素；卡片、HUD和交互区域相互遮挡为0；无闪烁或透明边缘异常。每一组合/尺寸必须标PASS、FAIL或NOT_RUN并附截图。

## 6. 完整发行入口

运行完整测试和资源验证后使用：

```powershell
powershell -ExecutionPolicy Bypass -File tools\build.ps1
```

最终发行必须再从完整ZIP移至中文/空格路径验证；headless启动不能替代真实窗口/鼠标的拖放与SC-004性能测量。记录最终包哈希和未执行的外部人工验收。
