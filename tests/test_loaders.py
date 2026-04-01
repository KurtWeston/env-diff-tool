"""Tests for loaders module."""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from env_diff.loaders import load_from_file, load_from_stdin, _is_shell_script, _parse_shell_exports


class TestLoadFromFile:
    def test_load_dotenv_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('KEY1=value1\n')
            f.write('KEY2=value2\n')
            f.name
        
        try:
            result = load_from_file(f.name)
            assert result['KEY1'] == 'value1'
            assert result['KEY2'] == 'value2'
        finally:
            os.unlink(f.name)
    
    def test_load_shell_export_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write('export VAR1=value1\n')
            f.write('export VAR2=value2\n')
            f.name
        
        try:
            result = load_from_file(f.name)
            assert result['VAR1'] == 'value1'
            assert result['VAR2'] == 'value2'
        finally:
            os.unlink(f.name)
    
    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_from_file('/nonexistent/file.env')


class TestLoadFromStdin:
    def test_load_dotenv_from_stdin(self):
        with patch('sys.stdin.read', return_value='KEY1=value1\nKEY2=value2'):
            result = load_from_stdin()
            assert result['KEY1'] == 'value1'
            assert result['KEY2'] == 'value2'
    
    def test_load_shell_exports_from_stdin(self):
        with patch('sys.stdin.read', return_value='export VAR1=value1\nexport VAR2=value2'):
            result = load_from_stdin()
            assert result['VAR1'] == 'value1'
            assert result['VAR2'] == 'value2'
    
    def test_load_with_quotes(self):
        with patch('sys.stdin.read', return_value='KEY1="quoted value"'):
            result = load_from_stdin()
            assert result['KEY1'] == 'quoted value'


class TestIsShellScript:
    def test_detects_export_statement(self):
        assert _is_shell_script('export VAR=value')
    
    def test_detects_shebang(self):
        assert _is_shell_script('#!/bin/bash\nVAR=value')
    
    def test_not_shell_script(self):
        assert not _is_shell_script('VAR=value\nKEY=data')


class TestParseShellExports:
    def test_parse_basic_exports(self):
        content = 'export VAR1=value1\nexport VAR2=value2'
        result = _parse_shell_exports(content)
        assert result == {'VAR1': 'value1', 'VAR2': 'value2'}
    
    def test_parse_with_quotes(self):
        content = 'export VAR1="quoted value"\nexport VAR2=\'single quoted\''
        result = _parse_shell_exports(content)
        assert result['VAR1'] == 'quoted value'
        assert result['VAR2'] == 'single quoted'
    
    def test_parse_empty_content(self):
        result = _parse_shell_exports('')
        assert result == {}
