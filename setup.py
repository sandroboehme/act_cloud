from setuptools import setup, find_packages
setup(
    name='act-cloud',
    version='0.1',
    packages=find_packages(),
    install_requires=['google-cloud-scheduler', 'google-cloud-firestore','ccxt'],
    description='Algorithmic cloud based trading',
    url='https://github.com/sandroboehme/act_cloud',
    license='Apache2',
)
