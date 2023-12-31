import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mugravpy",
    version="0.0.1",
    author="Antony Butcher",
    description="A package for processing microgravity survey data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AntonyButcher/mugravpy/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)