# Quickstart: 验收 011 狗狗修复与双平台版本

本流程只保留构建可玩版本必须的检查。不要运行全量 pytest、压力矩阵或重复打包矩阵。

## Prerequisites

- Windows：现有项目 `.venv/Scripts/python.exe`、pygame-ce、PyInstaller 环境。
- Android：独立的 Linux/WSL 环境、Android SDK/NDK、JDK 与锁定的 python-for-android 及 pygame-ce 私有 recipe；不要安装到 Windows `.venv`。
- 可将最终 APK 安装到用户指定的魅族 20。

## Focused Source Checks

只运行与新行为直接关联的现有/新增用例：

1. 被窝和嗷嗷嗷每个可用帧的边界、帧引用和尺寸。
2. `pangbaobao` 倭瓜配置、目标命中/消耗、无目标边界、重开状态；确认旧土豆雷机制不再匹配胖宝宝。
3. Android 主触点归一化、连续移动、松手最近格、占格拒绝和触摸/合成鼠标去重。
4. 一次共用核心循环回归：进入游戏、种植、战斗、胜负及重开。

额外只运行一次现有 `tools/validate_assets.py`。有失败时修复直接关联的错误，不将无关测试模块一并展开。

## Android Compatibility Build and Device Run

1. 在 Android 专属环境先构建一个最小 SDL2/pygame-ce 2.5.8 APK，检查 ARM64 库、资源根和触摸事件是否可用。
2. 最小 APK 成功后构建一次正式 APK 到 `dist/android/`；保存构建日志和哈希到 `docs/validation/011/android/`。
3. 在魅族 20 侧载安装并离线启动。横屏完成触屏菜单、放置、收集资源、暂停/恢复、倭瓜攻击、结局和重新开始；连续观察约 10 秒植物动作约 12 帧/秒。
4. 删除 Android 专属临时 staging 与临时 APK，只保留最后交付的 APK。

Android 实际环境由 `packaging/android/` 配置指定。SDK、NDK 和 p4a storage/cache 使用 Android 专属路径；不得执行对共享 Windows 目录或 Windows `.venv` 的清理。

## Windows Build and Run

1. 在 Windows `.venv` 中运行与素材、倭瓜、共享游戏流程直接相关的定向测试。
2. 用 `packaging/windows/` 的构建入口仅生成一次正式 Windows 目录版到 `dist/windows/`；PyInstaller staging 限定为 `build/windows/`，不生成测试 ZIP。
3. 从 `dist/windows/` 启动一次，确认完整对局流程与素材加载；记录启动结果和哈希到 `docs/validation/011/windows/`。
4. 删除 Windows 专属 staging 和临时验证文件，保留最终 Windows 目录版。

## Cross-Platform Isolation Check

分别记录 `dist/windows/`、`dist/android/` 的相对路径和 SHA256；先做 Windows 专属清理，再做 Android 专属清理。每一步结束后，另一平台的配置与最终发行文件必须保持原路径及原哈希。禁止对 `build/`、`dist/` 根目录进行递归清理。
