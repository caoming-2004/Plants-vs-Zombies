# Quickstart Validation: 完整狗狗形象、五关战役与流畅表现

**Feature**: `012-dog-legs-playability-smoothness` | **Date**: 2026-10-31

本指南只覆盖本次改动必须验证的路径：狗狗完整轮廓、5 关战役/解锁/保存、无尽模式、关键流畅表现和 Windows 包启动。不要运行全量 pytest、长时间压力测试、全部外观组合或安卓流程。

## 环境

- Windows x64，项目 `.venv` 已安装 Python 3.12 与 pygame-ce 2.5.8。
- 所有命令在仓库根目录执行。
- 无需联网；资源、字体和关卡 JSON 都随项目提供。

```powershell
.\.venv\Scripts\python.exe -m pvz_game --smoke-frames 5
```

预期：窗口打开并正常绘制，无资源错误；关闭后进程退出。

## 1. 狗狗完整轮廓

### 1.1 重新生成动作帧

```powershell
.\.venv\Scripts\python.exe tools\import_dog_assets.py
.\.venv\Scripts\python.exe tools\validate_assets.py
```

预期：

- 导入工具成功处理被窝/嗷嗷嗷的 12 个源姿态，未改写原始 PNG。
- `validate_assets.py` 输出 `default/dogs/dogs_photo: valid`。
- 被窝/嗷嗷嗷的脚掌、腿、尾巴和耳朵在 atlas 帧内完整；帧边缘有透明留白。

### 1.2 定向边界检查

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration/test_animation.py -k dog_frame_bounds -q
```

预期：1 passed（或本次新增的等价定向用例通过）。

### 1.3 人工对照

```powershell
.\.venv\Scripts\python.exe tools\preview_animations.py --export docs\validation\012\animations
```

打开导出的狗狗动作图，按空格切换外观并检查：

- 菜单、卡片、地图、拖动预览中，被窝和嗷嗷嗷的四条腿/脚掌、尾巴、耳朵与口鼻完整。
- 抬腿、尾巴展开、卧倒和倒地姿态没有被平切；相邻姿态没有串入。
- 地图四角/相邻格子不裁切；脚底基线与现有狗狗一致。

## 2. 五关战役与进度

### 2.1 定向配置/进度检查

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_campaign_config.py tests/unit/test_campaign_progress.py -q
```

预期：

- 5 个关卡 ID 连续、顺序与 `campaign.json` 一致，波次/星级/可用植物/割草机行通过校验。
- 通关解锁下一关；失败不解锁；重复通关保留最佳星级；损坏进度回退到 day_01 且不崩溃。

### 2.2 实际试玩

```powershell
.\.venv\Scripts\python.exe -m pvz_game
```

按以下路径操作：

1. 主菜单 → 开始游戏 → 关卡选择：只有第 1 关可进入，其余显示锁定。
2. 通关第 1 关：结算显示胜利、星级目标和获得星数，下一关解锁；用“下一关”直接进入。
3. 依次通关到第 5 关；确认每关敌人组合/节奏/压力条件不同，波次预告与实际出怪一致。
4. 在第 2 关故意失败：重试必须以完整初始状态开始，不推进解锁。
5. 关闭游戏并重新启动：已解锁关卡、最佳星级保留；重玩同一关且成绩较低时，最佳星级/时间不被覆盖；外观选择不要求保留。
6. 找到 `%LOCALAPPDATA%\PvzMiniGame\progress.json`，确认解锁/星级字段；将文件临时改名为 `.bak` 后启动，再改回，确认回退不崩溃。
7. 写入一段无效 JSON 到 `progress.json`，启动游戏，确认回到 day_01 且界面有提示；恢复原文件。

预期：上述流程 5 关均可完成；进度只增不减；失败/重开不继承上一局植物、僵尸、阳光、冷却或波次。

## 3. 无尽模式

前置：先通关第 5 关。

```powershell
.\.venv\Scripts\python.exe -m pvz_game
```

1. 返回关卡选择，确认无尽入口已解锁；点击进入。
2. 连续推进至少 10 波：敌人持续出现且强度提升，没有“清空即胜利”或空场卡住。
3. 让防线被突破：结算显示本次生存波数/击杀/最佳记录；重试从第一波开始。
4. 重新启动：无尽解锁状态和最佳记录保留。

也可以运行：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_endless.py -q
```

预期：导演至少提前追加 2 波、同屏上限生效、失败结算和记录断言通过。

## 4. 流畅表现

### 4.1 10 秒观察

在狗狗外观下开始一关，录制约 10 秒画面（Windows Game Bar/现有录屏工具即可），逐帧检查：

- 狗狗待机/行走/攻击：每帧有可见推进，无超过 50 毫秒的完全静止，无两个姿态叠加的重影。
- 阳光：下落/浮动连续，收集光效、余额更新和阳光消失同帧；点击位置与可见位置一致。
- 子弹：连续移动、尾迹自然，命中特效在子弹消失位置；没有提前消失或残留。
- 暂停/失焦 2 秒再恢复：狗狗、阳光、子弹全部冻结，恢复无跳变/重复。

### 4.2 标准场景基准

```powershell
.\.venv\Scripts\python.exe tools\benchmark.py --window --scene standard --seconds 60 --output docs\validation\012\benchmark.json
```

预期：平均 ≥58 帧/秒，95% 帧间隔 ≤18 毫秒，最长停顿符合现有验收；若失败，先降低特效密度/尾迹点数，不得改玩法规则。

### 4.3 兼容性回归

```powershell
.\.venv\Scripts\python.exe -m pytest tests/replay/test_base_replay.py tests/integration/test_skin_invariance.py -q
```

预期：全部通过；day_01 的事件、快照和胜负结果未因新字段/表现变化而改变。

## 5. Windows 构建与启动

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File packaging\windows\build.ps1 -ArtifactName PvzMiniGame-v0.7.0
```

预期：

- `validate_assets.py` 同时通过战役/关卡校验；
- `dist\windows\PvzMiniGame-v0.7.0\PvzMiniGame.exe` 可启动；
- 在包内完成一次主菜单 → 关卡选择 → 第 1 关胜利 → 重开/返回菜单流程；
- 新增 `assets/levels/*.json` 已随包提供，离线可运行。

## 不执行的检查

- 全量 `pytest`、所有外观/角色组合矩阵；
- 长时间（>5 分钟）压力或无尽极限测试；
- 安卓安装、触控、性能验收；
- 多设备/多分辨率矩阵。

若以上最小检查失败，应修复后重跑对应条目；不得把未执行或失败项标为通过。
