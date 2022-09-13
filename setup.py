import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_datatable_serverside_mixin",
    version="2.0.0",
    description="Server-side Datatable processing view mixin for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthttam/django_datatable_serverside_mixin",
    license="MIT",
    author="Matt Henry",
    author_email="matt.henry8411@gmail.com",
    install_requires=["Django>=3.0", "querystring-parser>=1.2.4"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
