# Data Model: 波次 HUD、通关稳定性与高清背景

**Feature**: `013-wave-hud-error-backgrounds` | **Date**: 2026-10-31

本功能不改变 `Simulation` 快照或玩法实体；新增/扩展的数据集中在表现层布局、背景资源和本机设置。

## 1. HUD 状态条

**位置与尺寸**（逻辑像素，权威值放在 `presentation/scenes.py`）：

| 字段 | 值/规则 |
|---|---|
| 状态条矩形 | 约 `(160, 114, 680, 14)`，下边缘不超过 `grid_y - 8`（草坪起点 160） |
| 避让区 | 不与卡片底部（y≤109）、暂停按钮（x≥930）、铲子（774–849）、HUD 阳光框（15–150）重叠 |
| 内容 | 单行：关卡名 + 当前波次/出怪进度 + 下一波摘要 |
| 最大文本 | 状态条内宽 680；超出时单行截断/省略，不进入草坪 |

**渲染规则**：

- 状态条背景为半透明深色，文字用现有 CREAM/GOLD；对比度不依赖背景图。
- 波次公告不再使用 `(365,124,310,34)` 的浮动矩形；`wave_preview` 不再使用 `(650,166)` 的草坪内面板。
- 窗口缩放时按 1050×600 逻辑画布等比缩放，状态条仍位于草坪外。

## 2. BackgroundOption

| 字段 | 类型 | 规则 |
|---|---|---|
| `id` | string | 唯一、稳定，如 `day`/`night`/`dusk` |
| `name` | string | 中文显示名，非空 |
| `file` | string | 相对 `assets/backgrounds/` 的 PNG，存在 |
| `thumb` | string | 缩略图，存在 |
| `width`/`height` | int | 源图≥2560×1440、16:9 或足够裁切 |
| `theme` | string | `day`/`night`/`dusk` |
| `source` | string | 生成提示词或下载 URL |
| `author` | string | 摄影/渲染作者或生成者 |
| `sha256` | string | 文件校验 |
| `license` | string | 授权/使用说明（含署名要求） |

### BackgroundManifest

```json
{
  "schema_version": 1,
  "default": "day",
  "options": [
    {"id": "day", "name": "日间草坪", "file": "day.png", "thumb": "thumbs/day.png",
     "width": 2560, "height": 1440, "theme": "day",
     "source": "local image generation, 2026-10-31", "sha256": "...", "license": "project-local generated asset"}
  ]
}
```

**Validation**

- `schema_version=1`；`default` 必须存在于 `options`。
- 至少 3 个 option，id 唯一，theme 覆盖 day/night/dusk。
- 文件存在、可读、PNG；宽高≥2560×1440；清单 SHA-256 与文件匹配。
- 缩略图存在；所有路径不得越出 `assets/backgrounds/`。

## 3. ProgressFile（schema v2）

在现有 progress 结构上增加 `settings`：

```json
{
  "schema_version": 2,
  "unlocked": ["day_01", "day_02"],
  "levels": {"day_01": {"cleared": true, "best_stars": 2, "best_ticks": 9000}},
  "endless": {"unlocked": false, "best_wave": 0, "best_kills": 0},
  "settings": {"background_id": "day"}
}
```

**Rules**

- 旧 `schema_version=1` 读取时补 `settings.background_id=default`，保留 unlocked/levels/endless；下一次保存写 v2。
- `background_id` 必须是当前清单中的合法 id；未知/缺失回退 manifest default。
- 背景偏好与玩法进度同一文件保存，但不得改变关卡/星级/无尽数据。
- 保存失败只影响偏好/进度提示，不得导致结算崩溃。
- 背景偏好默认 `day`；外观选择仍不写入 progress。

## 4. ResultFlowState（内存）

| 字段 | 类型 | 说明 |
|---|---|---|
| `session_id` | int | 当前对局；用于防止重复结算 |
| `recorded_session` | int/null | 已写入进度的 session |
| `result_stars` | list[str] | 本次星级目标 id |
| `next_level_id` | str/null | 下一关 id；最后一关为 null |
| `result_error` | str/null | 结算/保存失败的可恢复提示 |
| `pending_action` | str/null | next/retry/menu/quit，处理中防止重复点击 |

**Transitions**

```text
playing --last zombie died--> won
won --record once--> progress.saved + result_stars + next_level_id
won --next--> day_02 playing (fresh state)
won --retry--> same level playing (fresh state)
won --menu--> menu
won --save/render error--> result_error shown; actions remain available
```

## 5. 背景渲染状态

| 字段 | 说明 |
|---|---|
| `background_id` | 当前选择 |
| `background_surface` | 已按 1050×600 预缩放/裁切的缓存 |
| `background_cache` | id → surface；最多 3–4 套 |
| `background_error` | 加载/切换错误提示 |

背景表面不进入 `snapshot`，不参与重放/模拟。

## 6. 关系

```text
BackgroundManifest 1 ── N BackgroundOption
ProgressFile 1 ── 1 settings.background_id
ProgressFile 1 ── N level records / endless record
Renderer 1 ── 1 current background_surface
ResultFlowState 1 ── 1 当前结算
```

## 7. 验证映射

| 数据/行为 | 定向检查 |
|---|---|
| HUD 不遮挡 | 双分辨率截图 + `test_hud_layout.py` 检查状态条矩形不与草坪矩形相交 |
| 第一关结算 | `tests/integration/test_result_flow.py`：20 次 next/retry/menu、只记录一次、损坏进度 |
| 背景清单/回退 | `tests/unit/test_backgrounds.py`：3 套、分辨率、SHA、未知 ID/缺失回退 |
| 偏好迁移 | schema v1→v2、非法 background_id 回退 |
| 性能 | 标准基准 + 背景切换截图 |
