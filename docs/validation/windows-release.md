# Windows发行验收

## 当前构建信息

- 目标：Windows 10/11 x64，标准用户、断网、无Python环境。
- 开发机：Windows 11 x64（10.0.26200），Python 3.12.15；不代表Windows 10或干净用户环境。
- ZIP：`dist/PvzMiniGame-windows-x64.zip`，38,013,063 bytes。
- SHA256：`c767ac9f4e18e175b300f454a2e48271012f47e2dd77cb02e51ec32d0495090d`

## 验收状态

| 检查 | 状态 | 说明 |
|---|---|---|
| Windows 11真实窗口双击启动 | NOT_RUN | SDL dummy或源码启动不等同干净环境实机验收 |
| Windows 10 x64启动 | NOT_RUN | 未在Windows 10设备执行 |
| 标准用户、断网、无Python | NOT_RUN | 未在干净系统环境执行 |
| 中文/空格目录解压并整体移动 | NOT_RUN | 未完成真实Windows窗口移动后启动 |
| 缺失/损坏资源中文提示 | NOT_RUN | 需在发行包实机验证 |
| ZIP结构、移动至中文空格目录及四种皮肤组合headless smoke | PASS | `docs/validation/bundle-smoke.json`；`python_in_child_path=false`，四种组合exit code均为0 |

代理指向不可达本机端口，仅为避免测试时访问网络的保护措施，不等同于系统级断网；
SDL dummy无窗口截图不等同于双击或真实鼠标试玩。T061因此保持未完成，不以此冒充离线Windows实机验收。
