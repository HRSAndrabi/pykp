from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pykp",
    version="0.0.24",
    description="Tooling for sampling and solving instances of the 0-1 Knapsack Problem",
    packages=find_packages(exclude=["docs", "tests*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HRSAndrabi/pykp",
    author="Hassan Andrabi",
    author_email="hrs.andrabi@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "anytree>=2.12.1", 
        "pandas>=2.2.3",
        "matplotlib==3.9.2",
		"numpy==2.1.3",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.12",
)