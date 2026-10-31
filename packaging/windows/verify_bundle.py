"""Run one minimal smoke pass against a Windows directory release."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact-name', default='PvzMiniGame-v0.6.1')
    parser.add_argument('--screenshot', type=Path,
                        default=ROOT / 'docs/validation/011/windows/desktop-smoke.png')
    args = parser.parse_args()
    bundle = ROOT / 'dist' / 'windows' / args.artifact_name
    exe = bundle / 'PvzMiniGame.exe'
    if not exe.is_file():
        raise SystemExit(f'Missing Windows executable: {exe}')
    for name in ('开始游戏.txt', '字体许可.txt', '音乐来源.md'):
        if not (bundle / name).is_file():
            raise SystemExit(f'Missing release file: {name}')
    music_assets = bundle / '_internal' / 'pvz_game' / 'assets' / 'music'
    for name in ('menu.mp3', 'gameplay.mp3', 'victory.mp3', 'provenance.json'):
        if not (music_assets / name).is_file():
            raise SystemExit(f'Missing bundled music asset: {name}')

    args.screenshot = args.screenshot.resolve()
    args.screenshot.parent.mkdir(parents=True, exist_ok=True)
    work = ROOT / '.tools' / 'windows' / 'smoke-workdir'
    work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env['PATH'] = str(Path(env.get('SystemRoot', 'C:/Windows')) / 'System32')
    env.pop('PYTHONHOME', None)
    env.pop('PYTHONPATH', None)
    env['SDL_VIDEODRIVER'] = 'dummy'
    env['SDL_AUDIODRIVER'] = 'dummy'
    env['HTTP_PROXY'] = env['HTTPS_PROXY'] = 'http://127.0.0.1:9'
    result = subprocess.run(
        [str(exe), '--smoke-frames', '8', '--smoke-play', '--screenshot', str(args.screenshot)],
        cwd=work, env=env, timeout=40, check=False)
    if result.returncode or not args.screenshot.is_file():
        raise SystemExit(f'Windows directory smoke failed with exit code {result.returncode}')
    digest = hashlib.sha256(exe.read_bytes()).hexdigest()
    report = {
        'artifact': bundle.relative_to(ROOT).as_posix(),
        'exe_sha256': digest,
        'exit_code': result.returncode,
        'python_in_child_path': False,
        'smoke_frames': 8,
        'game_loop': 'headless smoke-play',
        'screenshot': args.screenshot.relative_to(ROOT).as_posix(),
        'limitations': ['Automated headless smoke is not real mouse gameplay or a physical device test.'],
    }
    output = ROOT / 'docs' / 'validation' / '014' / 'windows' / 'desktop-smoke.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))


if __name__ == '__main__':
    main()
