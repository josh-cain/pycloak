from distutils.core import setup

setup(
    name='Pycloak',
    version='0.1dev',
    author='Josh Cain',
    author_email='jcain@redhat.com',
    packages=['pycloak','pycloak.test'],
    license='GNU Lesser General Public License, V3',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests == 2.10.0",
        "pyjwt == 1.5.2",
    ],
)
