import json
import subprocess
from enum import Enum

import typer
import uvicorn  # type: ignore
import yaml

from iac_scan_runner.object_store import app
from iac_scan_runner.object_store import scan_runner
from iac_scan_runner.routers import openapi as open_api, checks, project
from iac_scan_runner.routers.openapi import openapi_yaml

cli = typer.Typer(help="IaC Scan Runner CLI", context_settings={"help_option_names": ["-h", "--help"]})


class OpenApiFormat(str, Enum):
    """Open API format class object."""

    JSON = "json"
    YAML = "yaml"


@cli.command(help="Get OpenAPI specification")
def openapi(
        output_format: OpenApiFormat = typer.Option(OpenApiFormat.JSON, "--format", "-f", help="OpenAPI output format",
                                                    case_sensitive=False),
        output: str = typer.Option(None, "--output", "-o", help="Output file path")) -> None:
    """
    Get OpenAPI specification.

    :param output_format: OpenAPI output format (JSON or YAML)
    :param output: Output file path name, where OpenAPI specification will be written to
    """
    try:
        if output_format == OpenApiFormat.JSON:
            openapi_spec = app.openapi()
        else:
            openapi_spec = openapi_yaml()

        if output:
            with open(output, "w", encoding="utf-8") as f:
                if output_format == OpenApiFormat.JSON:
                    json.dump(openapi_spec, f, indent=2)
                else:
                    yaml.dump(yaml.safe_load(openapi_spec), f, indent=2)
        else:
            typer.echo(openapi_spec)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@cli.command(help="Install prerequisites for IaC Scan Runner")
def install() -> None:
    """Install prerequisites for IaC Scan Runner."""
    try:
        command = subprocess.call("./install-checks.sh")
        if command != 0:
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@cli.command(help="Run REST API for IaC Scan Runner")
def run() -> None:
    """Run REST API for IaC Scan Runner."""
    try:
        # initialize checks
        scan_runner.init_checks()

        # add routers
        app.include_router(open_api.router)
        app.include_router(checks.router)
        app.include_router(project.router)

        # run app
        uvicorn.run(app)
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


# this object is needed to get docs for sphinx-click Sphinx documentation module
typer_click_object = typer.main.get_command(cli)
