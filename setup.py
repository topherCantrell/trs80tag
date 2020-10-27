import setuptools

# https://packaging.python.org/tutorials/packaging-projects/

# From the directory with this file
#   py setup.py sdist bdist_wheel
#   py -m twine upload dist/*

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="trs80tag",  # Replace with your own username
    version="1.5",
    author="Chris Cantrell",
    author_email="topherCantrell@gmail.com",
    description="Classic text adventures from the CoCo and TRS80 Model 1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/topherCantrell/trs80tag",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'MC6809'
    ],
    include_package_data=True,
)
