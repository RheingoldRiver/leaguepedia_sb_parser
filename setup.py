import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lp_sb_parser",
    version="0.0.1",
    author="RheingoldRiver",
    author_email="river.esports@gmail.com",
    description="Parser for Leaguepedia scoreboards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RheingoldRiver/lp_sb_parser",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    install_requires=[]
)