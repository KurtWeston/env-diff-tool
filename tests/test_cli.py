"""Tests for CLI module."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from env_diff.cli import main, _load_source


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_missing_arguments(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code == 1
        assert 'Error' in result.output
    
    @patch('env_diff.cli.load_from_file')
    @patch('env_diff.cli.compare_envs')
    def test_compare_two_files(self, mock_compare, mock_load, runner):
        mock_load.return_value = {'KEY': 'value'}
        mock_compare.return_value = {
            'added': {},
            'removed': {},
            'changed': {},
            'unchanged': {'KEY': 'value'}
        }
        
        with runner.isolated_filesystem():
            with open('file1.env', 'w') as f:
                f.write('KEY=value')
            with open('file2.env', 'w') as f:
                f.write('KEY=value')
            
            result = runner.invoke(main, ['file1.env', 'file2.env'])
            assert result.exit_code == 0
    
    @patch('env_diff.cli.load_from_pid')
    @patch('env_diff.cli.compare_envs')
    def test_compare_two_pids(self, mock_compare, mock_load, runner):
        mock_load.return_value = {'KEY': 'value'}
        mock_compare.return_value = {
            'added': {},
            'removed': {},
            'changed': {},
            'unchanged': {}
        }
        
        result = runner.invoke(main, ['--pid1', '1234', '--pid2', '5678'])
        assert result.exit_code == 0
    
    @patch('env_diff.cli.load_from_stdin')
    @patch('env_diff.cli.load_from_file')
    @patch('env_diff.cli.compare_envs')
    def test_stdin_mode(self, mock_compare, mock_load_file, mock_load_stdin, runner):
        mock_load_stdin.return_value = {'KEY1': 'value1'}
        mock_load_file.return_value = {'KEY2': 'value2'}
        mock_compare.return_value = {
            'added': {'KEY2': 'value2'},
            'removed': {'KEY1': 'value1'},
            'changed': {},
            'unchanged': {}
        }
        
        with runner.isolated_filesystem():
            with open('file.env', 'w') as f:
                f.write('KEY2=value2')
            
            result = runner.invoke(main, ['--stdin', 'file.env'], input='KEY1=value1')
            assert result.exit_code == 0
    
    @patch('env_diff.cli.load_from_file')
    @patch('env_diff.cli.compare_envs')
    def test_json_output_format(self, mock_compare, mock_load, runner):
        mock_load.return_value = {'KEY': 'value'}
        mock_compare.return_value = {
            'added': {'NEW': 'val'},
            'removed': {},
            'changed': {},
            'unchanged': {}
        }
        
        with runner.isolated_filesystem():
            with open('f1.env', 'w') as f:
                f.write('KEY=value')
            with open('f2.env', 'w') as f:
                f.write('KEY=value')
            
            result = runner.invoke(main, ['f1.env', 'f2.env', '--format', 'json'])
            assert result.exit_code == 0
            assert 'added' in result.output


class TestLoadSource:
    @patch('env_diff.cli.load_from_pid')
    def test_load_from_pid(self, mock_load):
        mock_load.return_value = {'KEY': 'value'}
        result = _load_source('dummy', pid=1234)
        mock_load.assert_called_once_with(1234)
    
    @patch('env_diff.cli.load_from_file')
    def test_load_from_file(self, mock_load):
        mock_load.return_value = {'KEY': 'value'}
        result = _load_source('file.env')
        mock_load.assert_called_once_with('file.env')
