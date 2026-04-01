"""Output formatters for different formats."""
import json
import csv
import io
from typing import Dict
from rich.table import Table
from rich.text import Text
from .comparator import mask_sensitive

def format_terminal(diff: Dict, show_all: bool, mask: bool, sort_by: str) -> Table:
    """Format diff as colorized terminal table."""
    table = Table(title="Environment Variable Comparison")
    table.add_column("Variable", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Value")
    
    rows = []
    
    for key, value in diff['added'].items():
        val = mask_sensitive(value, key) if mask else value
        rows.append((key, 'added', Text(f"+ {val}", style="green"), 0))
    
    for key, value in diff['removed'].items():
        val = mask_sensitive(value, key) if mask else value
        rows.append((key, 'removed', Text(f"- {val}", style="red"), 1))
    
    for key, values in diff['changed'].items():
        old_val = mask_sensitive(values['old'], key) if mask else values['old']
        new_val = mask_sensitive(values['new'], key) if mask else values['new']
        rows.append((key, 'changed', Text(f"{old_val} → {new_val}", style="yellow"), 2))
    
    if show_all:
        for key, value in diff['unchanged'].items():
            val = mask_sensitive(value, key) if mask else value
            rows.append((key, 'unchanged', Text(val, style="dim"), 3))
    
    if sort_by == 'alpha':
        rows.sort(key=lambda x: x[0])
    else:
        rows.sort(key=lambda x: (x[3], x[0]))
    
    for key, status, value, _ in rows:
        table.add_row(key, status, value)
    
    return table

def format_json(diff: Dict, show_all: bool, mask: bool) -> str:
    """Format diff as JSON."""
    output = {
        'added': {},
        'removed': {},
        'changed': {}
    }
    
    for key, value in diff['added'].items():
        output['added'][key] = mask_sensitive(value, key) if mask else value
    
    for key, value in diff['removed'].items():
        output['removed'][key] = mask_sensitive(value, key) if mask else value
    
    for key, values in diff['changed'].items():
        output['changed'][key] = {
            'old': mask_sensitive(values['old'], key) if mask else values['old'],
            'new': mask_sensitive(values['new'], key) if mask else values['new']
        }
    
    if show_all:
        output['unchanged'] = {}
        for key, value in diff['unchanged'].items():
            output['unchanged'][key] = mask_sensitive(value, key) if mask else value
    
    return json.dumps(output, indent=2)

def format_csv(diff: Dict, show_all: bool, mask: bool) -> str:
    """Format diff as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Variable', 'Status', 'Old Value', 'New Value'])
    
    for key, value in sorted(diff['added'].items()):
        val = mask_sensitive(value, key) if mask else value
        writer.writerow([key, 'added', '', val])
    
    for key, value in sorted(diff['removed'].items()):
        val = mask_sensitive(value, key) if mask else value
        writer.writerow([key, 'removed', val, ''])
    
    for key, values in sorted(diff['changed'].items()):
        old_val = mask_sensitive(values['old'], key) if mask else values['old']
        new_val = mask_sensitive(values['new'], key) if mask else values['new']
        writer.writerow([key, 'changed', old_val, new_val])
    
    if show_all:
        for key, value in sorted(diff['unchanged'].items()):
            val = mask_sensitive(value, key) if mask else value
            writer.writerow([key, 'unchanged', val, val])
    
    return output.getvalue()