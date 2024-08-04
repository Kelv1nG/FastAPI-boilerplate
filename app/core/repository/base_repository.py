from typing import Any, ClassVar, Protocol, TypeVar, runtime_checkable

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapper
from sqlalchemy.sql import FromClause

from . import exceptions


@runtime_checkable
class ModelProtocol(Protocol):
    """base sqlalchemy model protocol"""

    __table__: ClassVar[FromClause]
    __mapper__: ClassVar[Mapper[Any]]


ModelT = TypeVar("ModelT", bound=ModelProtocol)


class AsyncBaseRepositoryProtocol(Protocol[ModelT]):
    model_type: type[ModelT]


class AsyncBaseRepository(AsyncBaseRepositoryProtocol[ModelT]):
    model_type: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, model: ModelT, commit: bool = False) -> ModelT:
        self.session.add(model)
        await self._commit_or_flush(commit=commit)
        return model

    async def update(self, model: ModelT, data: dict, commit: bool = False) -> ModelT:
        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)
        self.session.add(model)
        await self._commit_or_flush(commit=commit)
        return model

    async def delete(self, model: ModelT, commit: bool = False) -> None:
        await self.session.delete(model)
        await self._commit_or_flush(commit)

    async def get(
        self, value: int | str, attribute: str = "id", load_stmt: list | None = None
    ) -> ModelT | None:
        """
        Retrieves a single instance of a model based on a specified attribute and its value.

        Args:
            value (int | str): The value of the attribute to search for.
                Typically, this is the primary key value.
            attribute (str, optional): The name of the attribute to filter by.
                Defaults to "id".
            load_stmt (list, optional): A list of additional SQLAlchemy load options,
                such as relationships to eagerly load. Defaults to None.

        Returns:
            ModelT | None: An instance of the model if exactly one match is found, or None if no matching record is found.

        Raises:
            sqlalchemy.orm.exc.MultipleResultsFound: If more than one record matches the given criteria.
        """

        init_query = self._get_by_attribute(attribute, value)
        query = self._add_load_stmt(init_query, load_stmt)

        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_one_or_none(
        self, query_stmt: Select, load_stmt: list | None = None
    ) -> ModelT | None:
        query = self._add_load_stmt(query_stmt, load_stmt)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def all(
        self, query_stmt: Select | None = None, load_stmt: list | None = None
    ) -> list[ModelT]:
        if query_stmt is None:
            query_stmt = select(self.model_type)

        query = self._add_load_stmt(query_stmt, load_stmt)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    def _get_by_attribute(self, attribute: str, value: Any) -> Select:
        if not hasattr(self.model_type, attribute):
            raise exceptions.InvalidModelAttributeException()

        query = select(self.model_type).where(
            getattr(self.model_type, attribute) == value
        )
        return query

    def _add_load_stmt(self, query: Select, load_stmt: list | None):
        if load_stmt:
            query = query.options(*load_stmt)
        return query

    async def _commit_or_flush(self, commit: bool):
        if commit:
            await self.session.commit()
        else:
            await self.session.flush()
