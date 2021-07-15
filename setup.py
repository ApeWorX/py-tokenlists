#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup  # type: ignore

extras_require = {
    "test": [
        "pytest==5.4.1",
        "pytest-xdist",
        "pytest-cov",
        "PyGithub>=1.54,<2.0",
        "hypothesis<6.0",
        "hypothesis-jsonschema==0.19.0",
    ],
    "lint": [
        "black==20.8b1",
        "flake8==3.8.4",
        "isort>=5.7.0,<6",
        "mypy==0.790",
    ],
    "doc": ["Sphinx>=3.4.3,<4", "sphinx_rtd_theme>=0.5.1"],
    "release": [
        "setuptools",
        "setuptools-scm",
        "wheel",
        "twine",
    ],
    "dev": ["pytest-watch", "IPython", "ipdb"],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["test"]
    + extras_require["lint"]
    + extras_require["release"]
    + extras_require["doc"]
)

with open("README.md", "r") as fp:
    long_description = fp.read()


setup(
    name="tokenlists",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="Ben Hauser",
    author_email="ben@hauser.id",
    description="Python implementation of Uniswaps' tokenlists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ApeWorX/py-tokenlists",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "click>=8.0.0",
        "dataclassy>=0.10.3,<1.0",
        "pyyaml>=5.4.1,<6",
        "semantic-version>=2.8.5,<3",
    ],
    entry_points={"console_scripts": ["tokenlists=tokenlists._cli:cli"]},
    extras_require=extras_require,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires=">=3.7,<4",
)
