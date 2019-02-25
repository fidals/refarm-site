import abc
import typing

from django.db.migrations.operations.base import Operation
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

# @todo #283:30m Group models.py, models_operations.py, models_expressions.py into the module.


class IndexSQL(abc.ABC):

    def __init__(self, name: str):
        self.name = name

    def _index_name(self, table: str):
        return f'{table}_{self.name}_idx'

    @abc.abstractmethod
    def execute(self, table: str, schema_editor: BaseDatabaseSchemaEditor):
        """Execute SQL operation."""


class AddIndex(IndexSQL):

    def __init__(self, name: str, columns: typing.List[str]):
        self.name = name
        self.columns = columns

    def execute(self, table, schema_editor):
        schema_editor.execute(
            f'CREATE INDEX {self._index_name(table)} ON {table}'
            f'({", ".join(self.columns)});'
        )


class DropIndex(IndexSQL):

    def execute(self, table, schema_editor):
        schema_editor.execute(
            f'DROP INDEX {self._index_name(table)};'
        )


class IndexOperation(Operation):
    """
    Operate an index by given IndexSQL objects.

    Docs: https://docs.djangoproject.com/en/1.11/ref/migration-operations/#writing-your-own
    """

    reduces_to_sql = True
    reversible = True

    def __init__(self, model_name, forward: IndexSQL, backward: IndexSQL):
        self.model_name = model_name
        self.forward = forward
        self.backward = backward

    def state_forwards(self, app_label, state):
        """We have to implement this method for Operation interface."""

    def database_forwards(self, app_label, schema_editor, _, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            table_name = to_model._meta.db_table
            self.forward.execute(table_name, schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, _):
        from_model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, from_model):
            table_name = from_model._meta.db_table
            self.backward.execute(table_name, schema_editor)

    def describe(self):
        return f'Operate the index {self.name} for {self.model_name}'


class RevertOperation(Operation):

    reduces_to_sql = True
    reversible = True

    def __init__(self, operation: IndexOperation):
        self.operation = operation

    def state_forwards(self, app_label, state):
        """We have to implement this method for Operation interface."""

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.operation.database_backwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.operation.database_forwards(app_label, schema_editor, from_state, to_state)



# Django doesn't provide ability to add hooks to makemigrations.
# So we have to create migration files and add operations for
# abstract classes (like Tag) manually.
class IndexTagAlphanumeric:

    ALPHANUMERIC_NAME = 'alphanumeric_name'
    MODEL_NAME = 'tag'

    def v1(self) -> typing.List[IndexOperation]:
        return [IndexOperation(
            model_name=self.MODEL_NAME,
            forward=AddIndex(
                name=self.ALPHANUMERIC_NAME,
                columns=[
                    "substring(name, '[a-zA-Zа-яА-Я]+')",
                    "(substring(name, '[0-9]+\.?[0-9]*')::float)",
                ],
            ),
            backward=DropIndex(name=self.ALPHANUMERIC_NAME),
        )]

    def v2(self) -> typing.List[IndexOperation]:
        """Preserve whitespaces for alphabetic values of the index."""
        old = self.v1()[0]
        return [
            RevertOperation(old),
            IndexOperation(
                model_name=self.MODEL_NAME,
                forward=AddIndex(
                    name=self.ALPHANUMERIC_NAME,
                    columns=[
                        "substring(name, '[a-zA-Zа-яА-Я\s]+')",
                        "(substring(name, '[0-9]+\.?[0-9]*')::float)",
                    ],
                ),
                backward=DropIndex(name=self.ALPHANUMERIC_NAME),
            ),
        ]
