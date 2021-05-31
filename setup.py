#!/usr/bin/env python

import pathlib

from setuptools import find_packages, setup

development = ["pytest==6.2.4", "black==19.10b0", "pre-commit==2.0.1", "ipdb==0.13.7"]

setup(
    name="cargo-fuzz-sourcer",
    version="0.0.1",
    author="Matej Kastak",
    author_email="matej.kastak@gmail.com",
    description="Correlate lines code with cargo-fuzz output.",
    long_description=pathlib.Path("./README.md").read_text(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License ",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    extras_require={
        "all": development,
        "dev": development,
    },
    include_package_data=True,
    install_requires=pathlib.Path("./requirements.txt").read_text().splitlines(),
    url="https://github.com/MatejKastak/cargo-fuzz-sourcer",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["cargo-fuzz-sourcer = cargo_fuzz_sourcer.cli:main"]
    },
)
