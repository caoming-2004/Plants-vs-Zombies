from pathlib import Path
import os

root = Path(SPECPATH).parent
diagnostic = os.environ.get("PVZ_DIAGNOSTIC") == "1"
a = Analysis([str(root / "packaging" / "launcher.py")],
             pathex=[str(root / "src")],
             binaries=[], datas=[(str(root / "assets"), "pvz_game/assets")],
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=["numpy", "tkinter", "matplotlib"], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
          name="PvzMiniGame", debug=False, bootloader_ignore_signals=False,
          strip=False, upx=False, console=diagnostic, disable_windowed_traceback=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="PvzMiniGame-v0.2.0")
