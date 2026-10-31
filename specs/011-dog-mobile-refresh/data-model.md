# Data Model: 狗狗素材修复与双平台可玩版本

## Authoritative Game State

继续由 `src/pvz_game/domain/simulation.py` 的 `Simulation` 保存唯一对局状态。Android 只适配触摸事件、屏幕和应用生命周期；Windows 与 Android 不保留各自不同的玩法状态副本。

## Existing and Updated Entities

### Dog Animation Asset

源图和派生动作帧由 `assets/skins/dogs/source/`、狗狗 atlas、`manifest.json` 与 `provenance.json` 表达。

| 属性 | 约束 |
|---|---|
| `source_asset` | 被窝/嗷嗷嗷原始高清图，作为只读来源保留 |
| `frame_bounds` | 每个姿态对应独立边界；不得混入相邻帧 |
| `visible_bounds` | 角色身体、所有可见腿脚与尾巴全部包含在内 |
| `transparent_padding` | 为缩放与动画位置变化保留透明边距，避免帧间抖动/被裁 |
| `animation_state` | 沿用现有 idle/move/attack/hit/death 等 manifest 状态，不新增与玩法无关的状态系统 |

**Invariant**: 源图不得被打包脚本回写；Windows 与 Android 的角色边界、大小比例和帧顺序读取同一 manifest/atlas。

### Plant Configuration and Plant Instance

- `PlantConfiguration` 继续定义于 `assets/config/balance.json`；`pangbaobao` 从 `potato_mine` 变更为 `squash`。
- 倭瓜的阳光价格、冷却、触发距离/攻击距离、伤害和动作时间均有单一命名字段和单位。
- 植物实例复用现有 `Plant` 生命周期，由领域状态标识普通待机、蓄势/跳击、命中和消耗/死亡。具体字段最小扩展，不能重复存储一份渲染专属权威状态。
- 倭瓜攻击结束后只结算一次并移除单位；不得进入土豆雷的埋地武装/踩踏触发生命周期。

### Logical Pointer and Touch Gesture

- **Existing state**: 现有连续 `DragState.pointer`、候选格、工具种类、是否合法及拒绝原因。
- **Android adapter**: 主 `finger_id`、归一化/物理位置转换成逻辑画布坐标、按下/移动/松开状态；平台适配不自行决定种植费用和候选格。
- **Lifecycle**: FINGERDOWN 开始一次操作；FINGERMOTION 更新连续预览；FINGERUP 在松开点计算唯一最近格并走现有规则校验。其它触点不抢占主触点；Android 生成的同一操作鼠标事件去重。
- **Invariant**: 有效候选、占格拒绝、不扣资源和冷却均由共享输入流程/Simulation 保证，双平台一致。

### Platform Build Artifact

该实体是项目文件边界记录，不是游戏持久化数据。

| 字段 | 含义 |
|---|---|
| `platform` | `windows` 或 `android`，必须明确且唯一 |
| `configuration_root` | Windows 配置在 `packaging/windows/`；Android 配置在 `packaging/android/` |
| `staging_root` | Windows 为 `build/windows/`；Android 为 `build/android/` |
| `release_root` | Windows 为 `dist/windows/`；Android 为 `dist/android/` |
| `validation_root` | Windows 为 `docs/validation/011/windows/`；Android 为 `docs/validation/011/android/` |
| `runtime_data_root` | Windows 用户数据目录或 Android 应用私有目录；不得写进共享源码/只读资源 |

**Isolation rules**:

1. 任一平台的 build、test、clean 命令只拥有该平台的专属 staging、validation 和 release 子目录。
2. 平台专属输出不得使用项目根 `build/` 或 `dist/` 作为最终写入目标。
3. Windows 与 Android 的 APK/EXE/ZIP（若最终发行需要）互不存放、互不清理。
4. `src/`、`assets/` 及相同的源素材仍是一套权威副本；构建只读，不回写、不另造平台副本。
5. 交叉隔离验收记录两平台构建文件清单及 SHA256；构建或清理另一端后，哈希与路径必须保持不变。

## Data Migration

无需迁移玩家存档；当前关卡状态为单次运行内存状态。角色规则 ID 更新由配置、规则校验和测试夹具同步完成。既有 Windows 构建脚本/配置迁入 Windows 专属打包目录时，活动 README/quickstart 调用同步更新；历史 spec 作为已完成记录不批量重写。
