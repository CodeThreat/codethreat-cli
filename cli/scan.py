import click


@click.command()
@click.option('--target', required=True, help='Path to the target codebase')
@click.option('--project', required=True, help='Project name in CodeThreat')
def scan(target, project):
    """Run a SAST scan on the specified target."""
    click.echo(f'Scanning target: {target} in project: {project}')
    # Logic to connect to the CodeThreat API and trigger the scan
