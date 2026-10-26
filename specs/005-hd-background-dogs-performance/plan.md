# Implementation Plan: 高清背景、狗狗素材与运行流畅度

**Branch**: `version1` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

## Summary

复用现有 60Hz Simulation、manifest 图集、Animator、独立外观选择和 PyInstaller 发行结构。先测当前打包版的真实卡顿，再按原房屋、道路及种植格布局更新背景；将小杜、小宝和好孩子的新动作表导入照片版，并以其外形制作卡通版；最后调整角色尺寸、优化实测瓶颈并重新打包验收。三张用户上传的原始 10×6 动作表已保存在 `assets/skins/dogs/source/`。

## Technical Context

**Language/Version**: Python 3.12.15  
**Primary Dependencies**: pygame-ce 2.5.8、PyInstaller（沿用项目现有依赖）  
**Storage**: 本地 PNG/JPEG、JSON manifest、来源记录；运行不依赖网络  
**Testing**: pytest、`tools/validate_assets.py`、真实窗口与打包版性能测试  
**Target Platform**: 用户当前 Windows 电脑上的打包游戏  
**Project Type**: 离线桌面游戏  
**Performance Goals**: 固定标准场景（5向日葵、5豌豆射手、5僵尸、10投射物、3阳光、5割草机）60秒平均至少55 FPS；固定压力场景（45植物、30僵尸、100投射物、20阳光、5割草机）与标准场景P95帧间隔至多33ms；20次操作P95可见反馈至多100ms  
**Constraints**: 保持玩法 60Hz、既定 12–18 姿势/秒、小杜 2 秒清行和固定网格坐标；新背景有可核查许可  
**Scale/Scope**: 经典、狗狗卡通和狗狗照片三种植物外观；僵尸沿用经典/狗狗外观；1050×600 至 1920×1080 窗口

## Constitution Check

- **I 完整核心循环**: PASS；最终验收覆盖开始、阳光、种植、敌人、胜负与重开。
- **II 规则与渲染分离**: PASS；外观和性能改动限制在素材、呈现及主循环，不使 Simulation 依赖皮肤。
- **III 数值集中管理**: PASS；玩法参数仍由既有配置提供，角色显示倍率仅由 manifest 控制。
- **IV 核心玩法修改必须验证**: PASS；使用确定性重放和实机输入、渲染测试确认行为。
- **V 已有功能可运行**: PASS；经典和旧狗狗外观均回归，缺失新素材按既有整套外观回退。

## Project Structure

```text
specs/005-hd-background-dogs-performance/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/appearance-and-performance.md
assets/skins/default/             # 高清背景
assets/skins/dogs/                # 卡通狗狗资源及三张用户源图
assets/skins/dogs_photo/          # 照片版完整皮肤（新）
assets/sources.json               # 素材来源
src/pvz_game/presentation/        # 皮肤选择、动画与绘制
src/pvz_game/app.py               # 主循环和实机测量
tools/import_dog_assets.py        # 沿用动作表导入
tools/benchmark.py                # 压力场景
tests/integration/                # 外观与性能相关回归
docs/validation/005/             # 截图、帧间数据和发行证据
```

**Structure Decision**: 不引入新玩法层；新增一个符合现有 Skin 协议的皮肤目录，并扩展既有导入、渲染和验收工具。

## Phase 0: Research

决策见 [research.md](research.md)。保留布局比直接替换任意网络草地图片更重要；最终背景只采用许可允许的素材。照片版和卡通版各有完整动作，照片版的被窝、嗷嗷嗷沿用卡通；被窝取仓库现有 `beiwo-sheet.png` 灰白毛源表（其金色围巾属于原图）。先加入仅用于采样的性能入口并打包旧画面基线，再做素材和渲染改动，最后按实测瓶颈优化。

## Phase 1: Design and Contracts

模型见 [data-model.md](data-model.md)，用户可见选肤和性能验收见 [appearance-and-performance.md](contracts/appearance-and-performance.md)，端到端验证步骤见 [quickstart.md](quickstart.md)。`dogs_photo` 是完整植物皮肤，菜单阶段选择；皮肤对玩法没有影响。背景和角色均预先缓存适合逻辑画布的表面，避免主循环重复高成本缩放；具体优化以实测为准。

## Post-Design Constitution Check

五项原则仍通过。第三种皮肤增加图集大小和加载成本，必须用冷启动及真实窗口基准证明可接受；若未达标，优化缓存和图集组织，不降低规则 tick 或丢弃必要动作。
