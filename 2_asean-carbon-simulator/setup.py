"""
ASEAN Carbon Integration Simulator
Setup configuration for Python package installation
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="asean-carbon-simulator",
    version="2.0.0",
    author="Bosco Chiramel",
    author_email="bosco8b4824@gmail.com",
    description="Interactive tool for analyzing carbon pricing policy divergence across ASEAN's petroleum refining sector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bosco-chiramel/asean-carbon-simulator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.31.0",
        "pandas>=2.1.4",
        "numpy>=1.26.3",
        "plotly>=5.18.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "asean-carbon=app:main",
        ],
    },
    keywords="carbon pricing, ASEAN, energy transition, climate policy, emissions trading",
    project_urls={
        "Bug Reports": "https://github.com/bosco-chiramel/asean-carbon-simulator/issues",
        "Source": "https://github.com/bosco-chiramel/asean-carbon-simulator",
        "Documentation": "https://github.com/bosco-chiramel/asean-carbon-simulator#readme",
    },
)
