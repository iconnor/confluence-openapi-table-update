# Python wheel setup file
import os
from setuptools import setup, find_packages

# Get the version from the VERSION file
version = open(os.path.join(os.path.dirname(__file__), 'VERSION')).read().strip()

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    long_description = f.read()

setup(name='Confluence OpenAPI Table Update',
    version=version,
    description='A tool to update Confluence tables from OpenAPI specifications',
    long_description=long_description,
    url='http://github.com/iconnor/confluence-openapi-table-update',
    license='MIT',
    requires=[
        'requests',
        'argparse',
        'atlassian-python-api'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='confluence openapi table update',
    language='en',
    maintainer='Ian Connor',
    maintainer_email='ian.connor@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'confluence-openapi-table-update = update_confluence:main',
        ],
    },
)
