# 平台文件隔离检查

**结果：Windows 路径隔离通过；完整双端清理/哈希验收待 Android 构建环境。**（2026-10-30）

| 范围 | 路径 | 检查结果 |
|---|---|---|
| Windows 打包配置与入口 | `packaging/windows/` | 存在，独立 spec、build、launcher 和验证脚本 |
| Android 打包配置与入口 | `packaging/android/` | 存在，独立 p4a 配置、recipe、smoke 与 build 脚本 |
| Windows staging | `build/windows/` | 本轮临时 staging 已清除，目录为空 |
| Android staging/cache | `build/android/`、`.tools/android/` | 尚不存在；WSL 返回 `Wsl/Service/E_ACCESS_DENIED`，未运行 Android 构建/清理 |
| Windows 最终目录包 | `dist/windows/PvzMiniGame-v0.6.1/` | 存在，194 个文件，252,363,075 bytes |
| Android APK | `dist/android/` | 尚不存在；不得记作 APK 验收通过 |

## 关键 SHA256

- Windows 最终入口 `dist/windows/PvzMiniGame-v0.6.1/PvzMiniGame.exe`：`B50D7F2C6221155FAA7F0F943D6245D8A82D1338CA40F0303B8528139138DB1F`
- Windows builder `packaging/windows/build.ps1`：`6922F42C5766ED521CACECE5E278AC8F1A6C2BA14BEF032F84ACAE79818C3679`
- Android builder `packaging/android/build.sh`：`429BB1A9382AA2F023F2B197A8BEA03397EE84E96F9FD2A6031AAA3649280E05`
- Android p4a 配置 `packaging/android/app-config/.p4a`：`D4F90E63B8135D4BFD30597EAFF6DB73319207C5969AF4C1107F2ACCA4CF9138`
- Android pygame-ce recipe：`0BA28D094AEED1142980317B8A782ADADB690F56E29E8B4C424FF4383D99C68C`

Windows build 写入和清理仅使用 `build/windows/`、`.tools/windows/` 和 `dist/windows/`；本轮 Android 配置 SHA256 在 Windows staging 清理后采集，内容仍在 Android 专属目录。尚未生成 Android APK，也未执行 Android 专属清理，因此合同要求的双端对照哈希步骤不能标为完成。

## 清理

- 删除了本轮 Windows staging EXE、PyInstaller cache 和 smoke 工作目录；`dist/windows/` 最终 EXE 保留供游玩。
- 删除了遗留的独立测试/发行 ZIP `dist/PvzMiniGame-v0.5.0.zip`；`dist/` 下未留下独立发行 ZIP。最终程序 `_internal` 中的 `base_library.zip` 是运行时依赖，保留在最终目录包内。
- Android 尚未构建，故没有 Android 测试 APK 或 staging 需要删除。
