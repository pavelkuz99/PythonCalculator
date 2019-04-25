from setuptools import setup, find_packages

setup(
    name='pycalc',
    version='1.2.0',
    author='Pavel Kuzmich',
    author_email='Pavel_Kuzmich@epam.com',
    description='Pure Python command-line calculator',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pycalc=calculator.pycalc:main',
        ]
    }
)
