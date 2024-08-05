from typing import TypeVar

from httpx import Response
from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def verify_json_item_structure(
    response: Response,
    validation_schema: type[SchemaT],
) -> SchemaT:
    return validation_schema(**response.json())


def verify_json_list_structure(
    response: Response, validation_schema: type[SchemaT]
) -> list[SchemaT]:
    return [validation_schema(**item) for item in response.json()]
