from setuptools import setup, find_packages

setup(
    name="moovegate",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=1.10.0",
    ],
    entry_points={
        "console_scripts": [
            "moovegate=cli:main",
        ],
    },
)
