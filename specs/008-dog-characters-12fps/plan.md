# Implementation Plan: 高清狗狗角色与十二帧动作

**Branch**: `008-dog-characters-12fps` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

## Summary

沿用单一 Python/Pygame 游戏架构。复用狗狗素材导入、图集、manifest、动画采样和来源记录，将项目内被窝、嗷嗷嗷高清图替换狗狗卡通外观中的同名角色。胖宝宝、黄黄作为两个独立植物类型加入现有配置和规则分派：前者复用防御职责，后者复用远程攻击职责。狗狗外观新增两张可操作卡片，经典外观维持既有卡片。将植物循环动画目标调为每秒 12 个可见姿态，保持游戏 60 Hz 更新和玩法事件时间。只验证受影响规则、素材、界面和一次完整核心循环，再构建可玩包。

## Technical Context

**Language/Version**: Python 3.12 x64  
**Primary Dependencies**: pygame-ce 2.5.x；既有 PyInstaller 打包；不新增运行时依赖  
**Storage**: 仓库内 PNG、JSON 配置/manifest/来源记录及 Markdown 验收报告  
**Testing**: 现有 pytest 中受影响的规则、素材和集成检查；真实窗口试玩与正式包烟测  
**Target Platform**: Windows 11 x64 离线桌面游戏  
**Project Type**: 单一 Python/Pygame 桌面应用  
**Performance Goals**: 植物循环动作 12±1 个不同姿态/秒；保留约 60 FPS 显示及 60 Hz 玩法更新  
**Constraints**: 新植物仅狗狗外观可选；价格和战斗数值单点配置；卡片不遮挡现有 HUD 和地图；快速交付、精简测试  
**Scale/Scope**: 两个旧角色换图、两个新植物角色、六张狗狗外观植物卡片、一个既有白天关卡

## Constitution Check

**Pre-Phase 0**

- I 完整可玩循环：PASS；新增角色使用既有阳光、种植、敌人、胜负、重开路径，先保证一局可玩。
- II 规则与渲染分离：PASS；植物价格/行为由 config 与 domain 判定，皮肤可见性由输入和渲染层控制，不复制种植结算。
- III 关键数值集中管理：PASS；胖宝宝和黄黄的价格、生命、冷却、攻击数值放在 `assets/config/balance.json`。
- IV 核心修改必须验证：PASS；两种新植物覆盖种植成功、阳光不足、冷却、占格、攻击/阻挡与重开；真实窗口核对输入和动画。
- V 已有功能可运行：PASS；原有四植物、僵尸、开始、胜负和重开做针对性回归。
- 开发约束：PASS；复用原有模块与图集，不增加服务或持久化层。

**Post-Phase 1**: PASS；设计继续满足上述边界，无宪章例外。

## Design Decisions

1. **素材导入**：先核对四张项目内 RGBA 图片的实际姿态排列与透明边界，不按文件尺寸猜测帧数。扩展 `tools/import_dog_assets.py` 的输入描述和动作映射；源图不改动，派生图集、哈希与角色对应关系写入既有来源记录。被窝与嗷嗷嗷替换 `dogs` 卡通外观中的同名角色；照片外观如已有独立来源则保持其既有身份映射。
2. **新植物规则**：在 `assets/config/balance.json` 增加 `pangbaobao`（blocker）和 `huanghuang`（shooter），复用 `src/pvz_game/domain/simulation.py` 与 `systems.py` 已有通用种植、扣费、阻挡和射击路径。对尚有按旧 ID 分派的代码做最小扩展。玩法状态仍由 Simulation 单独持有。
3. **狗狗外观限定**：`presentation/input.py`、`scenes.py`、`renderer.py` 扩展两张卡片及可见性条件；经典外观隐藏并拒绝选择新卡片，已选狗狗外观的地图与预览使用新图集。布局采用既有 1050×600 逻辑画布，先测量六卡片、阳光与暂停按钮可用区域再定位置；不得移动种植格或改输入坐标变换。
4. **动作节奏**：保持 `tick_hz=60` 和游戏显示节奏。让植物循环动作的帧持续时长等价于 5 个玩法 tick/姿态，或按同一规则将动作周期均匀分配到 12 姿态/秒；非循环动作保持既有事件持续时间。若源姿态不足，复用当前中间姿态生成路径，避免简单重复画面冒充不同姿态。
5. **验收**：先做素材/manifest 与针对性规则检查，再在真实窗口核对六张卡片、四张新素材和 12 FPS 观感，完成一次含资源、种植、战斗、胜负与重开的流程。正式包独立启动一次；失败或未执行项如实记录。测试临时 EXE/ZIP 在结束后清理，正式发行物保留。

## Project Structure

### Documentation

```text
specs/008-dog-characters-12fps/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/appearance-and-plant-contract.md
└── tasks.md                 # 由 $speckit-tasks 创建
```

### Source Code

```text
assets/config/balance.json
assets/skins/dogs/{manifest.json,provenance.json,source/,atlas*.png}
assets/skins/dogs_photo/manifest.json
assets/sources.json
tools/import_dog_assets.py
src/pvz_game/domain/{simulation.py,systems.py,plant_rules.py}
src/pvz_game/presentation/{input.py,scenes.py,renderer.py,animation.py,skin_catalog.py}
tests/{unit/,integration/,replay/}
docs/validation/008/
```

**Structure Decision**: 保持单项目及现有职责边界；没有新应用、服务或运行时依赖。

## Validation Gates

- 四张项目源图的尺寸、帧布局、透明度与身份对应已核验；卡片和地图无白底、裁切或串角。
- 狗狗外观可分别种植胖宝宝与黄黄；经典外观不显示其卡片；正常与三类拒绝种植路径通过。
- 所有植物循环动作在真实窗口达到 12±1 个不同姿态/秒；60 Hz 玩法、输入和非循环事件时长不变。
- 可玩包启动，一局核心循环与重开通过；只运行受影响检查并记录证据；临时测试包清理。
