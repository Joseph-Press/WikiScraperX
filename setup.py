import setuptools

with open("readme.md", "r") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="wikiscraperx",
    version="1.0.2",
    author="Joseph Press",
    author_email="joepress101@gmail.com",
    description="scrape Wikipedia tables into CSV’s, enhancing data compatibility for text processing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Joseph-Press/wikiscraperx",
    download_url="https://github.com/Joseph-Press/WikiScraperX/archive/refs/tags/1.0.2.tar.gz",
    packages=setuptools.find_packages(),
    scripts=["scripts/wikiscraperx"],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)