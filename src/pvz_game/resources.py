from pathlib import Path
import json
import logging
import traceback
from logging.handlers import RotatingFileHandler
import os


def asset_root():
    # PyInstaller datas are placed next to the package inside _internal.
    candidates = [Path(__file__).resolve().parent / "assets",
                  Path(__file__).resolve().parents[2] / "assets"]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise RuntimeError("缺少游戏资源，请完整解压压缩包并保留全部文件。")


def resource(relative):
    root = asset_root()
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise RuntimeError(f"游戏资源缺失：{relative}。请重新完整解压。")
    return path


def read_json(relative):
    try:
        return json.loads(resource(relative).read_text(encoding="utf-8-sig"))
    except (ValueError, OSError) as exc:
        raise RuntimeError(f"无法读取游戏配置：{relative}") from exc


def user_data_dir():
    """Writable per-user data root; never the read-only asset tree."""
    android_private = os.environ.get("ANDROID_PRIVATE")
    base = Path(android_private) if android_private else Path(os.environ.get("LOCALAPPDATA", Path.home()))
    return base / "PvzMiniGame"


def log_exception(message):
    """Record a traceback for a recoverable UI/result failure."""
    error_logger().error("%s\n%s", message, traceback.format_exc())


def error_logger():
    logger = logging.getLogger("pvz")
    if not logger.handlers:
        try:
            directory = user_data_dir() / "logs"
            directory.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(directory / "game.log", maxBytes=1024*1024,
                                          backupCount=2, encoding="utf-8")
            logger.addHandler(handler)
        except OSError:
            logger.addHandler(logging.NullHandler())
    return logger
