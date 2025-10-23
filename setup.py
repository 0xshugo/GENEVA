from __future__ import annotations

from pathlib import Path

from setuptools import setup

README = Path("README.md").read_text(encoding="utf-8")

setup(
    name="geneva-ethics-validator",
    version="0.1.0",
    description="GENEVA – Generative Ethics Validator toolkit",
    long_description=README,
    long_description_content_type="text/markdown",
    author="GENEVA Project",
    python_requires=">=3.12",
    install_requires=[
        "numpy",
        "scipy",
        "pillow",
        "requests",
        "scikit-learn",
        "streamlit",
    ],
    py_modules=["text_check", "image_check"],
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Source": "https://example.com/GENEVA",
    },
)
