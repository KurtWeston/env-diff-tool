"""Tests for formatters module."""
import pytest
import json
from env_diff.formatters import format_terminal, format_json, format_csv


@pytest.fixture
def sample_diff():
    return {
        'added': {'NEW_VAR': 'new_value'},
        'removed': {'OLD_VAR': 'old_value'},
        'changed': {'CHANGED_VAR': {'old': 'old', 'new': 'new'}},
        'unchanged': {'SAME_VAR': 'same_value'}
    }


class TestFormatTerminal:
    def test_format_with_differences_only(self, sample_diff):
        table = format_terminal(sample_diff, show_all=False, mask=False, sort_by='alpha')
        assert table is not None
        assert table.title == "Environment Variable Comparison"
    
    def test_format_with_all_variables(self, sample_diff):
        table = format_terminal(sample_diff, show_all=True, mask=False, sort_by='alpha')
        assert table is not None
    
    def test_format_with_masking(self, sample_diff):
        diff = {'added': {'API_TOKEN': 'secret123'}, 'removed': {}, 'changed': {}, 'unchanged': {}}
        table = format_terminal(diff, show_all=False, mask=True, sort_by='alpha')
        assert table is not None
    
    def test_format_sort_by_type(self, sample_diff):
        table = format_terminal(sample_diff, show_all=False, mask=False, sort_by='type')
        assert table is not None


class TestFormatJson:
    def test_format_basic_diff(self, sample_diff):
        result = format_json(sample_diff, show_all=False, mask=False)
        data = json.loads(result)
        
        assert 'NEW_VAR' in data['added']
        assert 'OLD_VAR' in data['removed']
        assert 'CHANGED_VAR' in data['changed']
        assert 'unchanged' not in data
    
    def test_format_with_all_variables(self, sample_diff):
        result = format_json(sample_diff, show_all=True, mask=False)
        data = json.loads(result)
        
        assert 'unchanged' in data
        assert 'SAME_VAR' in data['unchanged']
    
    def test_format_with_masking(self):
        diff = {
            'added': {'PASSWORD': 'secret123'},
            'removed': {},
            'changed': {},
            'unchanged': {}
        }
        result = format_json(diff, show_all=False, mask=True)
        data = json.loads(result)
        assert data['added']['PASSWORD'] != 'secret123'


class TestFormatCsv:
    def test_format_basic_diff(self, sample_diff):
        result = format_csv(sample_diff, show_all=False, mask=False)
        lines = result.strip().split('\n')
        
        assert 'Variable,Status,Old Value,New Value' in lines[0]
        assert len(lines) > 1
    
    def test_format_with_all_variables(self, sample_diff):
        result = format_csv(sample_diff, show_all=True, mask=False)
        lines = result.strip().split('\n')
        assert len(lines) == 5
    
    def test_format_empty_diff(self):
        diff = {'added': {}, 'removed': {}, 'changed': {}, 'unchanged': {}}
        result = format_csv(diff, show_all=False, mask=False)
        lines = result.strip().split('\n')
        assert len(lines) == 1
