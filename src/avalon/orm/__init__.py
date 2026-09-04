"""Eloquent-like ORM over SQLAlchemy Core (async-first)."""

from avalon.orm.builder import ModelNotFoundError, QueryBuilder
from avalon.orm.casts import CastError
from avalon.orm.collection import Collection
from avalon.orm.connection import Connection, DatabaseManager
from avalon.orm.facade import DB, get_manager, raw, set_manager
from avalon.orm.migration import Migration, Migrator, guess_migration, make_migration
from avalon.orm.model import (
    MassAssignmentError,
    Model,
    RelationNotLoadedError,
    relation,
)
from avalon.orm.pagination import Paginator, SimplePaginator
from avalon.orm.provider import DatabaseServiceProvider
from avalon.orm.relations import (
    BelongsTo,
    BelongsToMany,
    HasMany,
    HasManyThrough,
    HasOne,
    HasOneThrough,
    MorphMany,
    MorphOne,
    MorphTo,
    MorphToMany,
    Relation,
)
from avalon.orm.schema import Blueprint, Schema, SchemaError
from avalon.orm.seeder import (
    Seeder,
    SeederError,
    WithoutModelEvents,
    invoke_seeder,
    load_database_seeder,
    make_seeder,
    reset_called,
    resolve_seeder_class,
    run_seeder,
    without_model_events,
)
from avalon.orm.soft_deletes import SoftDeletes

__all__ = [
    "DB",
    "BelongsTo",
    "BelongsToMany",
    "Blueprint",
    "CastError",
    "Collection",
    "Connection",
    "DatabaseManager",
    "DatabaseServiceProvider",
    "HasMany",
    "HasManyThrough",
    "HasOne",
    "HasOneThrough",
    "MassAssignmentError",
    "Migration",
    "Migrator",
    "Model",
    "ModelNotFoundError",
    "MorphMany",
    "MorphOne",
    "MorphTo",
    "MorphToMany",
    "Paginator",
    "QueryBuilder",
    "Relation",
    "RelationNotLoadedError",
    "Schema",
    "SchemaError",
    "Seeder",
    "SeederError",
    "SimplePaginator",
    "SoftDeletes",
    "WithoutModelEvents",
    "get_manager",
    "guess_migration",
    "invoke_seeder",
    "load_database_seeder",
    "make_migration",
    "make_seeder",
    "raw",
    "relation",
    "reset_called",
    "resolve_seeder_class",
    "run_seeder",
    "set_manager",
    "without_model_events",
]
