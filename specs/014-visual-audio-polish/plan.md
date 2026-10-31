# Implementation Plan: 字体、场景背景与游戏音乐优化

**Branch**: `014-visual-audio-polish` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-visual-audio-polish/spec.md`

## Summary

仅优化 Windows 桌面版的字体、场景背景和音乐，不改动核心玩法。复用现有 Pygame 渲染器、Noto Sans SC 字体、背景清单/选择器/本机偏好、`assets/` 随包机制和 Windows 目录包。通过改善逻辑画布到窗口的缩放质量、换用成熟写实的草坪战斗背景、增加可降级的音乐控制器及本机音乐设置，交付可直接运行的桌面目录包。

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: pygame-ce 2.5.x；不新增运行时依赖

**Storage**: Windows 用户本机 `%LOCALAPPDATA%/PvzMiniGame/progress.json`，沿用现有 `settings` 区域

**Testing**: 仅运行受影响的定向 pytest 检查、资产清单校验和最终 Windows 目录包冒烟；不运行全量测试

**Target Platform**: Windows 桌面版；Android 明确不在范围内

**Project Type**: 单体桌面游戏

**Performance Goals**: 标准对局保持既有 60 FPS 目标；文字缩放及音乐状态切换不得引入可感知卡顿或重复播放

**Constraints**: 离线运行；字体、背景和音频随 Windows 目录包交付；背景来源/许可可追溯；无录音授权时胜利音乐不得包含俊良或狗狗声音；音频设备不可用时游戏仍可玩

**Scale/Scope**: 单人本地游戏；主要菜单、设置、关卡选择、对局 HUD、提示、暂停及胜负界面；沿用 1050×600 逻辑画布和已有背景选择流程

## Constitution Check

| 原则 | 方案检查 | 状态 |
|---|---|---|
| I. 完整可玩的核心循环优先 | 只调整视听呈现，不改玩法；最终目录包仍需可启动并进入完整对局/结算流程 | PASS |
| II. 游戏规则与界面渲染分离 | 字体、背景与音乐逻辑属于 presentation；不新增游戏规则判定 | PASS |
| III. 关键数值集中管理 | 音量使用统一设置值及有界验证；不触碰玩法平衡数值 | PASS |
| IV. 核心玩法修改必须验证 | 不修改核心玩法；采用最少量渲染、资源、音乐状态与桌面包检查 | PASS |
| V. 新增功能保持已有功能可运行 | 背景选择和进度格式兼容；音乐/素材失败时可静音或回退，核心循环不受阻 | PASS |

## Project Structure

### Documentation (this feature)

```text
specs/014-visual-audio-polish/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── visual-audio-presentation.md
```

### Source Code (repository root)

```text
assets/
├── backgrounds/                 # 场景背景、缩略图、清单与来源记录
├── fonts/                       # 随包字体及许可证
└── music/                       # 桌面菜单/对局/胜利音乐与来源记录
src/pvz_game/
├── app.py                       # 初始化与场景切换时驱动音乐状态
├── progress.py                  # 音量/静音偏好持久化
├── presentation/
│   ├── backgrounds.py           # 复用背景清单、验证、缓存和回退
│   ├── prototype_renderer.py    # 字体资源和抗锯齿文本缓存
│   ├── renderer.py              # 背景/设置 UI 与最终显示缩放
│   └── audio.py                 # 新增轻量音乐状态控制；不持有玩法状态
└── resources.py                 # 复用资源定位与离线打包路径
tests/
├── unit/                        # 音乐设置/播放状态与背景/偏好定向检查
└── integration/                 # 背景画面、窗口呈现与最小桌面循环检查
packaging/windows/
└── pvz_game.spec                # 沿用 assets 随包打包
```

**Structure Decision**: 沿用现有单体 Python/Pygame 桌面架构，不拆分子项目。音乐控制器放在 presentation 层，通过 app 的场景状态调用；保存的偏好仍归 `Progress` 所有。背景继续由 `BackgroundCatalog` 管理，字体继续由 `PrototypeRenderer` 统一绘制。

## Complexity Tracking

无宪章例外；不新增运行时依赖。

## Phase 0: Research

已通过代码检查确认：

- 全局文字入口是 `src/pvz_game/presentation/prototype_renderer.py::Renderer.text`，当前使用 antialias 字形并缓存渲染表面；主应用在 `src/pvz_game/app.py` 将 1050×600 逻辑画布放大到窗口。
- 窗口最终合成目前采用普通整数缩放；优先在最终缩放环节改善边缘质量，并以标准窗口渲染性能作为唯一必要性能门槛，不把整个游戏重写为高分辨率画布。应用与性能基准必须共用相同的窗口缩放函数，确保测到的是实际交付路径。
- 背景目录 `src/pvz_game/presentation/backgrounds.py` 已负责 manifest、尺寸、哈希校验、缓存与默认项回退；`renderer.py` 和 `progress.py` 已提供背景选择及本机记忆。保留三个现有选择项，以成熟写实的单一新场景主素材生成相符的日间/夜间/黄昏版本，更新原选择项及缩略图和来源元数据。
- 当前默认已有 Noto Sans SC 和字体许可证；先核验窗口缩放链路及现有字号/粗体效果，再在该统一入口改进呈现，不替换中文字体或逐界面重复修补。
- 当前没有游戏音乐资产或音乐控制器。复用 pygame-ce 已有音频能力；添加本地随包音乐，不加入运行时网络下载或新的音频依赖。音乐 API/设备初始化失败须静音降级。
- 进度 `settings` 已独立容纳背景选择，读取兼容旧 schema v1/v2。新增音乐音量/开关作为兼容字段加入该设置区，保持旧存档默认可用，不改战役进度模型。
- 背景主素材使用本项目生成能力制作的成熟写实前院草坪/防守场景，避免沿用已明确不适合的低龄卡通图或只有泛草坪、与战斗空间无关的照片；记录生成说明及哈希，并复用本地构建器生成光照变体。音乐采用可随包分发且来源/许可明确的成熟、轻度紧张游戏配乐；没有用户提供或授权录音则不用俊良/狗狗声音。

## Phase 1: Design

- `data-model.md` 定义文字样式、背景条目、音乐状态与 `settings.music` 的最小字段及兼容规则。
- `contracts/visual-audio-presentation.md` 定义呈现和播放的场景切换、降级及离线资源契约。
- `quickstart.md` 只列资产校验、相关定向测试、固定 60 FPS 窗口性能测量、Windows 目录包构建与核心循环验收；性能基准调用与应用相同的窗口合成/缩放路径。

## Constitution Check (post-design)

设计继续维持上述 PASS：音乐状态与模拟分离，背景及音乐离线资源有回退，保存字段扩展不丢失关卡进度；最终进行一次桌面可玩包验收。测试范围限于新旧边界交界，不运行不相关的全量套件。
