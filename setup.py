import setuptools

with open("readme.md", "r") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="wikiscraper",
    version="1.0.1",
    author="Jeicex1",
    author_email="joepress101@gmail.com",
    description="scrape Wikipedia tables into CSV’s, enhancing data compatibility for text processing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Joseph-Press/WikiScraper",
    packages=setuptools.find_packages(),
    scripts=["scripts/wikiscraper"],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)