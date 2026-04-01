"""Tests for comparator module."""
import pytest
from env_diff.comparator import compare_envs, filter_vars, mask_sensitive


class TestCompareEnvs:
    def test_compare_identical_envs(self):
        env1 = {'KEY1': 'value1', 'KEY2': 'value2'}
        env2 = {'KEY1': 'value1', 'KEY2': 'value2'}
        result = compare_envs(env1, env2)
        
        assert result['added'] == {}
        assert result['removed'] == {}
        assert result['changed'] == {}
        assert result['unchanged'] == {'KEY1': 'value1', 'KEY2': 'value2'}
    
    def test_compare_with_additions(self):
        env1 = {'KEY1': 'value1'}
        env2 = {'KEY1': 'value1', 'KEY2': 'value2'}
        result = compare_envs(env1, env2)
        
        assert result['added'] == {'KEY2': 'value2'}
        assert result['removed'] == {}
    
    def test_compare_with_removals(self):
        env1 = {'KEY1': 'value1', 'KEY2': 'value2'}
        env2 = {'KEY1': 'value1'}
        result = compare_envs(env1, env2)
        
        assert result['removed'] == {'KEY2': 'value2'}
        assert result['added'] == {}
    
    def test_compare_with_changes(self):
        env1 = {'KEY1': 'old_value'}
        env2 = {'KEY1': 'new_value'}
        result = compare_envs(env1, env2)
        
        assert result['changed'] == {'KEY1': {'old': 'old_value', 'new': 'new_value'}}
    
    def test_compare_empty_envs(self):
        result = compare_envs({}, {})
        assert all(not result[k] for k in ['added', 'removed', 'changed', 'unchanged'])


class TestFilterVars:
    def test_filter_with_include_pattern(self):
        diff = {
            'added': {'DB_HOST': 'localhost', 'API_KEY': 'secret'},
            'removed': {'OLD_VAR': 'value'},
            'changed': {},
            'unchanged': {}
        }
        result = filter_vars(diff, include='DB_.*')
        
        assert 'DB_HOST' in result['added']
        assert 'API_KEY' not in result['added']
    
    def test_filter_with_exclude_pattern(self):
        diff = {
            'added': {'DB_HOST': 'localhost', 'API_KEY': 'secret'},
            'removed': {},
            'changed': {},
            'unchanged': {}
        }
        result = filter_vars(diff, exclude='API_.*')
        
        assert 'DB_HOST' in result['added']
        assert 'API_KEY' not in result['added']
    
    def test_filter_no_patterns(self):
        diff = {'added': {'KEY': 'value'}, 'removed': {}, 'changed': {}, 'unchanged': {}}
        result = filter_vars(diff)
        assert result == diff


class TestMaskSensitive:
    def test_mask_password(self):
        result = mask_sensitive('mypassword123', 'DB_PASSWORD')
        assert result == 'my*********23'
    
    def test_mask_token(self):
        result = mask_sensitive('token_abc123', 'API_TOKEN')
        assert result == 'to*********23'
    
    def test_mask_short_value(self):
        result = mask_sensitive('abc', 'SECRET_KEY')
        assert result == '***'
    
    def test_no_mask_non_sensitive(self):
        result = mask_sensitive('normal_value', 'DB_HOST')
        assert result == 'normal_value'
    
    def test_mask_case_insensitive(self):
        result = mask_sensitive('secretvalue', 'my_SECRET')
        assert result.startswith('se') and result.endswith('ue')
