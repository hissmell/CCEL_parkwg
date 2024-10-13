from setuptools import setup

setup(
    name="ccel_park",
    version="0.0.2",
    description="vasp envionment setting",
    url="https://github.com/hissmell/CCEL_parkwg.git",
    author="Park_wongyu",
    author_email="parkwg@postech.ac.kr",
    license="parkwg",
    packages=["park_lib"],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'park=my_library:main',
        ]},
    install_requires=["ase","treelib"]
)