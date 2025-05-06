# setup.py
from setuptools import setup, find_packages

setup(
    name="eventual",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
    ],
    description="A toolkit for working with event-based hypergraphs for LLM-based agents.",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/Eventual",
)