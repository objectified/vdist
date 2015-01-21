from setuptools import setup, find_packages

setup(
    name='vdist',
    version='0.1',
    description='Create OS packages from Python projects using Docker containers',
    long_description='Create OS packages from Python projects using Docker containers',
    author='L. Brouwer',
    author_email='objectified@gmail.com',
    url='https://github.com/objectified/vdist',
    packages=find_packages(),
    install_requires=['jinja2==2.7.3', 'docker-py==0.7.1'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators'
    ],
)
