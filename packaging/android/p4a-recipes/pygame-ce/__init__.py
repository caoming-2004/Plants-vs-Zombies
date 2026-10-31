"""Private pygame-ce recipe adapted from python-for-android PR #2971."""

from os.path import join

import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import current_directory


class PygameCERecipe(CompiledComponentsPythonRecipe):
    version = "2.5.8"
    url = "https://github.com/pygame-community/pygame-ce/archive/{version}.tar.gz"
    name = "pygame-ce"
    site_packages_name = "pygame-ce"
    depends = ["sdl2", "sdl2_image", "sdl2_mixer", "sdl2_ttf", "setuptools", "jpeg", "png"]
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            setup_template = open(join("buildconfig", "Setup.Android.SDL2.in"), encoding="utf-8").read()
            env = self.get_recipe_env(arch)
            env["ANDROID_ROOT"] = join(self.ctx.ndk.sysroot, "usr")

            png = self.get_recipe("png", self.ctx)
            png_lib_dir = join(png.get_build_dir(arch.arch), ".libs")
            png_inc_dir = png.get_build_dir(arch.arch)

            jpeg = self.get_recipe("jpeg", self.ctx)
            jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)

            mixer_includes = ""
            mixer = self.get_recipe("sdl2_mixer", self.ctx)
            for include_dir in mixer.get_include_dirs(arch):
                mixer_includes += f"-I{include_dir} "

            setup_file = setup_template.format(
                sdl_includes=(
                    " -I" + join(self.ctx.bootstrap.build_dir, "jni", "SDL", "include")
                    + " -L" + join(self.ctx.bootstrap.build_dir, "libs", str(arch))
                    + " -L" + png_lib_dir
                    + " -L" + jpeg_lib_dir
                    + " -L" + arch.ndk_lib_dir_versioned
                ),
                sdl_ttf_includes="-I" + join(self.ctx.bootstrap.build_dir, "jni", "SDL2_ttf"),
                sdl_image_includes=(
                    "-I" + join(self.ctx.bootstrap.build_dir, "jni", "SDL2_image", "include")
                ),
                sdl_mixer_includes=mixer_includes,
                jpeg_includes="-I" + jpeg_inc_dir,
                png_includes="-I" + png_inc_dir,
                freetype_includes="",
            )
            with open("Setup", "w", encoding="utf-8") as setup:
                setup.write(setup_file)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env["USE_SDL2"] = "1"
        env["PYGAME_CROSS_COMPILE"] = "TRUE"
        env["PYGAME_ANDROID"] = "TRUE"
        return env

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        """Install the extensions already built by p4a without pip build isolation."""
        env = env or self.get_recipe_env(arch)
        install_dir = self.ctx.get_python_install_dir(arch.arch)
        record_file = join(self.get_build_dir(arch.arch), "android-install-record.txt")
        hostpython = sh.Command(self.hostpython_location)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                hostpython,
                "setup.py",
                "install",
                "--install-lib",
                install_dir,
                "--install-scripts",
                join(install_dir, "bin"),
                "--record",
                record_file,
                _env=env,
            )


recipe = PygameCERecipe()
