

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='terraformvspherevm',  
    version='0.0.12',  
    description='Create VSphere resources using terraform',  
    long_description=long_description,  
    long_description_content_type='text/markdown',
    url='https://github.com/tsenay/python-terraformvpsherevm',  
    author='Thomas Senay',  
    author_email='tsenay.consulting@icloud.com',  
    classifiers=[  
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='vpshere terraform',  
    packages=find_packages(exclude=['contrib', 'docs', 'tests']), 
    python_requires='>=3.6',
    install_requires=['terrascript','python_terraform'],  
    package_data={  
        'terraformvspherevm': ['terraformvm.py','terrascriptvspherevm.py'],
    },
    entry_points={  
        'console_scripts': [
            'terraformvspherevm=terraformvspherevm:main',
        ],
    },
    project_urls={  
        'Bug Reports': 'https://github.com/tsenay/python-terraformvpsherevm/issues',
        'Source': 'https://github.com/tsenay/python-terraformvpsherevm',
    },
    
)
