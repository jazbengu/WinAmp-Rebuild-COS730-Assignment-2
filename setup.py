import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Winamp",
    version="0.1",
    author="Joy Bengu",
    author_email="u25000307@tuks.co.za",
    description="Remake of the leagcy system Winamp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jazbengu/WinAmp-Rebuild-COS730-Assignment-2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
