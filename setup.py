from setuptools import setup, find_packages

version = '1'

setup(
    name='robocam',
    version=version,
    description="",
    long_description='',
    classifiers=[
        'Framework :: Tornado',
        'Programming Language :: Python',
    ],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=filter(len, open('requirements.txt').readlines()),
    entry_points={
        'console_scripts': [
            'robocam=robocam.app:main',
        ]
    },
)
