from setuptools import setup, find_packages

setup(
    name='vdist',
    version='0.6',
    description='Create OS packages from Python '
                'projects using Docker containers',
    long_description='Create OS packages from Python '
                     'projects using Docker containers',
    author='objectified, dante-signal31',
    author_email='objectified@gmail.com, dante.signal31@gmail.com',
    license='MIT',
    url='https://github.com/dante-signal31/vdist',
    packages=find_packages(),
    install_requires=['jinja2==2.7.3'],
    package_data={'': ['internal_profiles.json', '*.sh']},
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='python docker deployment packaging',
)
