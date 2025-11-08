from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jsonql",
    version="0.1.0",
    author="FBF",
    author_email="f.bfalik@gmail.com",
    description="A lightweight, file-based JSON database with SQL-like interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/takouzlo/jsonql",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    extras_require={
        "browser": ["flet>=0.25.0"],
    },
    keywords="json database sqlite alternative lightweight file-based",
)