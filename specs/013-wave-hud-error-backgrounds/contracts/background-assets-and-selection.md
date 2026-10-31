# Contract: 高清背景资源与选择

**Feature**: `013-wave-hud-error-backgrounds` | **Date**: 2026-10-31

## 资源

- 目录：`assets/backgrounds/`，独立于植物皮肤。
- 三套：day/night/dusk；源图至少 2560×1440，PNG；必须是真实感/高级感摄影或写实渲染，不得幼稚卡通。
- 每套含缩略图、manifest 元数据、作者/来源/授权、SHA-256。
- 运行时不访问网络；Windows 包递归包含该目录。

## manifest

```json
{
  "schema_version": 1,
  "default": "day",
  "options": [
    {"id": "day", "name": "日间草坪", "file": "day.png", "thumb": "thumbs/day.png",
     "width": 2560, "height": 1440, "theme": "day",
     "source": "licensed photo URL", "author": "author", "sha256": "...",
     "license": "CC BY-SA 3.0; attribution required"}
  ]
}
```

校验：default 存在；至少 3 个唯一 id；theme 覆盖 day/night/dusk；文件存在且尺寸达标；SHA 匹配；路径不越界。

## 选择与保存

- 主菜单“更换背景”打开选择页：三张缩略图、名称、当前标记、返回。
- 点击已存在背景立即应用；下一个绘制帧使用新背景。
- 选择写入 `progress.json` 的 `settings.background_id`；schema v1→v2 迁移。
- 旧存档缺失设置 → default；未知 id/文件缺失/损坏 → default；显示提示但不阻断。
- 外观选择仍 session-only；背景和外观独立。

## 渲染

- 首次使用/切换时把源图按 1050×600 预缩放/裁切并缓存；不在每帧缩放 2560×1440。
- 背景只替换草坪底图；`grid_x/grid_y/cell_width/cell_height`、HUD、角色、点击区域不变。
- 夜间/黄昏需保证僵尸、植物、阳光和 HUD 文字对比度；必要时在表现层加轻量暗角/亮度层，但不改变玩法。
- 三套背景缓存最多 3–4 个 surface；切换失败回退当前可用背景。

## 验收

1. `tools/validate_assets.py` 校验三套文件/分辨率/清单；缺文件/低分辨率/错 SHA 应失败。
2. 主菜单切换日间/夜间/黄昏各一次：立即生效、截图清晰、HUD/角色可读。
3. 重启后恢复到上次选择；移除当前背景文件后启动回退默认并提示。
4. 标准场景基准无性能回退；运行期无网络请求。
