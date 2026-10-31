# 素材与界面核对

结果：通过。`tools/validate_assets.py` 对经典、狗狗、狗狗照片三套资源完成清单与动作检查；狗狗皮肤增加的两个角色也在 `Skin` 的狗狗专属必需角色校验中。

被窝、嗷嗷嗷、胖宝宝、黄黄分别映射到 `sunflower`、`zombie_basic`、`pangbaobao`、`huanghuang`，原始 PNG 的哈希和导入姿态映射见 [素材接入记录](source-intake.md)。alpha 连接主体提取移除透明背景杂点，四张源图均不覆盖。

六张卡只在狗狗外观显示，新增角色不出现在经典外观或 `dogs_photo`；经典与照片版保留四张卡。六卡布局未改草坪种植区坐标。HUD 与地图图像已在实际打包截图中复核：[正式包烟测画面](release-smoke.png)。卡片、图鉴及地图展示的新角色身份与姿态完整。

素材校验覆盖 538 个经典、359 个狗狗、316 个照片皮肤动作帧引用；状态见 `tools/validate_assets.py` 输出。
