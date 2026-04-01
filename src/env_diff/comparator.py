"""Core comparison logic for environment variables."""
import re
from typing import Dict, Set

def compare_envs(env1: Dict[str, str], env2: Dict[str, str]) -> Dict:
    """Compare two environment dictionaries and return structured diff."""
    keys1 = set(env1.keys())
    keys2 = set(env2.keys())
    
    added = keys2 - keys1
    removed = keys1 - keys2
    common = keys1 & keys2
    
    changed = {}
    unchanged = {}
    
    for key in common:
        if env1[key] != env2[key]:
            changed[key] = {'old': env1[key], 'new': env2[key]}
        else:
            unchanged[key] = env1[key]
    
    return {
        'added': {k: env2[k] for k in added},
        'removed': {k: env1[k] for k in removed},
        'changed': changed,
        'unchanged': unchanged
    }

def filter_vars(diff: Dict, include: str = None, exclude: str = None) -> Dict:
    """Filter diff results by variable name patterns."""
    include_pattern = re.compile(include) if include else None
    exclude_pattern = re.compile(exclude) if exclude else None
    
    def should_include(key: str) -> bool:
        if include_pattern and not include_pattern.search(key):
            return False
        if exclude_pattern and exclude_pattern.search(key):
            return False
        return True
    
    return {
        'added': {k: v for k, v in diff['added'].items() if should_include(k)},
        'removed': {k: v for k, v in diff['removed'].items() if should_include(k)},
        'changed': {k: v for k, v in diff['changed'].items() if should_include(k)},
        'unchanged': {k: v for k, v in diff['unchanged'].items() if should_include(k)}
    }

def mask_sensitive(value: str, key: str) -> str:
    """Mask sensitive values based on key patterns."""
    sensitive_patterns = ['password', 'token', 'key', 'secret', 'api', 'auth']
    
    key_lower = key.lower()
    if any(pattern in key_lower for pattern in sensitive_patterns):
        if len(value) <= 4:
            return '***'
        return value[:2] + '*' * (len(value) - 4) + value[-2:]
    
    return value