import json
import subprocess
import os
import mimetypes
from enum import Enum
from typing import List, Optional

import typer
import uvicorn  # type: ignore
import yaml
import requests

import iac_scan_runner.vars as env
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


@cli.command(help="List checks and their properties")
def get_checks(keyword: Optional[str] = None, enabled: Optional[bool] = None,
               configured: Optional[bool] = None, target_entity_type: Optional[str] = None) -> None:
    """List all checks and their properties."""
    try:
        args = []
        if keyword:
            args.append(f"keyword={keyword}")
        if enabled is not None:
            args.append(f"enabled={enabled}")
        if configured is not None:
            args.append(f"configured={configured}")
        if target_entity_type in ["IaC", "component", "IaC and component"]:
            args.append(f"target_entity_type={target_entity_type}")
        if args:
            _url = f"{env.SERVER_HOST}/default/checks?{'&'.join(args)}"
        else:
            _url = f"{env.SERVER_HOST}/default/checks"

        response = requests.get(url=_url)
        typer.echo(response.json())

    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=0)


@cli.command(help="Enable the selected check")
def enable_check(check_name: str) -> None:
    """Enable the selected check."""
    try:
        _url = f"{env.SERVER_HOST}/default/checks/{check_name}/enable"

        response = requests.put(url=_url)
        typer.echo(response.json())
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@cli.command(help="Disable the selected check")
def disable_check(check_name: str) -> None:
    """Disable the selected check."""
    try:
        _url = f"{env.SERVER_HOST}/default/checks/{check_name}/disable"

        response = requests.put(url=_url)
        typer.echo(response.json())
    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@cli.command(help="Configure the selected check using a config file and a secret")
def configure_check(check_name: str, config_file_path: Optional[str] = None,
                    secret: Optional[str] = None, mime_type: Optional[str] = None) -> None:
    """
    Configure the file using a config file and a secret.

    :param check_name: Name of the check to be configured
    :param file_path: Path to the config file
    :param secret: Secret used for the configuration of the check
    :param mime_type: Mime-type of the config file
    """
    try:
        _url = f"{env.SERVER_HOST}/default/checks/{check_name}/configure"
        _headers = {
            "accept": "application/json",
        }
        files_passed = False
        data_passed = False
        if config_file_path and os.path.exists(config_file_path) and mime_type:
            config_filename = config_file_path.split("/")[-1]
            file = open(config_file_path, "rb")
            _files = {
                "config_file": (config_filename, file, mime_type)
            }
            files_passed = True
        if secret:
            _data = {
                "secret": secret
            }
            data_passed = True

        if files_passed and data_passed:
            response = requests.put(url=_url, headers=_headers, files=_files, data=_data)
        elif files_passed:
            response = requests.put(url=_url, headers=_headers, files=_files)
        elif data_passed:
            response = requests.put(url=_url, headers=_headers, data=_data)
        else:
            response = requests.put(url=_url, headers=_headers)

        typer.echo(response.json())
        if files_passed:
            file.close()

    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@cli.command(help="Scan the your project provided in an archive with all enabled and configured checks")
def scan(scan_response_type: str, archive_path: str,
         checks: Optional[List[str]] = None) -> None:
    """
    Scan the provided archive using the enabled and configured checks.

    :param scan_response_type: Type of the response (JSON or HTML)
    :param archive_path: Path to the archive to be scanned
    :param checks: List of checks to be used during the scan, if empty all checks are used
    """
    try:
        _url = f"{env.SERVER_HOST}/default/scan?scan_response_type={scan_response_type}"
        mime_type = mimetypes.guess_type(archive_path)[0]
        archive_name = archive_path.split("/")[-1]
        archive = open(archive_path, "rb")

        _headers = {
            "accept": "application/json",
        }

        _data = {
            "checks": ",".join(checks) if checks else ""
        }

        _iac = {
            "iac": (archive_name, archive, mime_type)
        }

        response = requests.post(url=_url, headers=_headers, files=_iac, data=_data)
        if scan_response_type == "json":
            typer.echo(response.json())
        else:
            typer.echo(response.content.decode())

    except Exception as e:
        typer.echo(e)
        raise typer.Exit(code=1)


# this object is needed to get docs for sphinx-click Sphinx documentation module
typer_click_object = typer.main.get_command(cli)


if __name__ == "__main__":
    cli()
