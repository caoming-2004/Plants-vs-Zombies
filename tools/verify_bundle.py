"""Run only the packaged exe after relocation, with no Python in PATH."""
from pathlib import Path
import os
import shutil
import subprocess
import json
import hashlib
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    archive=ROOT/'dist/PvzMiniGame-windows-x64.zip'
    destination=ROOT/'.tools/试玩 目录检查 v0.2.0'
    destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        for name in bundle.namelist():
            resolved=(destination/name).resolve()
            if not resolved.is_relative_to(destination.resolve()):raise ValueError('Unsafe zip path')
        bundle.extractall(destination)
    game=destination/'PvzMiniGame-v0.2.0'
    for name in ('开始游戏.txt','字体许可.txt','PvzMiniGame.exe'):
        if not (game/name).is_file():raise ValueError('Missing bundled file '+name)
    env=dict(os.environ)
    env['PATH']=str(Path(env.get('SystemRoot','C:/Windows'))/'System32')
    env.pop('PYTHONHOME',None);env.pop('PYTHONPATH',None)
    env['SDL_VIDEODRIVER']='dummy'
    env['SDL_AUDIODRIVER']='dummy'
    env['HTTP_PROXY']=env['HTTPS_PROXY']='http://127.0.0.1:9'
    cwd=destination/'不同 工作目录';cwd.mkdir(exist_ok=True)
    records=[]
    for plant,zombie in [('default','default'),('dogs','default'),('default','dogs'),('dogs','dogs')]:
        output=ROOT/'docs/validation'/f'bundle-{plant}-{zombie}.png'
        process=subprocess.run([str(game/'PvzMiniGame.exe'),'--smoke-frames','8','--smoke-play',
                                '--plant-skin',plant,'--zombie-skin',zombie,'--screenshot',str(output)],
                               cwd=cwd,env=env,timeout=40)
        if process.returncode!=0 or not output.is_file():raise RuntimeError('Bundle smoke failed')
        records.append(dict(plant=plant,zombie=zombie,exit_code=process.returncode,screenshot=output.name))
    menu_output=ROOT/'docs/validation/bundle-dog-menu.png'
    menu=subprocess.run([str(game/'PvzMiniGame.exe'),'--smoke-frames','2','--smoke-skins',
                         '--plant-skin','dogs','--zombie-skin','dogs','--screenshot',str(menu_output)],
                        cwd=cwd,env=env,timeout=40)
    if menu.returncode!=0 or not menu_output.is_file():raise RuntimeError('Dog appearance menu smoke failed')
    records.append(dict(plant='dogs',zombie='dogs',scene='skin_menu',exit_code=menu.returncode,screenshot=menu_output.name))
    report=dict(sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                platform=os.name,python_in_child_path=False,proxy_points_to_unreachable_local_port=True,
                caveat='Not an OS-level network block or a clean VM; headless SDL smoke, not mouse gameplay',
                relocated_directory=destination.relative_to(ROOT).as_posix(),combinations=records)
    (ROOT/'docs/validation/bundle-smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=True))


if __name__=='__main__':main()
