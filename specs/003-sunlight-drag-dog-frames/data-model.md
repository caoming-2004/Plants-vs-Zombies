# Data Model: 阳光界面、拖铲操作与小狗动作素材

本功能不增加领域玩法实体或持久化状态，复用目前的 `Simulation.snapshot()`、输入命令和皮肤manifest。下列模型描述新增/受影响的数据边界。

## 1. 阳光余额视图

| 字段 | 类型 | 来源 | 约束 |
|---|---|---|---|
| `sun` | 非负整数 | `snapshot['sun']` | 唯一权威值由Simulation持有；绘制层不缓存副本。 |
| `hud_rect` | 逻辑坐标矩形 | Presentation共享场景几何 | 左上角可见；不得与四张植物卡或必要交互区域相交；renderer/input/拖动预览共用同一个矩形。 |
| `collectibles` | 当前阳光实体集合 | `snapshot['suns']` | 独立绘制和命中；余额显示不能替代或拦截其有效拾取。 |

## 2. 瞬时拖动态

拖动态只在Presentation中存在，退出/暂停/失焦/结算后清除，不保存到Simulation，不进入存档。

| 字段 | 类型 | 说明 |
|---|---|---|
| `tool_kind` | `plant` 或 `shovel` | 当前按下来源工具。 |
| `plant_type_id` | 植物ID或空 | `tool_kind=plant`时标识四种植物之一；铲子时为空。 |
| `pointer` | 逻辑坐标或空 | 当前指针位置，已转换为1050×600逻辑画布坐标。 |
| `hover_cell` | `(row, col)`或空 | 当前落点格；草坪外/留边处为空。 |
| `preview_valid` | 布尔值 | 当前只读snapshot下目标是否可执行。 |
| `reason_code` | 原因码或空 | 种植预览复用`placement_reason`；铲子预览区分有植物、空格、草坪外。 |

**生命周期**：`idle → pressed(tool) → dragging(tool,target) → completed | cancelled`。只有有效释放可生成命令。短按来源卡/铲子仍按既有点击语义选择工具。目标格释放使用当下snapshot重新检查；Presentation预览不是授权或最终规则判断。

### 命令映射

| 玩家操作 | Presentation产生的命令 | Domain职责 |
|---|---|---|
| 点击植物卡 | `SelectPlant(type_id)` | 记录当前选中植物。 |
| 拖植物到空格 | 按序`SelectPlant(type_id)`、`PlantAt(row,col)` | 检查阶段、资源、冷却和占格；成功一次扣费并设置冷却。 |
| 点击铲子 | `SelectShovel` | 记录铲子选择。 |
| 拖铲子到有植物格 | 按序`SelectShovel`、`ShovelAt(row,col)` | 仅移除该格当前植物，不返还阳光。 |
| 无效释放/取消/焦点或阶段变化 | 无`PlantAt`/`ShovelAt`命令 | 不改变游戏状态；既有取消选择规则继续生效。 |

## 3. 小狗角色动作素材

素材仍通过`assets/skins/dogs/manifest.json`表示。源素材为每只狗用户提供的60帧图像（逐帧文件或合成图），在上传和检查后归一化到现有manifest帧条目。不得把未检查的推测写为源帧分组。

| 资产概念 | 字段/关联 | 验证约束 |
|---|---|---|
| 原始帧来源 | 角色（小宝/小杜）、输入文件、源文件摘要 | 可追溯；使用用户提供帧，不静默替换为旧生成帧。 |
| 角色映射 | 小宝→`wallnut`；小杜→`jalapeno` | 卡片、预览、场上渲染角色一致。 |
| 动作clip | `wallnut`: `idle/hit/die`；`jalapeno`: `plant/ignite/hit/die` | clip覆盖`skin_catalog.REQUIRED`要求；每帧播放时长为正整数tick。 |
| 帧定位 | `rect`、`source_size`、`trim_offset`、`anchor`、`muzzle`、`contact` | 图片边界、裁切、脚底/接触定位有效；动作切换位置连续。 |
| 动作时间 | `duration_ticks`、clip `loop` | 沿用60tick/s模拟时间轴；通过现有独特姿势/秒及循环时长校验。 |

源图收齐后，根据可见动作、帧序和锚点建立source-frame至clip的映射。缺帧/损坏时继续使用既有阵营级默认外观回退；不能把半套小狗素材混配后声称验收通过。

## 关系

- `Sunlight HUD`读取`Simulation.snapshot.sun`；`SunPickup`实体仍由游戏世界独立保存和收集。
- `DragState`引用一个工具和一个可选草坪格，不拥有Plant或阳光。
- `Skin Manifest`将角色映射到图集帧；`Animator`按角色状态和游戏tick取帧，不调用Simulation命令。
