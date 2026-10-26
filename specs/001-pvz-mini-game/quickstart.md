# Quickstart 与验证指南

本指南对应当前已实现的Python 3.12/pygame-ce游戏与Windows onedir发行流程。
玩家只需完整解压发行包并双击exe；开发、自动化和实机验收步骤供维护者使用。

## 开发环境（开发者）

前提：Windows x64、uv；仅准备依赖与素材时联网。开发者工具不随玩家操作要求提供。
在项目根目录执行：

```powershell
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e '.[dev]'
.venv/Scripts/python.exe -m pvz_game
```

项目已在pyproject.toml声明pygame-ce及测试/打包开发依赖，并将src配置为包目录。
复现环境从requirements.lock.txt安装依赖：

```powershell
uv pip install --python .venv/Scripts/python.exe -r requirements.lock.txt
uv pip install --python .venv/Scripts/python.exe --no-deps -e .
```
不得用系统现有Python3.8.5直接构建，也不得同时安装pygame和pygame-ce这两个占用同一导入名的包。

## 规则、素材和回放检查

```powershell
.venv/Scripts/python.exe -m pytest tests/unit tests/integration tests/replay
.venv/Scripts/python.exe tools/validate_assets.py
.venv/Scripts/python.exe tools/preview_animations.py
```

预期：pytest通过；资源清单及动作覆盖检查无误；预览可检查全部角色和状态切换。
无窗口环境下可为渲染冒烟测试设置SDL_VIDEODRIVER=dummy，但该结果不替代真实画面验收。
回放至少3组相同关卡/输入，比较默认、只换植物、只换僵尸、双方换肤的规则状态和事件序列。
默认资源缺失应中文报错；小狗缺帧或图集损坏应回退对应阵营默认外观并提示。

## 完整对局验证

1. 开始游戏并收集自然阳光，种向日葵，验证产出与余额；种射手，验证同排攻击。
2. 验证余额不足、冷却、重复占格、场外点击和快速连点均不错误扣费。
3. 选择铲子清除植物，余额不增加且卡片冷却不重置；点击空格无效果，右键/Esc取消。
4. 不防守使僵尸触发一行割草机，确认只清除沿途敌人且其他行不变；后续突破该行时失败。
5. 重新开始，确认所有割草机和游戏状态恢复，所选皮肤保留。
6. 合理种植完成一次胜利；暂停期间阳光、冷却、僵尸、投射物和割草机完全停止。
7. 对四种外观组合重复胜利、失败和重开；测试同tick最后僵尸死亡与防线判断边界。

## 视觉与小狗映射

按contracts/assets-and-release.md建立参考对照板并逐状态审核。
先提交小狗名称、参考、三角色对应和动作适配方案给用户确认，再正式制作。
每种动画至少观察3循环及所有适用过渡；比对原版方向、节奏、比例、发射/接触位置。
截图与实际验收记录放docs/validation；程序校验通过不代表视觉已通过。

## 构建和玩家验收

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
.venv/Scripts/python.exe tools/verify_bundle.py
```

构建脚本先运行完整测试与资源校验，再通过packaging/pvz_game.spec构建onedir，
把版本化目录打包到dist/PvzMiniGame-windows-x64.zip。当前包内目录为PvzMiniGame-v0.2.0，
包含exe、_internal资源依赖、开始游戏说明和字体许可。

玩家仅需完整解压并双击游戏exe。不得要求玩家执行上述开发命令。
在无Python、非管理员、断网的Windows10及11分别验证；将整个解压目录移动到含中文和空格路径再次启动。
删除或损坏资源的失败场景必须显示中文提示，不得无声退出。

持续游玩30分钟，暂停/继续和重开各10次；三名未参与开发的新手各在3分钟内完成开局、收集和种植。
使用最终发行包按plan.md压力负载测量帧率和启动时间，记录机器配置及结果；
源码侧的参考测量见docs/validation/performance.md，尚不替代最终包测量。
最终在docs/validation/release-report.md逐项对应SC-001至SC-009及FR-001至FR-022，注明证据、PASS/FAIL/NOT_RUN。
缺少Windows系统或试玩者时明确NOT_RUN，不以自动化测试替代实机和人员验收。

## 澄清后的边界验证

- 阳光到期前一tick可收集，到期当tick及后一tick不可收集；暂停不延长或推进模拟到期tick。
- 新投射物出生tick不移动或命中；下tick开始更新。已有投射物先结算命中，植物再行动，存活僵尸最后啃咬。
- 视觉检查使用contracts/assets-and-release.md的固定尺度：布局2逻辑像素、同姿态宽高5%、周期5%且至少允许1tick采样误差、接缝脚底1像素、关键事件1tick；必须保留测量与造型审核证据。

## 加长地图、HUD与小狗动画验收

1. 验证day_01配置为五行十二列，且全部格子坐标位于1050×600战斗画布内；12列均完整可见，格子保持72×76逻辑尺寸。
2. 以1260×720、1920×1080及最低支持客户区1050×600启动战斗画面；均应显示十二列且格子保持72×76逻辑尺寸。尝试缩小到1050×600以下时，窗口必须阻止调整到不受支持的尺寸；不能裁切或滚动。
3. 在场上制造密集单位，并让可收集阳光靠近右上HUD下方；导出截图核对阳光图标、余额和HUD文字无角色/特效/阳光覆盖。点击HUD、HUD边缘、场上阳光及草坪，逐次确认每次点击最多产生一个预期命令。
4. 分别预览每种小狗角色的idle、walk、produce、attack、bite及状态过渡；每个重复循环至少60 tick、动画采样至少30Hz，绘制目标60 FPS。记录循环时长、实际采样/绘制帧率，并确认受击/死亡未被错误拉长。
5. 将每个狗狗角色与对应默认角色测量高度，确认不低于75%；逐一覆盖三种角色的全部两两组合（含同角色配对），将其置于同一行相邻列的格子中心，对所有动作帧成对检查裁切偏移与脚底锚点还原后的非透明像素遮罩，不得相交；脚底锚点在循环接缝和状态切换不跳变。
6. 使用30FPS与60FPS绘制条件回放相同输入至少各三组，确认游戏逻辑事件、阳光、伤害、胜负和模拟tick相同；画面侧验证60FPS目标及至少30Hz动画更新。