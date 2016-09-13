from setuptools import setup, find_packages

setup(
    name='migraine',
    version='1.0.0',
    description='Datastore independent migration tool',
    author='Alexander Jung-Loddenkemper',
    author_email='alexander@julo.ch',
    url='https://github.com/alexanderjulo/migraine',
    packages=find_packages(),
    install_requires=[
        'Click==6.0',
        'click-log==0.1.4',
        'PyYAML==3.11',
        'jinja2==2.7.3'
    ],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['migraine=migraine.cli:main']
    }
)
