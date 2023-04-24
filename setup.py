from setuptools import setup

setup(
    name="ccel_park",
    version="0.0.1",
    description="vasp envionment setting",
    url="https://github.com/hissmell/CCEL_parkwg.git",
    author="Park_wongyu",
    author_email="parkwg@postech.ac.kr",
    license="parkwg",
    packages=["park_lib"],
    zip_safe=False,
    install_requires=["ase=3.22.1"]
)