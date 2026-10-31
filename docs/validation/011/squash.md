# 胖宝宝倭瓜规则验收

**结果：通过**（2026-10-30）

- `assets/config/balance.json` 已将胖宝宝改为 `squash`，使用独立的价格、冷却、攻击距离、重击时长和伤害字段，不含土豆雷埋地/武装参数。
- `tests/unit/test_new_plant_rules.py -k "squash or huanghuang"`：2 passed；`tests/unit/test_combat_and_lifecycle.py -k squash`：1 passed。
- 定向用例覆盖无目标待机、目标进入范围后蓄势并只命中一次、击中后消耗、重开清空植物状态，以及黄黄继续使用寒冰射手规则。
- `tests/integration/test_animation.py -k squash_attack_uses_dog_pose`：1 passed，确认倭瓜攻击姿态和击中反馈效果。
- `tools/validate_assets.py` 通过，胖宝宝的 attack 姿态映射有效。
