import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

p = setuptools.find_packages()

setuptools.setup(
    name                          = "BMSS", 
    version                       = "2.0.16",
    author                        = "Russell Ngo",
    author_email                  = "biernjk@nus.edu.sg",
    description                   = "A package for dyanmic model analysis.",
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/EngBioNUS/BMSS2",
    packages                      = setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['numpy', 'scipy', 'numba', 'matplotlib', 'pandas',
                      'PyYAML', 'SALib', 'arviz', 'xarray'
                      ],
    python_requires='>=3.7',
    include_package_data = True,
    package_dir          = {'BMSS': 'BMSS'},
    package_data         = {'BMSS': ['models/*.db',
                                     'models/*.txt',
                                     'models/*.ini',
                                     'stylelib/*.mplstyle']}
)
