import json
import subprocess
from enum import Enum

import typer
import uvicorn
import yaml
from iac_scan_runner.api import app, openapi_yaml

cli = typer.Typer(help="IaC Scan Runner CLI", context_settings={"help_option_names": ["-h", "--help"]})


class OpenApiFormat(str, Enum):
    json = "json"
    yaml = "yaml"


@cli.command(help="Get OpenAPI specification")
def openapi(
        output_format: OpenApiFormat = typer.Option(OpenApiFormat.json, "--format", "-f", help="OpenAPI output format",
                                                    case_sensitive=False),
        output: str = typer.Option(None, "--output", "-o", help="Output file path")):
    """
    Get OpenAPI specification

    :param output_format: OpenAPI output format (JSON or YAML)
    :param output: Output file path name, where OpenAPI specification will be written to
    """
    try:
        if output_format == OpenApiFormat.json:
            openapi_spec = app.openapi()
        else:
            openapi_spec = openapi_yaml()

        if output:
            with open(output, 'w') as f:
                if output_format == OpenApiFormat.json:
                    json.dump(openapi_spec, f, indent=2)
                else:
                    yaml.dump(yaml.safe_load(openapi_spec), f, indent=2)
        else:
            typer.echo(openapi_spec)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@cli.command(help="Install prerequisites for IaC Scan Runner")
def install():
    """
    Install prerequisites for IaC Scan Runner
    """
    try:
        rc = subprocess.call('./install-checks.sh')
        if rc != 0:
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@cli.command(help="Run REST API for IaC Scan Runner")
def run():
    """
    Run REST API for IaC Scan Runner
    """
    try:
        uvicorn.run(app)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


# this object is needed to get docs for sphinx-click Sphinx documentation module
typer_click_object = typer.main.get_command(cli)
