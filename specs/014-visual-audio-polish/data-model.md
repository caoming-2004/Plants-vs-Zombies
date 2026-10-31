# Data Model: 视听呈现偏好

本功能不改变模拟/战役实体，仅扩展用户偏好并明确呈现资源记录。

## Text Style

| Attribute | Meaning | Validation |
|---|---|---|
| region | 菜单、HUD、卡片、提示、结算等呈现区域 | 使用既有区域；不引入玩法状态 |
| font_size | 逻辑画布字号 | 正数；沿用统一 renderer 尺寸层级 |
| antialias | 字形边缘抗锯齿状态 | 开启；缩放路径不得产生明显锯齿 |
| character_coverage | 中文、数字、标点覆盖 | 主要界面抽样字符均可显示 |

文字样式是 renderer 内部的呈现属性，不写入玩家存档。

## Background Asset

| Attribute | Meaning | Validation |
|---|---|---|
| id | 稳定选择标识 | 保留既有 `day`、`night`、`dusk` |
| theme | 日间/夜间/黄昏类别 | 属于三种既有主题之一 |
| file / thumb | 主图和菜单缩略图相对路径 | 文件存在且可解码 |
| width / height | 主图像素尺寸 | 满足既有至少 2560×1440 要求 |
| source / license | 来源或生成记录及授权 | 来源可复核；不明授权不得打包 |
| sha256 | 内容摘要 | 与实际文件匹配 |

## Music Preference

在当前 `progress.json` 的 `settings` 对象内扩展：

| Field | Type | Default | Validation |
|---|---|---|---|
| music_enabled | boolean | `true` | 严格布尔值；非法值恢复默认 |
| music_volume | number | `0.55` | 有限数且位于 0.0–1.0；非法值恢复默认 |

旧版缺少以上字段的存档继续有效，首次加载采用默认值。读取、写入或损坏回退不得覆盖已解锁关卡、星级或背景选择。

## Music Playback State

由音乐控制器在内存维护，不写入玩家进度：

| State | Meaning |
|---|---|
| disabled | 用户关闭音乐或音频设备不可用 |
| menu | 菜单循环曲目 |
| gameplay | 对局循环曲目 |
| paused | 暂停时停止/暂停对局曲目，恢复时续播 |
| victory_cue | 胜利事件触发的一次性提示 |
| stopped | 失败、退出或没有活动场景 |

相同状态重复更新不得重复启动同一轨；胜利 cue 对同一结算会话最多触发一次。

## Relationships

- 玩家偏好保存选定背景 ID 与音乐设置。
- BackgroundCatalog 使用 manifest 将背景 ID 映射到场景资源。
- 音乐播放状态由 app 当前场景和用户偏好决定；不向 Simulation 写入音频字段。
