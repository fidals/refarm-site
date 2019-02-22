from django.db.migrations.operations.base import Operation

# @todo #283:30m Group models.py, models_operations.py, models_expressions.py into the module.


class AddIndexSQL(Operation):
    """
    Create a B-Tree index by given columns or expressions.

    Docs: https://docs.djangoproject.com/en/1.11/ref/migration-operations/#writing-your-own
    """

    reduces_to_sql = True
    reversible = True

    def __init__(self, name, columns, model_name):
        self.name = name
        self.columns = columns
        self.model_name = model_name

    def state_forwards(self, app_label, state):
        """We have to implement this method for Operation interface."""

    def _index_name(self, table_name):
        return f'{table_name}_{self.name}_idx'

    def database_forwards(self, app_label, schema_editor, _, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            table_name = to_model._meta.db_table
            schema_editor.execute(
                f'CREATE INDEX {self._index_name(table_name)} ON {table_name}'
                f'({", ".join(self.columns)});'
            )

    def database_backwards(self, app_label, schema_editor, from_state, _):
        from_model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, from_model):
            table_name = from_model._meta.db_table
            schema_editor.execute(
                f'DROP INDEX {self._index_name(table_name)};'
            )

    def describe(self):
        return f'Create index {self.name} for {self.model_name}'

# Django doesn't provide ability to add hooks to makemigrations.
# So we have to create migration files and add operations for
# abstract classes (like Tag) manually.
index_alphanumeric_tag_name = AddIndexSQL(
    name='alphanumeric_name',
    columns=[
        "substring(name, '[a-zA-Zа-яА-Я]+')",
        "(substring(name, '[0-9]+\.?[0-9]*')::float)"
    ],
    model_name='tag',
)
