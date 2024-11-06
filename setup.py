from setuptools import find_packages, setup

with open("./README.md", "r") as f:
    long_description = f.read()

setup(
    name="pykp",
    version="0.0.10",
    description="Tooling for sampling and solving instances of the 0-1 Knapsack Problem",
    package_dir={"": "pykp"},
    packages=find_packages(where="pykp"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HRSAndrabi/pykp",
    author="Hassan Andrabi",
    author_email="hrs.andrabi@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "anytree>=2.12.1", 
        "tqdm>=4.66.6", 
        "pandas>=2.2.3",
        "matplotlib==3.9.2",
		"numpy==2.1.3",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.12",
)