"""Cut the twelve supplied poses from their printed 4x3 sheets.

Run with the workstation Python that provides OpenCV; the game has no OpenCV
runtime dependency.  The original user files are preserved unchanged.
"""
from pathlib import Path
import shutil
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/skins/dogs/source'


def cut_sheet(source: Path, target: Path) -> None:
    sheet = cv2.imdecode(np.frombuffer(source.read_bytes(), np.uint8), cv2.IMREAD_COLOR)
    if sheet is None or sheet.shape[:2] != (1086, 1448):
        raise ValueError(f'{source.name}: expected a 1448x1086 sheet')
    result = np.zeros((1086, 1448, 4), np.uint8)
    for row in range(3):
        for col in range(4):
            x, y = col * 362, row * 362
            tile = sheet[y:y+362, x:x+362]
            hsv = cv2.cvtColor(tile, cv2.COLOR_BGR2HSV)
            mask = np.full(tile.shape[:2], cv2.GC_PR_BGD, np.uint8)
            mask[:5] = mask[-5:] = cv2.GC_BGD
            mask[:, :5] = mask[:, -5:] = cv2.GC_BGD
            dark = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY) < 115
            colored = (hsv[:, :, 1] > 55) & (hsv[:, :, 2] < 245)
            mask[dark | colored] = cv2.GC_PR_FGD
            mask[dark & colored] = cv2.GC_FGD
            cv2.grabCut(tile, mask, None, np.zeros((1, 65), np.float64),
                        np.zeros((1, 65), np.float64), 3, cv2.GC_INIT_WITH_MASK)
            alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
            count, labels, stats, _ = cv2.connectedComponentsWithStats(alpha)
            if count < 2:
                raise ValueError(f'{source.name}: empty pose {row*4+col}')
            body = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            alpha = np.where(labels == body, 255, 0).astype(np.uint8)
            alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
            result[y:y+362, x:x+362, :3] = tile
            result[y:y+362, x:x+362, 3] = alpha
    if not cv2.imwrite(str(target), result):
        raise OSError(target)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for label, stem in [('小宝', 'xiaobao'), ('小杜', 'xiaodu'), ('好孩子', 'haohazi')]:
        original=ROOT / f'{label}.png'
        shutil.copy2(original, OUT / f'{stem}-original-007.png')
        cut_sheet(original, OUT / f'{stem}-user-007.png')
