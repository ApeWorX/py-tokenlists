#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup  # type: ignore

extras_require = {
    "test": [
        "pytest==5.4.1",
        "pytest-xdist",
        "pytest-coverage",
        "PyGithub>=1.54,<2.0",
        "hypothesis<6.0",
        "hypothesis-jsonschema==0.19.0",
    ],
    "lint": [
        "black==20.8b1",
        "flake8==3.8.4",
        "isort>=5.7.0,<6",
        "mypy==0.790",
        "pydocstyle>=5.1.1,<6",
    ],
    "doc": ["Sphinx>=3.4.3,<4", "sphinx_rtd_theme>=0.5.1"],
    "dev": ["pytest-watch>=4.2.0,<5", "wheel", "twine", "ipython"],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["test"]  # noqa: W504
    + extras_require["lint"]  # noqa: W504
    + extras_require["doc"]  # noqa: W504
)

with open("README.md", "r") as fp:
    long_description = fp.read()


setup(
    name="tokenlists",
    version="0.1.0-alpha.1",
    author="Ben Hauser",
    author_email="ben@hauser.id",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamdefinitelyahuman/py-tokenlists",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=["semantic-version>=2.8.5,<3"],
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
