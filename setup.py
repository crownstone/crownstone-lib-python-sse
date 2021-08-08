from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='crownstone-sse',
    version="2.0.1",
    url='https://github.com/crownstone/crownstone-lib-python-sse',
    author='Crownstone B.V.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=list(package.strip() for package in open('requirements.txt')),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    python_requires='>=3.7',
)
