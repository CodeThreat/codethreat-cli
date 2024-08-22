from setuptools import setup, find_packages

setup(
    name="codethreat-cli",
    version="0.1.0",
    description="CLI toolset for CodeThreat ASP",
    author="CodeThreat",
    author_email="dev@codethreat.com",
    packages=find_packages(include=['cli', 'cli.*']),
    include_package_data=True,
    install_requires=[
        'setuptools~=73.0.1',
        'click~=8.1.7',
        'requests~=2.32.3',
        'colorama~=0.4.6',
    ],
    entry_points={
        "console_scripts": [
            "codethreat-cli=cli.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
