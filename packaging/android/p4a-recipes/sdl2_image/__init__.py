"""SDL2_image recipe for this PNG/JPEG-only Android game.

python-for-android's stock recipe recursively clones every optional codec,
including libjxl's skcms submodule. Android.mk's built-in stb backend supports
the PNG/JPEG assets used by this game, so no optional codec source is needed.
"""

import os

from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL2Image(BootstrapNDKRecipe):
    version = "2.8.2"
    url = (
        "https://github.com/libsdl-org/SDL_image/releases/download/"
        "release-{version}/SDL2_image-{version}.tar.gz"
    )
    dir_name = "SDL2_image"

    def get_include_dirs(self, arch):
        return [os.path.join(self.ctx.bootstrap.build_dir, "jni", "SDL2_image", "include")]


recipe = LibSDL2Image()
