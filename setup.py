#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

extras_require = {
    "test": [  # `test` GitHub Action jobs uses this
        "pytest>=6.0",  # Core testing package
        "pytest-xdist",  # multi-process runner
        "pytest-cov",  # Coverage analyzer plugin
        "hypothesis>=6.86.2,<7",  # Strategy-based fuzzer
        "PyGithub>=1.54,<2",  # Necessary to pull official schema from github
        "hypothesis-jsonschema==0.19.0",  # Fuzzes based on a json schema
    ],
    "lint": [
        "black>=23.11.0,<24",  # auto-formatter and linter
        "mypy>=1.7.1,<2",  # Static type analyzer
        "types-requests",  # Needed due to mypy typeshed
        "types-setuptools",  # Needed due to mypy typeshed
        "flake8>=6.1.0,<7",  # Style linter
        "isort>=5.10.1",  # Import sorting linter
        "mdformat>=0.7.17",  # Auto-formatter for markdown
        "mdformat-gfm>=0.3.5",  # Needed for formatting GitHub-flavored markdown
        "mdformat-frontmatter>=0.4.1",  # Needed for frontmatters-style headers in issue templates
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
    python_requires=">=3.8,<4",
    install_requires=[
        "importlib-metadata ; python_version<'3.8'",
        "click>=8.1.7,<9",
        "pydantic>=2.5.2,<3",
        "pyyaml>=6.0,<7",
        "requests>=2.28.1,<3",
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
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
