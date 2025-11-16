from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="jsonql-db",
    version="0.1.3",
    description="A lightweight, file-based JSON database with SQL-like interface",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/takouzlo/jsonql-db",
    author="FBF",
    author_email="f.bfalik@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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
    packages=find_packages(),
    python_requires=">=3.7",
    extras_require={
        "browser": ["flet>=0.25.0"],
    },
    keywords="json database sqlite alternative lightweight file-based",
)