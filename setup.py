from setuptools import setup, find_packages

setup(
    name='crownstone-lib-python-sse',
    version='1.1',
    url='https://github.com/crownstone/crownstone-lib-python-sse',
    author='Crownstone B.V.',
    description='Async python SSE client to receive Crownstone events',
    packages=find_packages(exclude=['examples', 'tests']),
    platforms='any',
    install_requires=list(package.strip() for package in open('requirements.txt')),
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ]
)
