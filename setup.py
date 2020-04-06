import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='PyWhitakersWords',
     version='0.0',
     author="Henry Heffan",
     author_email="henry.heffan@yale.com",
     description="A Latin Dictionary (Whitaker's Words combined with Lewis & Short)",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/HenryHeffan/PyWhitakersWords",
     packages=setuptools.find_packages(),
 )