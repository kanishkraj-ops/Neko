from setuptools import setup, find_packages

setup(
    name='neko',
    version='2.0.0',
    description='Neko: A multi-mode offensive security framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Kanishk',
    url='https://github.com/kanishkraj-ops/Neko',
    packages=find_packages(),
    install_requires=[
        'rich',
        'requests',
        'dnspython',
        'paramiko',
        'python-whois',
        'shodan'
    ],
    entry_points={
        'console_scripts': [
            'neko=neko.cli:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Security',
    ],
)

