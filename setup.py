import setuptools

setuptools.setup(
    name="pywhydup",
    version="0.1.0",
    url="https://github.com/cchwala/pywhydup.git",

    author="Christian Chwala",
    author_email="christian.chwala@kit.edu",

    description="Python WRF-Hydro setup duplicator, manipulator and SLURM runner",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
