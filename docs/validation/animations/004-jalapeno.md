# US2 验收：小杜清行动画

- `dogs/jalapeno/ignite` 使用源姿势 10–44，共 35 帧；无插值帧，引用顺序与源帧一一对应。
- 总时长：120 tick；60 tick/s；姿势率 17.5/s；名义时长 2.0 秒。
- 清行规则由 Simulation 在种植成功时结算一次。Animator 仅消费 `row_clear_started` 绘制特效，120 tick 后移除，不延迟规则推进。
- 自动验证：`tests/integration/test_jalapeno_row_clear.py` 覆盖 35 帧顺序、效果持续、单次清除、规则继续、暂停 tick 冻结和 session 重开清理。
- 素材验证：`tools/validate_assets.py` 检查精确帧数、源帧顺序、时长、17.5/s，以及其他 clip 的 12–18/s 门槛。

2026-10-26，Windows，项目 Python 3.12 环境：通过。
