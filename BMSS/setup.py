import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name                          = "russellnjk", # Replace with your own username
    version                       = "2.0.1",
    author                        = "Russell Ngo",
    author_email                  = "biernjk@gmail.com",
    description                   = "A package for dyanmic model analysis.",
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/pypa/sampleproject",
    packages                      = setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",,
        "Intended Audience :: Science/Research",
        "License           :: Freely Distributable",
        "Operating System  :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Synthetic Biology",
        "Topic :: Scientific/Engineering :: Systems Biology",
        "Topic :: Software Development   :: Libraries :: Python Modules",
    ],
    python_requires='>=3.7',
)
