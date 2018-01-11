from distutils.core import setup

setup(
    name='pycloak',
    packages=['pycloak','pycloak.test'],
    version='0.1.9',
    description='API for Keycloak Admin Interface',
    author='Josh Cain',
    author_email='jcain@redhat.com',
    license='GNU Lesser General Public License, V3',
    long_description=open('README.txt').read(),
)
