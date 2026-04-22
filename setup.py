"""
Setup configuration for Plant Based Assistant package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="plant-based-assistant",
    version="0.1.0",
    author="Plant Based Assistant Team",
    author_email="your-email@example.com",
    description="A Python chatbot that analyzes ingredients, suggests vegan alternatives, and recommends recipes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/plant-based-assistant",
    packages=find_packages(exclude=["tests", "docs"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.10",
        "openai>=1.0.0",
        "requests>=2.30.0",
        "httpx>=0.24.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.30.0",
        "streamlit-chat>=0.1.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.10.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "plant-based-assistant=main:main",
        ],
    },
)
