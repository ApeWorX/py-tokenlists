import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

with open("requirements.txt", "r") as fp:
    requirements = list(map(str.strip, fp.read().split("\n")))[:-1]


setuptools.setup(
    name="tokenlists",
    version="0.0.0-alpha0",
    author="Ben Hauser",
    author_email="ben@hauser.id",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamdefinitelyahuman/py-tokenlists",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6,<4',
)
