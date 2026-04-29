from setuptools import find_packages, setup

with open('requirements.txt') as f:
    required_modules = f.read().splitlines()

version = {}
with open('dcdownloader/version.py') as f:
    exec(f.read(), version)

setup(
    name='DCDownloader',
    version=version['version'],
    description="a pluggable crawler for extracting image collections from target sites",
    author='techmoe',
    url='https://github.com/dev-techmoe/python-dcdownloader',
    license='MIT',
    packages=find_packages(include=['dcdownloader', 'dcdownloader.*']),
    install_requires=required_modules,
    entry_points={
        'console_scripts': [
            'dcdownloader=dcdownloader.main:main',
        ],
    },
)
