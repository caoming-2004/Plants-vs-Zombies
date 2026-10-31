"""High-resolution background catalog; presentation only, no gameplay."""
from pathlib import Path
import hashlib
import json
import pygame

from ..resources import asset_root
from ..config import LOGICAL_WIDTH, LOGICAL_HEIGHT

MIN_WIDTH = 2560
MIN_HEIGHT = 1440
DEFAULT_ID = "day"


class BackgroundError(RuntimeError):
    pass


class BackgroundCatalog:
    def __init__(self, root=None):
        self.root = Path(root) if root is not None else asset_root() / "backgrounds"
        self.manifest = None
        self.options = {}
        self.order = []
        self.default_id = DEFAULT_ID
        self.error = ""
        self._surfaces = {}
        self._thumbs = {}
        try:
            self._load()
            self.validate(check_files=True, check_hash=True)
        except (BackgroundError, OSError, ValueError, TypeError, pygame.error) as exc:
            self.error = str(exc)
            self.manifest = None
            self.options = {}
            self.order = []

    def _load(self):
        manifest_path = self.root / "manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if data.get("schema_version") != 1:
            raise BackgroundError("背景清单版本必须为1")
        default = data.get("default")
        options = data.get("options")
        if not isinstance(default, str) or not isinstance(options, list) or len(options) < 3:
            raise BackgroundError("背景清单必须包含至少三套背景")
        by_id = {}
        for item in options:
            if not isinstance(item, dict):
                raise BackgroundError("背景项必须为对象")
            required = ("id", "name", "file", "thumb", "width", "height", "theme", "source", "sha256", "license")
            if any(key not in item for key in required):
                raise BackgroundError("背景项字段缺失")
            if not isinstance(item["id"], str) or not item["id"] or item["id"] in by_id:
                raise BackgroundError("背景ID必须唯一")
            if item["theme"] not in ("day", "night", "dusk"):
                raise BackgroundError("背景主题必须为 day/night/dusk")
            if type(item["width"]) is not int or type(item["height"]) is not int:
                raise BackgroundError("背景尺寸必须为整数")
            if item["width"] < MIN_WIDTH or item["height"] < MIN_HEIGHT:
                raise BackgroundError("背景分辨率不足 2560x1440")
            by_id[item["id"]] = item
        if default not in by_id:
            raise BackgroundError("默认背景不存在")
        if not {"day", "night", "dusk"} <= {item["theme"] for item in by_id.values()}:
            raise BackgroundError("背景主题必须覆盖 day/night/dusk")
        self.manifest = data
        self.options = by_id
        self.order = [item["id"] for item in options]
        self.default_id = default

    def _path(self, relative):
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root.resolve()) or not path.is_file():
            raise BackgroundError("背景文件缺失")
        return path

    def validate(self, check_files=True, check_hash=True):
        if self.manifest is None:
            raise BackgroundError(self.error or "背景清单不可用")
        for item in self.options.values():
            if check_files:
                path = self._path(item["file"])
                self._path(item["thumb"])
                image = pygame.image.load(str(path))
                if image.get_size() != (item["width"], item["height"]):
                    raise BackgroundError("背景尺寸与清单不一致")
                if check_hash:
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    if digest != item["sha256"]:
                        raise BackgroundError("背景SHA-256不匹配")
        return True

    def _fallback_id(self):
        if self.default_id in self.options:
            return self.default_id
        return self.order[0] if self.order else None

    def resolve(self, background_id):
        if background_id in self.options:
            return background_id
        return self._fallback_id()

    def surface(self, background_id=None):
        chosen = self.resolve(background_id)
        if chosen is None:
            return None
        if chosen not in self._surfaces:
            item = self.options[chosen]
            try:
                image = pygame.image.load(str(self._path(item["file"])))
                if pygame.display.get_init() and pygame.display.get_surface() is not None:
                    image = image.convert()
                self._surfaces[chosen] = pygame.transform.smoothscale(
                    image, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
            except (BackgroundError, pygame.error):
                fallback = self._fallback_id()
                if fallback is None or fallback == chosen:
                    return None
                return self.surface(fallback)
        return self._surfaces[chosen]

    def thumbnail(self, background_id=None):
        chosen = self.resolve(background_id)
        if chosen is None:
            return None
        if chosen not in self._thumbs:
            item = self.options[chosen]
            try:
                image = pygame.image.load(str(self._path(item["thumb"])))
                if pygame.display.get_init() and pygame.display.get_surface() is not None:
                    image = image.convert()
                self._thumbs[chosen] = pygame.transform.smoothscale(image, (220, 124))
            except (BackgroundError, pygame.error):
                fallback = self._fallback_id()
                if fallback is None or fallback == chosen:
                    return None
                return self.thumbnail(fallback)
        return self._thumbs[chosen]
