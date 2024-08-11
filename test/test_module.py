# my_python_module/module.py

"""
module.py
=========

This module provides example functions and classes for demonstration purposes.
"""

def some_function(x, y):
    """
    Adds two numbers together.

    Parameters
    ----------
    x : int or float
        The first number.
    y : int or float
        The second number.

    Returns
    -------
    int or float
        The sum of x and y.
    """
    return x + y

class ExampleClass:
    """
    An example class that performs simple arithmetic operations.

    Attributes
    ----------
    value : int or float
        The initial value for the arithmetic operations.
    """

    def __init__(self, value):
        """
        Initializes the ExampleClass with a value.

        Parameters
        ----------
        value : int or float
            The initial value for the arithmetic operations.
        """
        self.value = value

    def add(self, amount):
        """
        Adds a given amount to the value.

        Parameters
        ----------
        amount : int or float
            The amount to add to the value.

        Returns
        -------
        int or float
            The new value after addition.
        """
        self.value += amount
        return self.value

    def multiply(self, factor):
        """
        Multiplies the value by a given factor.

        Parameters
        ----------
        factor : int or float
            The factor to multiply the value by.

        Returns
        -------
        int or float
            The new value after multiplication.
        """
        self.value *= factor
        return self.value

def helper_function():
    """
    A helper function that prints a message.

    This function doesn't do much but serves as an example of utility functions
    you might include in your module.
    """
    print("This is a helper function.")
