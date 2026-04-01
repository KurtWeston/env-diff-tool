"""Click-based CLI interface for env-diff."""
import sys
import click
from rich.console import Console
from .loaders import load_from_pid, load_from_file, load_from_stdin
from .comparator import compare_envs, filter_vars
from .formatters import format_terminal, format_json, format_csv

console = Console()

@click.command()
@click.argument('source1', required=False)
@click.argument('source2', required=False)
@click.option('--pid1', type=int, help='First process ID')
@click.option('--pid2', type=int, help='Second process ID')
@click.option('--format', type=click.Choice(['terminal', 'json', 'csv']), default='terminal', help='Output format')
@click.option('--all', 'show_all', is_flag=True, help='Show all variables, not just differences')
@click.option('--mask/--no-mask', default=True, help='Mask sensitive values')
@click.option('--include', help='Include only variables matching pattern')
@click.option('--exclude', help='Exclude variables matching pattern')
@click.option('--sort', type=click.Choice(['alpha', 'type']), default='alpha', help='Sort order')
@click.option('--stdin', is_flag=True, help='Read first source from stdin')
def main(source1, source2, pid1, pid2, format, show_all, mask, include, exclude, sort, stdin):
    """Compare environment variables between two sources.
    
    Sources can be PIDs, .env files, or shell export scripts.
    Use --pid1/--pid2 for process comparison, or provide file paths as arguments.
    """
    try:
        if stdin:
            env1 = load_from_stdin()
            if not source1:
                console.print("[red]Error: Second source required when using --stdin[/red]", file=sys.stderr)
                sys.exit(1)
            env2 = _load_source(source1, pid2)
        elif pid1 and pid2:
            env1 = load_from_pid(pid1)
            env2 = load_from_pid(pid2)
        elif source1 and source2:
            env1 = _load_source(source1, pid1)
            env2 = _load_source(source2, pid2)
        else:
            console.print("[red]Error: Provide either two file paths or --pid1 and --pid2[/red]", file=sys.stderr)
            sys.exit(1)
        
        diff = compare_envs(env1, env2)
        
        if include or exclude:
            diff = filter_vars(diff, include, exclude)
        
        if format == 'terminal':
            output = format_terminal(diff, show_all, mask, sort)
            console.print(output)
        elif format == 'json':
            output = format_json(diff, show_all, mask)
            print(output)
        elif format == 'csv':
            output = format_csv(diff, show_all, mask)
            print(output)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]", file=sys.stderr)
        sys.exit(1)

def _load_source(source, pid=None):
    """Load environment from source (file or PID)."""
    if pid:
        return load_from_pid(pid)
    return load_from_file(source)

if __name__ == '__main__':
    main()