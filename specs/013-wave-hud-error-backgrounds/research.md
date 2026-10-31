# Research: 波次 HUD、通关稳定性与高清背景

**Feature**: `013-wave-hud-error-backgrounds` | **Date**: 2026-10-31

本文件记录 Phase 0 决策。规格中的 4 个澄清问题已解决；不引入新运行时依赖。

## 1. HUD 状态条位置

- **Decision**: 在现有顶部 HUD 下、草坪上边界（y=160）之上建立单行固定状态条（约 y=114–128），统一显示关卡名、当前波次/出怪进度和下一波预告；移除当前位于 `(650,166)` 的预告面板和覆盖草坪的浮动波次公告。
- **Rationale**: 用户已选择顶部 HUD；当前预告面板 y=166 直接压在第 1 行，浮动公告也占用草坪上缘。固定条在草坪矩形之外，窗口缩放由现有画布等比缩放统一处理。
- **Alternatives considered**: 底部提示栏（已有操作提示，拥挤）；右上角紧凑面板（长波次名/预告容易溢出）；继续缩小浮动文字（仍覆盖地图）。

## 2. 第一关结算报错

- **Decision**: 先建立可重复的真实/无头 harness（清空第一关→结算→下一关/重试/返回/退出），捕获完整 traceback；在 `app` 结果/进度边界增加详细日志、单次结算标记和可恢复错误提示；修复根因后，用 20 次连续流程作为门槛。
- **Rationale**: 用户未提供具体错误文本。当前程序顶层只记录异常类型，无法定位；直接猜修风险高。harness 能覆盖真实结果状态、progress 保存、day_02 加载和结算渲染。
- **Alternatives considered**: 直接加 try/except 吞掉异常（会掩盖问题）；只根据代码猜测根因（可能修错）；要求用户提供日志（可并行，但不应阻塞方案）。

## 3. 背景资源与生成

- **Decision**: 新建 `assets/backgrounds/`，以授权的真实感/高级感摄影或写实渲染为基础，提供日间、夜间、黄昏三套至少 2560×1440 的 PNG，加缩略图和 `manifest.json`；开发阶段允许联网检索授权照片或本地生成，不使用幼稚卡通/低龄插画，最终随 Windows 包离线提供。每套记录作者、来源 URL、日期、SHA-256、授权和派生方式。
- **Rationale**: 用户明确允许联网/生图；独立目录避免与 `skins/default` 的 UI 图集耦合；2560×1440 在 1920×1080 下保留细节，1050×600 预缩放后不模糊。运行期离线符合现有游戏约束。
- **Alternatives considered**: 直接放大现有 2800×1200 背景（细节不足）；运行时在线下载（离线不可用、失败/授权风险）；把背景塞进 default atlas（资源耦合、切换困难）。

## 4. 背景渲染

- **Decision**: 启动/首次选择时把每套背景按 1050×600 逻辑画布预缩放/裁切并缓存；`Renderer.background()` 只替换底图，HUD、草坪格、角色和点击区域保持原逻辑。三套背景按需加载，切换只切换缓存表面。
- **Rationale**: 避免每帧对大图缩放；保持现有 1050×600 坐标和点击区域；夜间/黄昏可在图像层控制对比度，不改 UI 布局。
- **Alternatives considered**: 每帧缩放/裁切 2560×1440（性能风险）；把背景做成动态视差（超出范围）；改变关卡格尺寸（违反规则）。

## 5. 背景选择与持久化

- **Decision**: 在主菜单新增“更换背景”入口和背景选择页，显示三张缩略图/名称/当前标记；选择立即应用。背景偏好写入 `progress.json` 的 `settings.background_id`，progress schema 升到 2，旧 v1 自动补 `settings.background_id=day`，不改变已解锁/星级/无尽记录。
- **Rationale**: 用户已确认本机保存；复用现有 Progress 文件避免第二个可写文件；schema 迁移可保持旧存档。背景只改视觉，不需要进入 Simulation。
- **Alternatives considered**: 单独 preferences.json（多一个文件和错误面）；session-only（用户明确要保留）；放进外观选择（外观是 session-only，语义不同）。

## 6. 背景清单与回退

- **Decision**: `assets/backgrounds/manifest.json` 声明 `schema_version`、`default`、`options[]`（id/name/file/thumb/width/height/theme/source/sha256/license）。加载时校验 id 唯一、默认存在、文件存在、分辨率≥2560×1440；未知/缺失/损坏背景回退 default 并提示。
- **Rationale**: 数据驱动便于增加背景；清单校验可在 `tools/validate_assets.py` 和 Windows 构建前拦截坏资源。
- **Alternatives considered**: 硬编码路径（难扩展/难校验）；仅依赖文件存在（无法检查分辨率/授权）。

## 7. 菜单与输入兼容

- **Decision**: `scenes.BUTTONS` 增加背景菜单/缩略图/返回键；`input.click` 增加 `view="backgrounds"` 分支和默认参数；`Renderer.menu` 增加背景页。旧调用不带新参数时行为不变。
- **Rationale**: 复用现有 `button/rounded/text` 和点击处理；不引入 UI 框架；现有测试/基准调用不需要改。
- **Alternatives considered**: 新 UI 窗口/独立页面（超出范围）；把背景选择塞进外观菜单（用户需要独立入口）。

## 8. 最小验证

- **Decision**: HUD 双分辨率截图；第一关 20 次结算 harness + 一次真实窗口试玩；三套背景切换/重启/损坏回退截图；一次标准基准；少量定向 pytest。不跑全量、安卓、外观矩阵或长时压力。
- **Rationale**: 用户要求快速可玩；风险集中在 HUD 安全区、结果流程、背景清单/大图缓存和偏好迁移，定向检查足够。
- **Alternatives considered**: 全量回归/多设备矩阵（成本过高）；只靠人工看一眼（无法覆盖结算重复/损坏存档）。

## 开放问题

无未决澄清项。第一关报错的具体异常文本仍需在实施时通过 harness/日志确认，但验收目标和修复边界已明确。
