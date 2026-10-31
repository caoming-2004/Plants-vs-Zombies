# 013 高清背景验证

日期：2026-10-31

## 结果

| 检查 | 结果 | 证据 |
|---|---|---|
| 三套 day/night/dusk | PASS | `assets/backgrounds/manifest.json`；3 options |
| 源图 2560×1440 | PASS | day 2560×1440 / night 2560×1440 / dusk 2560×1440 |
| 文件/SHA/尺寸校验 | PASS | `tools/validate_assets.py`：backgrounds valid, 3 options, default day |
| 主菜单选择页 | PASS | [backgrounds.png](backgrounds.png)；三张缩略图、名称、当前标记 |
| 立即应用/保存 | PASS | `Progress.set_background` + `progress.save`；`test_progress_v1_migrates_background_setting` |
| 重启恢复/未知 ID 回退 | PASS | `BackgroundCatalog.resolve` 回退 default；进度迁移测试 |
| 缺失文件回退 | PASS | `test_missing_background_manifest_is_reported` |
| 角色/HUD 可读 | PASS（视觉） | [hud-1920.png](hud-1920.png)；[exe-play.png](exe-play.png) |
| 标准场景性能 | PASS（dummy 10s） | [benchmark.json](benchmark.json)：61.4 fps，p95 16.01 ms；状态 INCONCLUSIVE（无历史基线） |
| 运行期离线 | PASS（代码路径） | 运行时只读本地 manifest/PNG，无网络调用；未做抓包 |

## 素材

- 来源：Wikimedia Commons, “Mona-lawn-dusk-Panorama1.jpg”
- 作者：Wiki ian
- 授权：CC BY-SA 3.0；必须署名
- 派生：裁切 16:9 + 日间/黄昏/夜间色彩分级
- 记录：`assets/backgrounds/source/provenance.json`、manifest 的 author/source/license/sha256

风格：真实感建筑与草坪摄影，不是卡通/低龄插画；符合“高清、高大上、不幼稚”的要求。

## 未执行

- 未用真实鼠标逐一切换三套背景并重启 exe；自动测试覆盖清单/偏好/回退，选择页与游戏内截图已人工查看。
- 未做真实显示驱动 60 秒性能基线；当前 61.4 fps 仅作 dummy 快速验证。
