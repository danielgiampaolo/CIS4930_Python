import setuptools
from setuptools import setup
from distutils.core import Extension

c_lib = [Extension("libc_graph",
            sources = ["graph/c_graph.cpp"],
            include_dirs = ["graph"],
        ),
    ]

# https://docs.python.org/3/extending/building.html

#module1 = Extension('demo',
#                    define_macros = [('MAJOR_VERSION', '1'),
#                                     ('MINOR_VERSION', '0')],
#                    include_dirs = ['/usr/local/include'],
#                    libraries = ['tcl83'],
#                    library_dirs = ['/usr/local/lib'],
#                    sources = ['demo.c'])

setup(
    name = "NetView",
    version = 2.5,
    packages= ["netview","sample","graph","templates"],
    package_data={'graph': ['libc_graph.so']},
    description='Network Grapher',
    install_requires=["networkx", "Django", "matplotlib", "colour", "django_plotly_dash"],
    ext_modules=c_lib,
    entry_points =
    { 'console_scripts':
        [
            'runmyserver = sample.run:main',
            'initmigrate = sample.init:main',
        ]
    },
)
