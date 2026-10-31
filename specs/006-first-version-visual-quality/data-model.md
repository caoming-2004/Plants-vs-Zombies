# Data Model: 视觉素材与实机验收

本功能不新增游戏领域实体、账号或数据库。以下是现有本地素材和本轮验收证据需要遵守的数据形状。

## Visual Asset Source

| Field | Type | Required | Meaning / Validation |
|---|---|---:|---|
| asset_id | string | yes | 稳定、唯一的本地来源清单键 |
| source_url | string | external assets | 可打开的原始作者/下载页面 |
| author | string | yes | 作者或“项目生成”；不得将平台误当作者 |
| license | string | yes | 页面实际许可标记与版本/条款 |
| file | relative path | yes | 仓库内最终源文件或派生文件 |
| sha256 | 64-char hex | yes | 文件内容校验哈希 |
| dimensions | integer pair | images | 原始及最终图像宽高，记录像素单位 |
| derivation | string | generated/adapted | 说明合成/处理方式，引用对应源素材 |
| attribution | string/null | yes | 必要署名或明确不要求署名 |

约束：最终静态背景源图为 2800×1200 或更高且维持第一版 7:3 画幅；任何外部来源都必须可追溯并允许当前项目分发。未经许可确认的候选不得进入默认清单或发行包。

## Appearance Clip (existing manifest concept)

| Field | Type | Meaning / Validation |
|---|---|---|
| skin_id | string | default、dogs 或 dogs_photo 等现有皮肤标识 |
| role | string | 玩法角色，如 peashooter、sunflower、wallnut、jalapeno |
| state | string | 必要动作状态，如 idle、attack、hit、die、produce、ignite |
| frame_rect | integer[4] | 图集中的合法 x/y/width/height |
| source_size | integer[2] | 去裁边前逻辑姿势画布尺寸 |
| trim_offset | integer[2] | 图集裁切相对逻辑姿势的位置 |
| anchor / muzzle / contact | number[2] | 落脚、发射、接触逻辑点；不得因清晰化漂移 |
| duration_ticks | integer | 正整数；既有 60Hz 动作节奏和时长保持 |
| source_frames | integer[] | 可选；记录用户动作表里派生帧对应的原帧 |

照片/卡通皮肤必须保留同一 role/state 语义与规则映射；卡通派生需能追溯到相同原始动作表和源帧。

## Performance Run

| Field | Type | Meaning / Validation |
|---|---|---|
| build_id / revision | string | 第一版提交或新版打包标识 |
| machine / OS | string | 实测设备和 Windows 版本 |
| display_refresh_hz | number/null | 当前显示器报告的刷新率；不可得时记 null 并注明 |
| window_size | integer[2] | 实际显示窗口像素尺寸 |
| scene / load | object | standard 或 pressure，明确对象数量 |
| duration_seconds | number | 每场景连续 60 秒 |
| frame_intervals_ms | number[] | 每次显示交换之间的单调时钟间隔，保持采样顺序 |
| average_fps / p95_frame_ms | number | 平均速率及 95 百分位画面间隔 |
| baseline_average_fps | number/null | 同机、同场景第一版配对基线平均循环帧率；未采得时为 null |
| average_fps_vs_baseline_pct | number/null | 新版平均循环帧率占第一版基线的百分比（100 表示持平） |
| over_33ms_frames | integer | 大于33ms的帧间隔总数 |
| longest_over_33ms_run | integer | 连续大于33ms的最长帧数 |
| action_feedback_samples | object[] | 操作类型、有效事件、首次可见画面延迟和结果 |
| missing / duplicate_actions | integer | 漏处理/重复处理数 |

P95 采用按间隔升序后的 ceil(0.95*n) 项；所有样本和测试环境一起保留。标准与压力目标见规格及 contracts/packaged-validation-report.md。

## Replay Comparison

| Field | Type | Meaning / Validation |
|---|---|---|
| baseline_revision / candidate_revision | string | 第一版与新版源码/发行标识 |
| input_sequence | string | 两个版本共同使用的确定性回放策略/输入文件 |
| events | object[] | 按顺序保存事件类型、tick 及必要参数 |
| final_state | object | 最终胜负阶段、tick、阳光、击杀数及割草机状态 |
| differences | object[] | 按事件/字段列出的差异；完全相同时为空 |

对照输出写入 docs/validation/006/replay.md；两版本都必须使用相同回放输入与字段归一规则。
