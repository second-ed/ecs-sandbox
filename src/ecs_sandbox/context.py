from enum import StrEnum, unique
from functools import reduce
from typing import Any

import attrs
import polars as pl

from ecs_sandbox.components import Components


@unique
class PrimaryKeys(StrEnum):
    ENTITY_ID = "entity_id"


@attrs.define
class Context:
    tables: dict[Components, pl.DataFrame] = attrs.field(factory=dict)

    def __attrs_post_init__(self) -> None:
        self.tables = {comp: pl.DataFrame() for comp in Components._member_map_.values()}

    def create_entity(self, entity_id: int, **components: dict[str, Components]) -> None:
        for comp_name, value in components.items():
            table = self.tables[comp_name]
            if table.is_empty() or entity_id not in table[PrimaryKeys.ENTITY_ID.value].to_list():
                new_row = pl.DataFrame(
                    {PrimaryKeys.ENTITY_ID.value: [entity_id], comp_name: [value]}
                )
                self.tables[comp_name] = pl.concat([table, new_row], how="vertical")

    def query_components(
        self,
        *,
        on: str = PrimaryKeys.ENTITY_ID.value,
        **components: dict[str, Components],
    ) -> pl.DataFrame:
        joined_df = self._join_components(on=on)
        return self._create_filtered_df(joined_df, **components)

    def update_entity_component(
        self,
        entity_id: int,
        component_name: Components,
        new_value: Any,  # noqa: ANN401
    ) -> None:
        table = self.tables[component_name]
        if entity_id in table[PrimaryKeys.ENTITY_ID.value].to_list():
            table = table.with_columns(
                [
                    pl.when(pl.col(PrimaryKeys.ENTITY_ID.value) == entity_id)
                    .then(pl.lit(new_value))
                    .otherwise(pl.col(component_name))
                    .alias(component_name)
                ]
            )
            self.tables[component_name] = table

    def delete_entity(self, entity_id: int) -> None:
        for name, table in self.tables.items():
            self.tables[name] = table.filter(pl.col(PrimaryKeys.ENTITY_ID.value) != entity_id)

    def _join_components(self, *, on: str = PrimaryKeys.ENTITY_ID.value) -> pl.DataFrame:
        non_empty_tables = [t for t in self.tables.values() if not t.is_empty()]
        if not non_empty_tables:
            return pl.DataFrame({on: pl.Series([], dtype=pl.Int64)})
        return reduce(lambda left, right: left.join(right, on=on, how="inner"), non_empty_tables)

    def _create_filtered_df(
        self, joined: pl.DataFrame, **filters: dict[str, Components]
    ) -> pl.DataFrame:
        if not filters:
            return joined

        combined = reduce(lambda x, y: x & y, [(pl.col(k) == v) for k, v in filters.items()])
        return joined.filter(combined)
