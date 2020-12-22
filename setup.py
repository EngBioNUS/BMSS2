import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name                          = "BMSS", 
    version                       = "2.0.1",
    author                        = "Russell Ngo",
    author_email                  = "biernjk@gmail.com",
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
    python_requires='>=3.7',
)
