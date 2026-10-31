# Research Decisions

- **Decision**: 沿用三狗角色映射和双图集。**Rationale**: 现有导入脚本已有名称、角色、来源帧对应关系。**Alternative**: 新增角色系统会重复现有职责。
- **Decision**: 在导入与渲染缓存处处理图像成本。**Rationale**: `Skin.surface` 和动画缩放已有缓存，先测量首次加载再决定预热位置。**Alternative**: 改玩法 tick 或跳过动作帧会改变体验。
- **Decision**: 以站立高度和全姿态边界验收。**Rationale**: 趴卧、抬爪姿态天然高度不同。**Alternative**: 逐帧强制缩放易造成跳动。
- **Decision**: 精简为针对性校验和一局试玩。**Rationale**: 符合快速可玩目标及宪章的必要回归要求。**Alternative**: 重跑全部旧性能矩阵会拖慢交付。
