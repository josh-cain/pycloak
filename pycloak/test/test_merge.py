
from pycloak import merge
import pytest

def test_discrete_value_merge():
    result = merge.merge('wanted', 'unwanted')
    assert result == 'wanted'

def test_discrete_value_merge_None():
    result = merge.merge('wanted', None)
    assert result == 'wanted'

def test_discrete_value_merge_None_preferred():
    result = merge.merge(None, 'unwanted')
    assert result == None

def test_basic_dict_merge_orthogonal():
    result = merge.merge({'a': 1, 'c': 3}, {'b': 2, 'd': 4})
    assert {'a': 1, 'b': 2, 'c': 3, 'd': 4} == result

def test_basic_dict_merge_parallel():
    result = merge.merge({'a': 1, 'c': 3}, {'a': 2, 'c': 4})
    assert {'a': 1, 'c': 3} == result

def test_basic_dict_merge_intersecting():
    result = merge.merge({'a': 1, 'c': 3}, {'a': 2, 'd': 4})
    assert {'a': 1, 'c': 3, 'd': 4} == result

def test_basic_bool_merge_parallel():
    result = merge.merge({'a': True, 'b': False}, {'a': False, 'b': True})
    assert {'a': True, 'b': False} == result

def test_nested_dict_merge_orthogonal():
    preferred = {'a': 1, 'b': 2, 'c': {'c1': 31, 'c2': 32}}
    secondary = {'d': 4, 'e': 5, 'f': {'f1': 61, 'f2': 62}}
    result = merge.merge(preferred, secondary)
    assert {'a': 1, 'b': 2, 'c': {'c1': 31, 'c2': 32}, 'd': 4, 'e': 5, 'f': {'f1': 61, 'f2': 62}} == result

def test_nested_dict_merge_parallel():
    preferred = {'a': 1, 'b': 2, 'c': {'c1': 31, 'c2': 32}}
    secondary = {'a': 4, 'b': 5, 'c': {'c1': 61, 'c2': 62}}
    result = merge.merge(preferred, secondary)
    assert {'a': 1, 'b': 2, 'c': {'c1': 31, 'c2': 32}} == result

def test_nested_dict_merge_intersecting():
    preferred = {'a': 1, 'b': 2, 'c': {'c1': 31, 'c2': 32}}
    secondary = {'a': 4, 'e': 5, 'c': {'c1': 11, 'c3': 33}, 'f': {'f1': 61, 'f2': 62}}
    result = merge.merge(preferred, secondary)
    assert {'a': 1, 'b': 2, 'c': {'c1': 31, 'c2': 32, 'c3': 33}, 'e': 5, 'f': {'f1': 61, 'f2': 62}} == result

def test_nested_dict_merge_orthogonal_child():
    preferred = {'c': {'c1': 31, 'c2': 32}}
    secondary = {'c': {'c3': 33, 'c4': 34}}
    result = merge.merge(preferred, secondary)
    assert {'c': {'c1': 31, 'c2': 32, 'c3': 33, 'c4': 34}} == result

def test_nested_dict_merge_parallel_child():
    preferred = {'c': {'c1': 31, 'c2': 32}}
    secondary = {'c': {'c3': 33, 'c4': 34}}
    result = merge.merge(preferred, secondary)
    assert {'c': {'c1': 31, 'c2': 32, 'c3': 33, 'c4': 34}} == result

def test_nested_dict_merge_intersecting_child():
    preferred = {'c': {'c1': 31, 'c2': 32}}
    secondary = {'c': {'c1': 13, 'c4': 34}}
    result = merge.merge(preferred, secondary)
    assert {'c': {'c1': 31, 'c2': 32, 'c4': 34}} == result

def test_mismatched_type_merge_dict():
    preferred = {'c': {'c1': 31, 'c2': 32}}
    secondary = {'c': [13, 34]}
    result = merge.merge(preferred, secondary)
    assert {'c': {'c1': 31, 'c2': 32}} == result

def test_mismatched_type_merge_list():
    preferred = {'c': [13, 34]}
    secondary = {'c': {'c1': 31, 'c2': 32}}
    result = merge.merge(preferred, secondary)
    assert {'c': [13, 34]} == result

def test_nested_list_merge_orthogonal():
    preferred = {'a': 1, 'b': [21, 22, 23]}
    secondary = {'c': 3, 'd': [41, 42, 43]}
    result = merge.merge(preferred, secondary)
    assert {'a': 1, 'b': [21, 22, 23], 'c': 3, 'd': [41, 42, 43]} == result

def test_nested_list_merge_parallel():
    preferred = {'b': [21, 22, 23]}
    secondary = {'b': [41, 42, 43]}
    result = merge.merge(preferred, secondary)
    assert {'b': [21, 22, 23]} == result
