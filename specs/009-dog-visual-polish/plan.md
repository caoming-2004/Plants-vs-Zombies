# Implementation Plan: 狗狗视觉与阳光动效优化

**Branch**: `009-dog-visual-polish` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-dog-visual-polish/spec.md`

## Summary

在现有 Python/Pygame 单项目中校正狗狗卡通与照片两种外观中的可见轮廓和角色比例，并分别缩小被窝显示尺寸。保留现有坚果墙、豌豆射手；胖宝宝采用土豆雷的准备、触发、爆炸和消耗流程，黄黄采用寒冰射手的发射、伤害与移动/啃食减速流程。阳光增加出现、落地和轻柔浮动表现，游戏规则和资源值继续由现有 simulation 负责；优先复用现有 actor、projectile、plant config、卡片输入和素材 manifest。只做受影响规则、素材/尺寸、窗口性能和完整流程所需的精简验收。

## Technical Context

**Language/Version**: Python 3.12 x64  
**Primary Dependencies**: pygame-ce 2.5.x；已有 PyInstaller 发行流程；不增加运行时依赖  
**Storage**: 仓库内 PNG、JSON 配置/manifest、Python 游戏状态及 Markdown 验收记录  
**Testing**: pytest 定向单元/集成检查、素材校验、一次窗口观察与可玩包 smoke；完整测试套件不作为默认门槛  
**Target Platform**: Windows 11 x64 离线桌面游戏  
**Project Type**: 单一 Python/Pygame 桌面项目  
**Performance Goals**: 常规对局 10 秒观察中大多数帧间隔 ≤20 ms、无 >100 ms 的非预期卡顿；界面切换 ≤500 ms 开始呈现，使用 60fps 录屏逐帧或运行时单调时钟记录点击与首个目标场景画面的时间；玩法更新仍为 60 Hz  
**Constraints**: 新角色仅在狗狗外观中可选；关键数值放入 `assets/config/balance.json`；动画坐标须与点击命中一致；保留经典植物及完整核心循环；快速交付并限制测试数量  
**Scale/Scope**: 四项可见改进（两种狗狗外观的比例/完整显示、两种新植物职责、阳光动效、开始/切换响应）；一个现有关卡；无联网、存档或新游戏模式

## Constitution Check

**Pre-Phase 0**

- I 完整可玩的核心循环：PASS。新植物仍使用已有资源、卡片、种植与结算流程；验收覆盖一轮胜负和重开。
- II 游戏规则与渲染分离：PASS。土豆雷/减速判定进入 domain simulation；动画和角色轮廓留在 presentation；阳光命中坐标使用与画面相同的状态。
- III 关键数值集中管理：PASS。土豆雷准备时间、爆炸伤害/范围、寒冰伤害/减速系数/时长及价格/冷却集中在 balance 配置。
- IV 核心玩法修改必须验证：PASS。仅对新植物触发/效果/到期、收集输入、必要回归及完整可玩循环进行定向检查。
- V 新功能保持已有功能可运行：PASS。经典坚果墙和豌豆射手保留；经典外观和旧对局流程做受影响回归。
- 开发约束：PASS。沿用现有 config、simulation、systems、renderer 和 skin manifest，不引入新依赖或子项目。

**Post-Phase 1**: PASS。设计通过既有 `Plant`、`Projectile`、`Zombie`、`SunPickup` 与渲染/输入边界扩展；暂不需要新服务或持久化系统。

## Design Decisions

1. **角色映射与卡片可见性**：保留 `pangbaobao`、`huanghuang` 两个现有类型 ID 和狗狗卡片；实现土豆雷与寒冰射手职责，不取代 `wallnut`、`peashooter`。沿用现有卡片布局与皮肤过滤规则。
2. **土豆雷机制**：通过角色配置提供准备时间、触发距离、爆炸范围和伤害。准备期间不能爆炸，但仍可被敌人啃食；准备完成后敌人接近所在格触发一次范围伤害，随后移除。状态用现有植物 action/计时生命周期表示，避免为单一角色建立独立系统。准备时间初值采用 14 秒（840 tick），伤害和范围按本项目基础僵尸生命值在配置中调整。
3. **寒冰射手机制**：沿用既有同排目标选择、发射节奏和 projectile 命中结算；为冰豌豆加入减速参数。被命中的僵尸在有限时长内以配置速度系数移动、并按减速后的节奏啃食；再次命中刷新/延长效果但不叠加减速强度，过期后恢复原移速和啃食间隔。初值目标为 50% 移速/啃食频率、300 tick（5 秒），可由平衡配置调整。
4. **阳光运动**：将天空落下和植物产出作为两类视觉起点，落点仍是既有可收集阳光。确定性仿真维护阳光当前位置和阶段/时间，渲染层负责平滑位移、落地轻浮及轻量视觉强调；snapshot 的命中位置与绘制位置共用，暂停不推进。保持 `value`、生成间隔和 `expires_tick` 语义。
5. **完整轮廓与尺寸**：在 `animation.py` 的既有角色缩放/锚点和 `renderer.py` 的绘制路径调整狗狗显示；在 `assets/skins/dogs/manifest.json` 和 `assets/skins/dogs_photo/manifest.json` 中校正两种狗狗外观各自包含的角色，基于非透明身体边界对照最大伸展姿势和画布边界，分别缩小被窝并校准同外观内其余角色，不裁切原图来掩盖问题。胖宝宝与黄黄保持狗狗卡通外观专属。
6. **界面与性能**：检查 `app.py` 场景切换、`scenes.py` 主界面绘制与 `skin_catalog.py` 资源加载路径；复用预加载/缓存，避免开始点击后的同步工作阻塞首帧。以现有窗口 benchmark 观察 P95 帧时间；用 60fps 录屏逐帧或运行时单调时钟记录点击到首个目标场景画面的时间，重复 10 次。
7. **必要验证**：新增植物规则用定向单测；狗狗卡片、素材尺寸和阳光位置使用相关集成/素材校验；完整关卡只运行一次必要 replay/烟测；临时测试 EXE/ZIP 结束清理，正式包保留。

## Project Structure

### Documentation (this feature)

```text
specs/009-dog-visual-polish/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/dog-plants-sun-visual-contract.md
└── tasks.md                 # 由 speckit-tasks 后续生成
```

### Source Code (repository root)

```text
assets/config/balance.json
assets/skins/dogs/manifest.json
src/pvz_game/domain/{models.py,simulation.py,systems.py,plant_rules.py}
src/pvz_game/presentation/{animation.py,renderer.py,input.py,scenes.py,skin_catalog.py}
tests/unit/test_new_plant_rules.py
tests/integration/{test_drag_input.py,test_animation.py,test_playable_loop.py,test_asset_manifest.py}
tools/{validate_assets.py,benchmark.py}
```

**Structure Decision**: 单一桌面应用。领域规则仍置于 `src/pvz_game/domain/`，图形与输入仍置于 `presentation/`，角色数值沿用 JSON 平衡配置；不新建项目或服务。

## Validation Gates

- 狗狗姿态的可见身体轮廓完整；被窝较当前版本缩小约 20%，狗狗可见高度差异约不超过 20%。
- 胖宝宝准备期间不能爆炸但仍可被僵尸啃食；准备完成后触发一次爆炸。黄黄命中造成伤害并暂时减慢僵尸移动和啃食频率，重复命中不叠加强度，效果到期后两者恢复。
- 天空和植物生成阳光可见平滑下落、落地浮动；点击位置与显示位置一致，资源只结算一次，暂停/到期行为不变。
- 开始/切换的目标界面 500 ms 内开始呈现；标准窗口观察达到规格的帧时限。
- 经典坚果墙、豌豆射手和既有完整核心循环通过必要回归；可玩构建 smoke 成功。

## Complexity Tracking

无宪章违规，无新增依赖，无新增项目/服务。
