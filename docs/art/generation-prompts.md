# 门头沟小狗动画素材生成记录

当前使用内置 imagegen 生成原创卡通帧，按 6 列×4 行、每格256×256像素保存；源表和 SHA256 记录见 `assets/skins/dogs/source/` 与 `assets/skins/dogs/provenance.json`。导入器只保留每格主体连通轮廓、统一脚底锚点，并以 2x 源像素进入图集。每个动作循环有至少24张不同可见图像/秒；循环时长至少60 tick。

## 原型特征

- **被窝**：阿拉斯加卡通体型、浅色厚毛、金围巾；坐姿呼吸、产阳光抬爪、受击和趴下。项目保留已有公开封面/犬种线索，但不把生成帧称作照片复刻。
- **黄黄**：按用户映射制作黄黄角色，绿背心；向右待机与短吠射击。现有公开搜索仅足以确认“黄黄”是骏良的狗，未找到可验证的花色特写，因此采用黄色短毛犬的原创卡通解释。
- **小宝**：坚果墙角色，体型敦实、低重心、稳定挡咬；官方公开视频/帖子只给出大体型等线索，未据此断言具体毛色。
- **小杜**：火爆辣椒角色，短毛、宽头比特犬体态；表现点燃、整行火焰、受击与消散。
- **嗷嗷嗷**：比格特征、长垂耳和三色面部斑纹，红背心标明进攻阵营；向左行走和原地啃咬。

## 提示词共同约束

```text
Create a transparent-background 2D game sprite sheet featuring the named Mentougou dog as a friendly, recognizable cartoon interpretation. Preserve the dog identity cues described for this role, coat markings and proportions consistently across every cell. EXACT 6 columns by 4 rows, 1536x1024 canvas, each cell 256x256. One complete dog per cell, no text, borders, grid lines, humans, background props or neighboring-cell fragments. Fixed paw baseline, same camera and scale. Rows: 12 distinct idle poses; 6 articulated role-action poses; 6 distinct recovery/defeat poses. Clear continuous paw, head, ear and tail motion. Do not replace actions with whole-image shaking.
```

上游身份线索链接及用户确认见 `dog-mapping.md`；具体角色是否与真实个体相似仍需用户/维护者看图验收。
