from setuptools import setup, find_packages

setup(
    name='neko',
    version='1.0.0',
    description='A netcat-style backdoor tool in Python',
    author='YourName',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'neko=neko.cli:main',
        ],
    },
    python_requires='>=3.6',
)
