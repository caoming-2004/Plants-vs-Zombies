# 006 第一版性能基线

## 基准版本与设备

- 基准提交：`7305e3d7fb751e41351aea9fcccd6352ee54b315`（历史第一版）。
- 目标设备：当前 Windows 11 x64 电脑；具体型号、Windows build、Pygame 显示驱动、刷新率与窗口尺寸在实测 JSON 写入。
- 比较窗口：1260×720；标准/压力场景各 60 秒；皮肤保持一致。
- 通过条件：新版标准场景平均循环帧率 ≥58 FPS 且 ≥第一版同条件值的 97%；standard P95≤18ms、pressure P95≤20ms；两场景最长连续 >33ms 帧数 <2。

## 历史性能证据

005 的 [`performance.md`](../005/performance.md) 有当前版本的打包性能样本（最终标准 62.42 FPS/P95 16.02ms，压力 62.40 FPS/P95 16.03ms），但不是 7305e3d 配对基线，不能作为第一版数据。第一版同机数据由 T004 重新测量并与其并列记录。

| 版本 | 场景 | 平均循环 FPS | P95 帧间隔 | >33ms 最长连续帧 | 窗口/刷新率 | 状态 |
|---|---|---:|---:|---:|---|---|
| 7305e3d | standard | 60.35 | 17.48ms | 1 | 1260×720 / 90Hz | BASELINE |
| 7305e3d | pressure | 59.99 | 17.54ms | 2 | 1260×720 / 90Hz | BASELINE |
| 005 最终包 | standard | 62.42 | 16.02ms | 未按 >33ms 口径记录 | 1260×720 / 报告记录 | 参考样本 |
| 005 最终包 | pressure | 62.40 | 16.03ms | 未按 >33ms 口径记录 | 1260×720 / 报告记录 | 参考样本 |

## 采样记录

基线包由 `.tools/feature-006-baseline/` 的 `7305e3d` 源码构建，测量于 2026-10-27 的同一 Windows 11 x64 显示窗口，Windows SDL 显示驱动、1260×720、90Hz、狗狗卡通皮肤。版本用其原有 `clock.tick(60)` 节奏；追加的 JSON 慢帧统计为纯诊断后处理。

- [基线标准场景完整 60 秒样本](baseline-standard.json)
- [基线压力场景完整 60 秒样本](baseline-pressure.json)
- 原始历史程序输出保留为 `baseline-standard-raw.json` 和 `baseline-pressure-raw.json`。
