# 004 改动前基准

采集时间：2026-10-26；当前分支：version1；采集时尚未修改游戏代码。
素材节奏按RGBA逐像素去重；姿势率=unique_pose_count × tick_hz / duration_ticks；当前tick_hz=60。
当前dogs全局缩放DOG_SCALE=0.68；visible height是帧RGBA主体bbox经pixel_scale和DOG_SCALE折算后的逻辑像素范围。

## default/dogs全部动作clip动画基准

| Skin | Role | Clip | Frames | Unique RGBA poses | Duration (ticks) | Rate (/s) | Dog height (logical px) |
|---|---|---|---:|---:|---:|---:|---:|
| default | sunflower | idle | 54 | 54 | 108 | 30.0000 | — |
| default | sunflower | produce | 54 | 54 | 108 | 30.0000 | — |
| default | sunflower | hit | 4 | 4 | 8 | 30.0000 | — |
| default | sunflower | die | 4 | 4 | 8 | 30.0000 | — |
| default | peashooter | idle | 39 | 39 | 78 | 30.0000 | — |
| default | peashooter | attack | 39 | 39 | 78 | 30.0000 | — |
| default | peashooter | hit | 4 | 4 | 8 | 30.0000 | — |
| default | peashooter | die | 4 | 4 | 8 | 30.0000 | — |
| default | wallnut | idle | 24 | 24 | 60 | 24.0000 | — |
| default | wallnut | hit | 7 | 7 | 16 | 26.2500 | — |
| default | wallnut | die | 24 | 24 | 60 | 24.0000 | — |
| default | jalapeno | plant | 13 | 13 | 16 | 48.7500 | — |
| default | jalapeno | ignite | 24 | 24 | 60 | 24.0000 | — |
| default | jalapeno | hit | 7 | 7 | 16 | 26.2500 | — |
| default | jalapeno | die | 24 | 24 | 60 | 24.0000 | — |
| default | zombie_basic | walk | 88 | 87 | 198 | 26.3636 | — |
| default | zombie_basic | bite | 84 | 84 | 189 | 26.6667 | — |
| default | zombie_basic | hit | 4 | 4 | 8 | 30.0000 | — |
| default | zombie_basic | die | 37 | 37 | 90 | 24.6667 | — |
| dogs | sunflower | idle | 48 | 48 | 60 | 48.0000 | — |
| dogs | sunflower | produce | 24 | 24 | 48 | 30.0000 | — |
| dogs | sunflower | hit | 4 | 4 | 8 | 30.0000 | — |
| dogs | sunflower | die | 24 | 24 | 48 | 30.0000 | — |
| dogs | peashooter | idle | 48 | 48 | 60 | 48.0000 | — |
| dogs | peashooter | attack | 24 | 24 | 48 | 30.0000 | — |
| dogs | peashooter | hit | 4 | 4 | 8 | 30.0000 | — |
| dogs | peashooter | die | 24 | 24 | 48 | 30.0000 | — |
| dogs | wallnut | idle | 60 | 60 | 120 | 30.0000 | 38.76–63.92 |
| dogs | wallnut | hit | 28 | 28 | 28 | 60.0000 | 32.98–49.64 |
| dogs | wallnut | die | 59 | 59 | 59 | 60.0000 | 17.68–48.96 |
| dogs | jalapeno | plant | 40 | 40 | 80 | 30.0000 | 45.22–70.72 |
| dogs | jalapeno | ignite | 69 | 69 | 69 | 60.0000 | 29.24–51.34 |
| dogs | jalapeno | hit | 25 | 25 | 25 | 60.0000 | 41.14–55.08 |
| dogs | jalapeno | die | 29 | 29 | 29 | 60.0000 | 48.28–66.64 |
| dogs | zombie_basic | walk | 48 | 48 | 60 | 48.0000 | — |
| dogs | zombie_basic | bite | 24 | 24 | 60 | 24.0000 | — |
| dogs | zombie_basic | hit | 4 | 4 | 8 | 30.0000 | — |
| dogs | zombie_basic | die | 24 | 24 | 48 | 30.0000 | — |

## 固定关卡玩法回放基准

- 输入：tests/replay/test_base_replay.py中的strategy逐模拟tick执行；配置与关卡SHA-256记录在fixture。
- 结果：phase=won，tick=12011，sun=450，kills=12。
- 事件数：355；60 tick间隔全量Simulation snapshot数：201。
- 完整事件trace与每60 tick gameplay snapshots保存在 tests/replay/fixtures/004-baseline.json，可作为修改后精确回放对照。
