# 005 背景验收

## 资产

- 原创背景由 `tools/generate_background.py` 本地确定性生成，源图为 2800×1200 PNG。
- 来源、许可、哈希和改编方式写入 `assets/sources.json` 的 `generated-background-005`。
- `default/manifest.json` 的 `ui.background` 指向本地 `ui-background.jpg`；无需网络。
- 游戏逻辑画布仍为 1050×600，网格仍为原点 (105,160)、12×5 格、每格 72×76。测试覆盖 1050×600、1260×720 和 1920×1080 下的鼠标格位换算。

## 结果

- 自动化布局/输入测试已加入 `tests/integration/test_background_layout.py`；最终重跑待完成。
- 本轮没有保存新旧游戏窗口对照截图，也没有完成目视的房屋边缘、草坪格线、道路纹理和角色对比度验收。
- 不将源图预览或 SDL dummy 窗口截图当作真实显示窗口验收。
