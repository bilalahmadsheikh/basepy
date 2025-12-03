from setuptools import setup, find_packages

setup(
    name="basepy-sdk",
    version="0.1.0",
    description="A Python SDK for the Base blockchain",
    author="BasePy Team",
    packages=find_packages(),
    install_requires=[
        "web3>=6.0.0",
        "eth-account>=0.8.0",
        "requests>=2.28.0",
    ],
    python_requires=">=3.8",
)
