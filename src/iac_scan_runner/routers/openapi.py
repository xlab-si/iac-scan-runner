import functools
import io

import yaml
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["test"])


def openapi_yaml() -> str:
    """
    Return OpenAPI specification as YAML string

    :return: string with YAML
    """
    openapi_json = router.openapi()
    yaml_str = io.StringIO()
    yaml.dump(openapi_json, yaml_str)
    return yaml_str.getvalue()


@router.get('/openapi.yml', include_in_schema=False)
@functools.lru_cache()
def get_openapi_yml() -> Response:
    """
    GET OpenAPI specification in YAML format (.yml)

    :return: Response object
    """
    return Response(openapi_yaml(), media_type='text/yml')


@router.get('/openapi.yaml', include_in_schema=False)
@functools.lru_cache()
def get_openapi_yaml() -> Response:
    """
    GET OpenAPI specification in YAML format (.yaml)

    :return: Response object
    """
    return Response(openapi_yaml(), media_type='text/yaml')
