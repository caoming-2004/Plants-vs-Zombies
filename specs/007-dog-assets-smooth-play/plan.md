# Implementation Plan: 狗狗素材与流畅可玩体验

**Branch**: `007-dog-assets-smooth-play` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

## Summary

复用现有 Python/Pygame 架构、狗狗图集导入、manifest、动画缓存和菜单输入路径。导入本轮三张图，统一地图尺寸并保证全身可见；测量并优化开始界面的首次加载耗时；以精简试玩验证核心循环，清理本轮临时测试产物。

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: pygame-ce；现有 PyInstaller 发行工具  
**Storage**: 本地 PNG、JSON 清单与 Markdown 验收记录  
**Testing**: 现有素材校验、针对性 pytest、真实窗口试玩  
**Target Platform**: Windows 离线桌面游戏  
**Project Type**: 单一 Python/Pygame 桌面游戏  
**Performance Goals**: 开始点击后 1 秒内可操作；动画连续且不阻塞输入  
**Constraints**: 三狗站立高度比≤1.15；身体完整；不改玩法规则；精简测试  
**Scale/Scope**: 三张用户图片、三只现有狗狗角色、菜单切换和一局核心玩法

## Constitution Check

- I 完整可玩循环：PASS；验收覆盖开始、资源、种植、战斗、胜负和重开。
- II 规则与渲染分离：PASS；素材、尺寸及缓存位于导入和显示层。
- III 数值集中管理：PASS；角色倍率沿用 manifest，玩法配置不变。
- IV 核心修改验证：PASS；不计划修改规则，仍对受影响交互和完整一局验收。
- V 已有功能回归：PASS；检查角色映射、开始、核心循环和重开。
- Post-design：PASS；无新依赖或架构层。

## Design Decisions

1. 复用 `tools/import_dog_assets.py`，保持 `peashooter=好孩子`、`wallnut=小宝`、`jalapeno=小杜` 映射；核对本轮原图尺寸和背景后导入，保存哈希与来源帧。
2. 复用 `display_scale_multiplier`、`DOG_SCALE`、锚点和 `dog_validation.py`；按站立可见高度校准，逐姿态检查透明边界、地图边缘和相邻遮挡。逻辑坐标及碰撞规则不变。
3. 保持 `animation.py` 的 tick 时序和缩放缓存。导入时完成素材处理；若首次缩放造成停顿，在菜单阶段预热必要帧。
4. 从鼠标按下事件进入游戏事件循环开始分段计时，分别记录可见按钮反馈、图片加载、`renderer.draw`、首次缩放以及首个可接收有效游戏输入的画面；优先缓存现有资源，不改变状态机语义。
5. 只执行素材校验、受影响的少量现有测试与一次真实窗口完整试玩。记录结果；仅清理本轮生成且路径明确的临时 EXE/ZIP。

## Project Structure

```text
specs/007-dog-assets-smooth-play/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/gameplay-visual-contract.md
├── quickstart.md
└── tasks.md                 # 后续 $speckit-tasks 创建

tools/import_dog_assets.py
src/pvz_game/app.py
src/pvz_game/presentation/animation.py
src/pvz_game/presentation/renderer.py
src/pvz_game/presentation/skin_catalog.py
src/pvz_game/presentation/dog_validation.py
assets/skins/dogs/
assets/skins/dogs_photo/
assets/sources.json
docs/validation/007/
```

**Structure Decision**: 维持单项目；素材归导入工具和 assets，显示与输入归 presentation/app，domain 规则保持权威。
