
from pythonforandroid.toolchain import Recipe, shprint, ArchAndroid, current_directory, debug, info, ensure_dir
from os.path import exists, join
import sh
import glob

class AwesomecnnRecipe(Recipe):
    name = 'awesomecnn'
    version = '0.28'
    url = 'https://github.com/radiodee1/awesome-cnn/archive/v{version}.zip'
    depends = ['python2', 'numpy', 'pyjnius']
    conflicts = []

    def get_recipe_env(self, arch):
        #env = super(PygameRecipe, self).get_recipe_env(arch)
        #env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
        #    self.ctx.get_libs_dir(arch.arch))
        #env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        #env['LIBLINK'] = 'NOTNONE'
        #env['NDKPLATFORM'] = self.ctx.ndk_platform

        # Every recipe uses its own liblink path, object files are collected and biglinked later
        #liblink_path = join(self.get_build_container_dir(arch.arch), 'objects_{}'.format(self.name))
        #env['LIBLINK_PATH'] = liblink_path
        #ensure_dir(liblink_path)
        return env

    def prebuild_armeabi(self):
        if exists(join(self.get_build_container_dir('armeabi'), '.patched')):
            info('Awesomecnn already patched, skipping.')
            return
        shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                join(self.get_build_dir('armeabi'), 'Setup'))
        self.apply_patch(join('patches', 'fix-surface-access.patch'))
        self.apply_patch(join('patches', 'fix-array-surface.patch'))
        shprint(sh.touch, join(self.get_build_container_dir('armeabi'), '.patched'))
        
    def build_armeabi(self):
        # AND: I'm going to ignore any extra pythonrecipe or cythonrecipe behaviour for now
        
        arch = ArchAndroid(self.ctx)
        env = self.get_recipe_env(arch)
        
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/png -I{jni_path}/jpeg'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl/include -I{jni_path}/sdl_mixer'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl_ttf -I{jni_path}/sdl_image'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        debug('pygame cflags', env['CFLAGS'])

        
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{libs_path} -L{src_path}/obj/local/{arch} -lm -lz'.format(
            libs_path=self.ctx.libs_dir, src_path=self.ctx.bootstrap.build_dir, arch=env['ARCH'])

        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')

        with current_directory(self.get_build_dir('armeabi')):
            info('hostpython is ' + self.ctx.hostpython)
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)

            info('strip is ' + env['STRIP'])
            build_lib = glob.glob('./build/lib*')
            assert len(build_lib) == 1
            print('stripping pygame')
            shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
                    env['STRIP'], '{}', ';')

        python_install_path = join(self.ctx.build_dir, 'python-install')
        # AND: Should do some deleting here!
        print('Should remove pygame tests etc. here, but skipping for now')


recipe = AwesomecnnRecipe()
