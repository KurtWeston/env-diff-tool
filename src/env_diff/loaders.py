"""Load environment variables from different sources."""
import os
import sys
import re
from typing import Dict
import psutil
from dotenv import dotenv_values

def load_from_pid(pid: int) -> Dict[str, str]:
    """Load environment variables from a running process."""
    try:
        process = psutil.Process(pid)
        return process.environ()
    except psutil.NoSuchProcess:
        raise ValueError(f"No process found with PID {pid}")
    except psutil.AccessDenied:
        raise ValueError(f"Access denied to process {pid}. Try running with elevated privileges.")

def load_from_file(filepath: str) -> Dict[str, str]:
    """Load environment variables from .env file or shell export script."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if _is_shell_script(content):
        return _parse_shell_exports(content)
    else:
        return dict(dotenv_values(filepath))

def load_from_stdin() -> Dict[str, str]:
    """Load environment variables from stdin."""
    content = sys.stdin.read()
    
    if _is_shell_script(content):
        return _parse_shell_exports(content)
    else:
        lines = content.strip().split('\n')
        env = {}
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                env[key.strip()] = value.strip().strip('"\'')
        return env

def _is_shell_script(content: str) -> bool:
    """Detect if content is a shell export script."""
    return 'export ' in content or content.strip().startswith('#!')

def _parse_shell_exports(content: str) -> Dict[str, str]:
    """Parse shell export statements."""
    env = {}
    export_pattern = re.compile(r'^export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$', re.MULTILINE)
    
    for match in export_pattern.finditer(content):
        key = match.group(1)
        value = match.group(2).strip()
        value = value.strip('"\'')
        env[key] = value
    
    return env