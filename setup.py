from setuptools import setup, find_namespace_packages

requirements = [
    "numpy",
    "opencv-python",
    "nptdms",
    "configparser",
    "pandas",
    "tqdm",

]

setup(
    name="tdmstovideo",
    version="0.0.0.2",
    author_email="federicoclaudi@protonmail.com",
    description="Code to convert Mantis TDMS files to mp4",
    packages=find_namespace_packages(exclude=()),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tdmstovideo_converter = tdmstovideo.converter:main",
        ]
    },
    url="https://github.com/BrancoLab/tdmstovideo_converter",
    author="Federico Claudi",
    zip_safe=False,
)
