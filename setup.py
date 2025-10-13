from setuptools import setup, find_packages

setup(
    name="library-management-system",
    version="1.0.0",
    description="A library management system with automated testing",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "pytest==7.4.2",
    ],
    python_requires=">=3.7",
)
