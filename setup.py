from setuptools import setup, find_packages

setup(
    name="moneyteacher",
    version="1.0.0",
    description="Interaktiv kassaövning för svenska valörer",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="MoneyTeacher",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["PyGObject>=3.42"],
        package_data={
        "": ["locale/*/LC_MESSAGES/*.mo"],
    },
    entry_points={
        "console_scripts": [
            "moneyteacher=moneyteacher.main:main",
        ],
    },
    data_files=[
        ("share/applications", ["moneyteacher.desktop"]),
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: X11 Applications :: GTK",
    ],
)
