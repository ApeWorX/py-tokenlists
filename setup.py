#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup  # type: ignore

extras_require = {
    "test": [  # `test` GitHub Action jobs uses this
        "pytest>=6.0,<7.0",  # Core testing package
        "pytest-xdist",  # multi-process runner
        "pytest-cov",  # Coverage analyzer plugin
        "hypothesis>=6.2.0,<7.0",  # Strategy-based fuzzer
        "PyGithub>=1.54,<2.0",  # Necessary to pull official schema from github
        "hypothesis-jsonschema==0.19.0",  # Fuzzes based on a json schema
    ],
    "lint": [
        "black>=22.3.0,<23.0",  # auto-formatter and linter
        "mypy>=0.950,<1.0",  # Static type analyzer
        "flake8>=4.0.1,<5.0",  # Style linter
        "isort>=5.10.1,<6.0",  # Import sorting linter
    ],
    "doc": [
        "Sphinx>=3.4.3,<4",  # Documentation generator
        "sphinx_rtd_theme>=0.1.9,<1",  # Readthedocs.org theme
        "towncrier>=19.2.0, <20",  # Generate release notes
    ],
    "release": [  # `release` GitHub Action job uses this
        "setuptools",  # Installation tool
        "wheel",  # Packaging tool
        "twine",  # Package upload tool
    ],
    "dev": [
        "commitizen",  # Manage commits and publishing releases,
        "pre-commit",  # Ensure that linters are run prior to commiting
        "pytest-watch",  # `ptw` test watcher/runner
        "IPython",  # Console for interacting
        "ipdb",  # Debugger (Must use `export PYTHONBREAKPOINT=ipdb.set_trace`)
    ],
}

extras_require["dev"] = (
    extras_require["test"]
    + extras_require["lint"]
    + extras_require["doc"]
    + extras_require["release"]
    + extras_require["dev"]
)

with open("./README.md") as readme:
    long_description = readme.read()

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
    include_package_data=True,
    python_requires=">=3.7.2,<3.11",
    install_requires=[
        "importlib-metadata ; python_version<'3.8'",
        "click>=8.0.1",
        "pydantic>=1.9.0,<2.0.0",
        "pyyaml>=6.0,<7.0",
        "semantic-version>=2.9.0,<3",
    ],
    entry_points={"console_scripts": ["tokenlists=tokenlists._cli:cli"]},
    extras_require=extras_require,
    py_modules=["tokenlists"],
    license="Apache-2.0",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"ape_tokens": ["py.typed"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
