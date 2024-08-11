# my_python_module/__init__.py

"""
My Python Module
================

A brief description of what your module does.

Submodules
----------
module
    Description of what the submodule does.
"""

__version__ = "0.1.0"

from .main import some_function

def package_function():
    """
    Example function at the package level.
    """
    print("This is a package-level function.")

# If you want to expose certain submodules or functions
# directly at the package level, you can import them here
# and list them in the __all__ variable.

__all__ = [
    "some_function",
    "package_function"
]
