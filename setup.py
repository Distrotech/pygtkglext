#!/usr/bin/env python
"""Python language binding for GtkGLExt, OpenGL Extension to GTK.

TODO: Write a good long description"""

from distutils.command.build import build
from distutils.core import setup
import os
import sys

from dsextras import GLOBAL_INC, GLOBAL_MACROS
from dsextras import getoutput, have_pkgconfig, list_files, pkgc_version_check
from dsextras import BuildExt, InstallLib, PkgConfigExtension
from dsextras import Template, TemplateExtension

MAJOR_VERSION = 0
MINOR_VERSION = 0
MICRO_VERSION = 2

VERSION = "%d.%d.%d" % (MAJOR_VERSION,
                        MINOR_VERSION,
                        MICRO_VERSION)

API_MAJOR_VERSION = 1
API_MINOR_VERSION = 0

API_VERSION = "%d.%d" % (API_MAJOR_VERSION,
                         API_MINOR_VERSION)

GTKGLEXT_PKG = 'gtkglext-1.0'
GTKGLEXT_REQUIRED_VERSION = '0.7.0'

PYGTK_REQUIRED_VERSION = '1.99.15'

PYGTK_SUFFIX = '2.0'
PYGTK_SUFFIX_LONG = 'gtk-' + PYGTK_SUFFIX

GLOBAL_INC += ['.', 'gtk/gdkgl', 'gtk/gtkgl']
GLOBAL_MACROS += [('PYGTKGLEXT_MAJOR_VERSION', MAJOR_VERSION),
                  ('PYGTKGLEXT_MINOR_VERSION', MINOR_VERSION),
                  ('PYGTKGLEXT_MICRO_VERSION', MICRO_VERSION)]

DEFS_DIR    = os.path.join('share', 'pygtk', PYGTK_SUFFIX, 'defs')
CODEGEN_DIR = os.path.join('share', 'pygtk', PYGTK_SUFFIX, 'codegen')
INCLUDE_DIR = os.path.join('include', 'pygtk-%s' % PYGTK_SUFFIX)

str_version = sys.version[:3]
version = map(int, str_version.split('.'))
if version < [2, 2]:
    raise SystemExit, \
          "Python 2.2 or higher is required, %s found" % str_version

class PyGtkGLExtInstallLib(InstallLib):
    def run(self):
        self.add_template_option('VERSION', VERSION)
        self.add_template_option('PYGTKGLEXT_API_VERSION', API_VERSION)
        self.prepare()

        self.install_template_as('pygtkglext.pc.in',
                                 os.path.join(self.libdir, 'pkgconfig'),
                                 'pygtkglext-' + API_VERSION + '.pc')

        # Modify the base installation dir
        install_dir = os.path.join(self.install_dir, PYGTK_SUFFIX_LONG)
        self.set_install_dir(install_dir)
                                          
        InstallLib.run(self)
    
    def install_template_as(self, filename, install_dir, install_filename):
        """Install template filename into target directory install_dir."""
        
        template = open(filename).read()
        for key, value in self.template_options.items():
            template = template.replace(key, value)
        
        output = os.path.join(install_dir, install_filename)
        self.mkpath(install_dir)
        open(output, 'w').write(template)
        self.local_inputs.append(filename)
        self.local_outputs.append(output)
        return output

if not pkgc_version_check('pygtk-2.0', 'PyGTK', PYGTK_REQUIRED_VERSION):
    raise SystemExit, "Aborting"
pygtkincludedir = getoutput('pkg-config --variable pygtkincludedir pygtk-2.0')
codegendir = getoutput('pkg-config --variable codegendir pygtk-2.0')
defsdir = getoutput('pkg-config --variable defsdir pygtk-2.0')

GLOBAL_INC.append(pygtkincludedir)

GTKDEFS = [os.path.join(defsdir, 'pango-types.defs'),
           os.path.join(defsdir, 'atk-types.defs'),
           os.path.join(defsdir, 'gdk-types.defs'),
           os.path.join(defsdir, 'gtk-types.defs')]

sys.path.append(codegendir)
try:
    from override import Overrides
except ImportError:
    raise SystemExit, \
'Could not find code generator in %s, do you have installed pygtk correctly?'

if sys.platform == 'win32':
    # MSVC compatible struct packing is required.
    # Note gcc2 uses -fnative-struct while gcc3
    # uses -mms-bitfields. Based on the version
    # the proper flag is used below.
    flag_dict = { '2' : '-fnative-struct', '3' : '-mms-bitfields' }
    gcc_version = getoutput('gcc --version')
    extra_compile_args = [ flag_dict[gcc_version[0]] ]
    print 'Using GCC version %s with the %s flag' % (gcc_version, flag_dict[gcc_version[0]])
else:
    extra_compile_args = None

gdkglext = TemplateExtension(name='gdkglext',
                             pkc_name=GTKGLEXT_PKG,
                             pkc_version=GTKGLEXT_REQUIRED_VERSION,
                             output='gtk.gdkgl._gdkgl',
                             defs='gtk/gdkgl/gdkglext.defs',
                             sources=['gtk/gdkgl/gdkglmodule.c',
                                      'gtk/gdkgl/gdkglext.c'],
                             register=GTKDEFS,
                             override='gtk/gdkgl/gdkglext.override',
                             extra_compile_args=extra_compile_args)

gtkglext = TemplateExtension(name='gtkglext',
                             pkc_name=GTKGLEXT_PKG,
                             pkc_version=GTKGLEXT_REQUIRED_VERSION,
                             output='gtk.gtkgl._gtkgl',
                             defs='gtk/gtkgl/gtkglext.defs',
                             sources=['gtk/gtkgl/gtkglmodule.c',
                                      'gtk/gtkgl/gtkglext.c'],
                             register=GTKDEFS + ['gtk/gdkgl/gdkglext-types.defs'],
                             override='gtk/gtkgl/gtkglext.override',
                             extra_compile_args=extra_compile_args)

data_files = []
ext_modules = []
py_modules = []

if gdkglext.can_build():
    ext_modules.append(gdkglext)
    data_files.append((DEFS_DIR, ('gtk/gdkgl/gdkglext.defs',
                                  'gtk/gdkgl/gdkglext-types.defs')))
    py_modules += ['gtk.gdkgl.__init__']

if gtkglext.can_build():
    ext_modules.append(gtkglext)
    data_files.append((DEFS_DIR, ('gtk/gtkgl/gtkglext.defs',)))
    py_modules += ['gtk.gtkgl.__init__', 'gtk.gtkgl.widget', 'gtk.gtkgl.apputils']

doclines = __doc__.split("\n")

setup(name="pygtkglext",
      url='http://gtkglext.sourceforge.net/',
      version=VERSION,
      license='LGPL',
      platforms=['yes'],
      maintainer="Naofumi Yasufuku",
      maintainer_email="naofumi@users.sourceforge.net",
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      py_modules=py_modules,
      ext_modules=ext_modules,
      data_files=data_files,
      cmdclass={'install_lib': PyGtkGLExtInstallLib,
                'build_ext': BuildExt })
