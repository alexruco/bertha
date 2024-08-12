from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bertha",  # Your package name
    version="0.2.0",  # Updated version to reflect recent changes
    author="Alex Ruco",  # Your name
    author_email="alex@ruco.pt",  # Your email
    description="A simple web crawler package for discovering all pages of a website.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexruco/bertha",  # Your GitHub repository
    packages=find_packages(),  # Automatically find all packages in the project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Assuming your project uses the MIT License
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Specify the Python version required
    install_requires=[
        "requests",  # Add any other dependencies your project requires
    ],
    entry_points={
        'console_scripts': [
            'bertha=bertha.main:main',  # Command-line script entry point, if applicable
        ],
    },
)
