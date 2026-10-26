# v0.2.0 历史狗狗外观验证基线

以下是 2026-10-26 的旧版验收记录，仅作历史基线；其中的黄黄豌豆射手映射、24姿势/秒要求和旧照片动作表不代表当前 005 功能。当前映射和验收状态见 `docs/art/dog-mapping.md` 与 `docs/validation/005/dogs.md`。

- 该次旧代码资源检查记录：五角色必需动作、2x像素清单、24个不同图像帧/秒及循环至少60 tick。
- 该次旧代码边界检查只检查横向相邻轮廓，不代表005要求的alpha≥96、双向邻格、25%主体遮挡率验证。
- 生成图预览：`docs/validation/animations/dogs-actions.png`；场景试玩预览：`docs/validation/final-play.png`；选肤菜单：`docs/validation/final-dog-menu.png`。
- NOT_RUN：旧版也未完成原型外形相似度、自然动作连续性最终目视确认及真实窗口拖动整局试玩。
