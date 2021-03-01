import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opoly", # Replace with your own username
    version="0.1.3",
    author="Giacomo Aloisi (GiackAloZ)",
    author_email="giacomo.aloisi1998@gmail.com",
    description="OPoly: a simple OpenMP polyhedral compilator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GiackAloZ/OPoly",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    keywords="compiler polyhedral optimization parallel omp c",
    packages=setuptools.find_packages(),
    package_data={
        "opoly.modules.minizinc": ["models/*.mzn", "libraries/*.mzn"],
    },
    install_requires=[
        "numpy>=1.19",
        "sympy>=1.7",
        "pymzn>=0.18.3"
    ],
    python_requires='>=3.9',
    entry_points={
        "console_scripts": [
            "opoly=opoly.scripts.opoly:main",
        ],
    }
)