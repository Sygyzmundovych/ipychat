# -*- coding: utf-8 -*-

import inspect
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
import pytest

from ipychat.context import (
    extract_variables_from_query,
    get_context_for_variables,
    get_variable_info,
)


@dataclass
class SampleClass:
    name: str
    value: int

    def sample_method(self):
        pass


def sample_function(x: int) -> int:
    """A sample function for testing."""
    return x * 2


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": ["a", "b", "c"],
            "C": [1.1, 2.2, 3.3],
        }
    )


@pytest.fixture
def sample_namespace(sample_dataframe):
    return {
        "df": sample_dataframe,
        "numbers": [1, 2, 3],
        "text": "hello world",
        "obj": SampleClass("test", 42),
        "func": sample_function,
        "np_array": np.array([1, 2, 3]),
    }


def test_extract_variables_from_query():
    query = "Show me the df and check numbers variable"
    vars = extract_variables_from_query(query)
    assert "df" in vars
    assert "numbers" in vars
    assert "variable" in vars  # Note: this is expected behavior
    assert "show" not in vars  # Common words should still be included


def test_get_variable_info_dataframe(sample_dataframe):
    info = get_variable_info("df", sample_dataframe)
    assert "Variable: df" in info
    assert "Type: DataFrame" in info
    assert "Shape: (3, 3)" in info
    assert "Columns:" in info
    assert "- A (int64)" in info
    assert "- B (object)" in info
    assert "- C (float64)" in info
    assert "Sample (first 5 rows):" in info


def test_get_variable_info_function():
    info = get_variable_info("func", sample_function)
    assert "Variable: func" in info
    assert "Type: function" in info
    assert "Source code:" in info
    assert inspect.getsource(sample_function) in info


def test_get_variable_info_class_instance():
    obj = SampleClass("test", 42)
    info = get_variable_info("obj", obj)
    assert "Variable: obj" in info
    assert "Type: SampleClass" in info
    assert "Attributes:" in info
    assert "name" in info
    assert "value" in info
    assert "sample_method" in info


def test_get_variable_info_list():
    numbers = [1, 2, 3, 4, 5]
    info = get_variable_info("numbers", numbers)
    assert "Variable: numbers" in info
    assert "Type: list" in info
    assert "Length: 5" in info
    assert "Sample: [1, 2, 3, 4, 5]" in info


def test_get_variable_info_numpy_array():
    arr = np.array([1, 2, 3])
    info = get_variable_info("arr", arr)
    assert "Variable: arr" in info
    assert "Type: ndarray" in info
    assert "Sample:" in info


def test_get_variable_info_long_string():
    long_text = "x" * 200
    info = get_variable_info("text", long_text)
    assert "Variable: text" in info
    assert "Type: str" in info
    assert len(info) < len(long_text)  # Should be truncated
    assert "..." in info


def test_get_context_for_variables_empty_query(sample_namespace):
    context = get_context_for_variables(sample_namespace, "")
    assert context == ""


def test_get_context_for_variables_single_var(sample_namespace):
    context = get_context_for_variables(sample_namespace, "Show me the df")
    assert "Variable: df" in context
    assert "Type: DataFrame" in context


def test_get_context_for_variables_multiple_vars(sample_namespace):
    context = get_context_for_variables(
        sample_namespace, "Compare df with numbers and text"
    )
    assert "Variable: df" in context
    assert "Variable: numbers" in context
    assert "Variable: text" in context


def test_get_context_for_variables_nonexistent_var(sample_namespace):
    context = get_context_for_variables(
        sample_namespace, "Show me nonexistent_variable"
    )
    assert context == ""  # Should return empty string for non-existent variables


def test_get_context_for_variables_with_error_variable():
    # Test handling of variables that raise errors during inspection
    class ErrorClass:
        @property
        def problematic_property(self):
            raise Exception("This property raises an error")

    namespace = {"error_obj": ErrorClass()}
    context = get_context_for_variables(namespace, "Show me error_obj")
    assert "Variable: error_obj" in context
    assert "Type: ErrorClass" in context


def test_get_variable_info_with_docstring():
    def documented_function():
        """This is a test docstring.

        It has multiple lines.
        """
        pass

    info = get_variable_info("func", documented_function)
    assert "Variable: func" in info
    assert "Type: function" in info
    assert "Documentation:" in info
    assert "This is a test docstring." in info


def test_get_variable_info_nested_structure():
    nested = {
        "list": [1, 2, 3],
        "dict": {"a": 1, "b": 2},
    }
    info = get_variable_info("nested", nested)
    assert "Variable: nested" in info
    assert "Type: dict" in info
    assert "Sample:" in info
