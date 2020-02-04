from setuptools import setup, find_namespace_packages

setup(
    name="tdmstovideo",
    version="0.0.0.1",
    author_email="federicoclaudi@protonmail.com",
    description="Code to convert Mantis TDMS files to mp4",
    packages=find_namespace_packages(exclude=()),
    include_package_data=True,
    url="https://github.com/BrancoLab/tdmstovideo_converter",
    author="Federico Claudi",
    zip_safe=False,
)
