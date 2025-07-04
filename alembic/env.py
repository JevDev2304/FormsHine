import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

# Obtener la URL desde el archivo .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuración de Alembic
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configuración de logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar el modelo a cambiar
from app.models.child import Children
target_metadata = Children.metadata



def run_migrations_offline():
    """Migraciones en modo offline"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Migraciones en modo online"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
