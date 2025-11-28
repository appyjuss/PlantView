"""Generic single-database configuration."""
from alembic import config as alembic_config

# Determine the config from the environment instead of
# guessing based on default values. This allows external
# projects to configure logging, use another config file
# for alembic etc.
fileConfig = alembic_config.FileConfig("alembic.ini")

# Provide support to exclude objects from the automatic
# migration by defining them here and then using the
# configure_models callable in env.py
# exclude_tables_from_auto_migrate = ["quarantine_table"]


def include_object(obj, name, type_, reflected, compare_to):
    """Configure which objects should be migrated."""
    if type_ == "table":
        return True
    elif type_ == "index":
        return True
    else:
        return True
