from enum import Enum
from typing import Dict, Optional, Type

from app.database.db import DatabaseClient
from app.database.mongodb import MongoDBClient
from app.database.sqlalchemy_client import SQLAlchemyClient, Base


class DatabaseType(str, Enum):
    """Supported database types"""
    MONGODB = "mongodb"
    SQLALCHEMY = "sqlalchemy"


class DatabaseFactory:
    """Factory for creating database clients"""
    
    @staticmethod
    async def create_client(
        db_type: DatabaseType,
        connection_string: str,
        database_name: str = "app",
        model_registry: Optional[Dict[str, Type[Base]]] = None,
        echo: bool = False
    ) -> DatabaseClient:
        """
        Create a database client based on the specified type
        
        Args:
            db_type: Type of database to use
            connection_string: Database connection string
            database_name: Name of the database (for MongoDB)
            model_registry: Dictionary mapping collection names to SQLAlchemy models (for SQLAlchemy)
            echo: Whether to echo SQL statements (for SQLAlchemy)
            
        Returns:
            Configured database client
        """
        if db_type == DatabaseType.MONGODB:
            client = MongoDBClient(connection_string, database_name)
        elif db_type == DatabaseType.SQLALCHEMY:
            if not model_registry:
                raise ValueError("model_registry is required for SQLAlchemy client")
            client = SQLAlchemyClient(connection_string, model_registry, echo)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Connect to the database
        await client.connect()
        
        return client
