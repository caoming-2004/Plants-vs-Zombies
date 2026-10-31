# Contract: Windows 与 Android 平台文件隔离

## Purpose

约束双平台构建、清理、验收和交付的路径边界。此契约只规定文件所有权，不要求复制游戏规则或完全相同的素材。

## Directory Ownership

| 内容 | Windows 所有目录 | Android 所有目录 |
|---|---|---|
| 平台打包配置/入口 | `packaging/windows/` | `packaging/android/` |
| 编译临时文件/staging | `build/windows/` | `build/android/` |
| 最终可玩版本 | `dist/windows/` | `dist/android/` |
| 本 feature 验收证据 | `docs/validation/011/windows/` | `docs/validation/011/android/` |
| 用户数据、日志 | Windows 用户数据目录 | Android 应用私有目录 |

Common code/data stay authoritative in `src/pvz_game/` and `assets/`. Platform builders may read them, but may not write generated results into them.

## Build and Cleanup Rules

1. Windows build sets PyInstaller work output explicitly under `build/windows/` and final bundle under `dist/windows/`.
2. Android build pins its own p4a recipe/distribution/cache and app staging to Android-owned locations; the installable APK is copied only to `dist/android/`.
3. A Windows build/clean command MUST NOT enumerate, overwrite, move, or delete Android-owned files. The same restriction applies in reverse.
4. No command may clean the generic `build/` or `dist/` parent recursively. Cleanup targets must be validated descendants of the calling platform root.
5. Android toolchain/SDK and Python environment remain separate from Windows `.venv` and PyInstaller dependencies.
6. Temporary test EXE/APK/archive files are removed from their own platform test/staging directories after validation. The final Windows playable directory and final Android APK remain in their own release roots. No test ZIP is produced.

## Acceptance Procedure

1. Build both platforms and record relative paths plus SHA256 for all files in each release root.
2. Run Android-scoped cleanup and verify Windows release/configuration hashes are unchanged.
3. Run Windows-scoped cleanup and verify Android release/configuration hashes are unchanged.
4. Verify both packages load the shared game configuration and dog assets without modifying the shared sources.
