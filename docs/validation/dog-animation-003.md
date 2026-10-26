# 小宝/小杜动画验证（003）

日期：2026-10-26。角色素材接收和帧映射详见[`dog-source-intake.md`](dog-source-intake.md)。

## 自动检查

- `tools/import_dog_assets.py`：成功，生成dogs图集/manifest/provenance；五角色共610个引用帧。
- `tools/validate_assets.py`：PASS。default 538、dogs 610引用帧；必需动作姿势速率≥24个不同可见帧/秒，循环clip≥60模拟tick；manifest、来源和狗狗邻格诊断通过。
- `tests/integration/test_asset_manifest.py`：加入源帧到动作clip映射、两个原图SHA-256来源记录、缺帧/清单字段既有校验。完整测试结果记录在`feature-003-regression.md`。
- 小宝/小杜全60个源帧都被clip引用；插值帧记录相邻源索引，不复制源姿势凑帧。

## 视觉检查

- 预览导出：[`animations/003/dogs-actions.png`](animations/003/dogs-actions.png)
- 小宝/小杜动作抽样：[`animations/003-user-pose-samples.png`](animations/003-user-pose-samples.png)
- PASS：坚果墙映射为小宝、火爆辣椒映射为小杜；朝向保持向右；喷火动作来自小杜的喷火帧；站立与卧倒脚底统一到同一锚点；裁剪后未看到相邻格的其他狗狗进入角色轮廓。
- 插值使用alpha混合相邻姿势；循环边界不做跨循环混合，避免不同动作姿势叠影。
- NOT_RUN：标准窗口中逐个触发全部受击/死亡状态的人工试玩。自动清单/帧率检查通过不能替代这些状态的实机目视验收。
