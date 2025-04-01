from typing import Any, Dict, List, Optional, Type

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.database.db import DatabaseClient


Base = declarative_base()


class SQLAlchemyClient(DatabaseClient):
    """SQLAlchemy implementation of the DatabaseClient interface"""
    
    def __init__(
        self, 
        connection_string: str,
        model_registry: Dict[str, Type[Base]],
        echo: bool = False
    ):
        """
        Initialize SQLAlchemy client
        
        Args:
            connection_string: SQLAlchemy connection string
            model_registry: Dictionary mapping collection names to SQLAlchemy models
            echo: Whether to echo SQL statements
        """
        self.connection_string = connection_string
        self.model_registry = model_registry
        self.echo = echo
        self.engine = None
        self.async_session = None
    
    async def connect(self) -> None:
        """Connect to the database"""
        self.engine = create_async_engine(
            self.connection_string,
            echo=self.echo,
            future=True
        )
        
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        # Create tables if they don't exist
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        if self.engine:
            await self.engine.dispose()
    
    def _get_model_class(self, collection: str) -> Type[Base]:
        """Get the SQLAlchemy model class for a collection"""
        if collection not in self.model_registry:
            raise ValueError(f"No model registered for collection: {collection}")
        return self.model_registry[collection]
    
    def _model_to_dict(self, model: Base) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary"""
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            result[column.name] = value
        return result
    
    async def get_by_id(self, collection: str, id: Any) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        if not self.async_session:
            await self.connect()
            
        model_cls = self._get_model_class(collection)
        
        async with self.async_session() as session:
            stmt = select(model_cls).where(model_cls.id == id)
            result = await session.execute(stmt)
            model = result.scalars().first()
            
            if model:
                return self._model_to_dict(model)
            return None
    
    async def get_many(
        self, 
        collection: str, 
        filters: Optional[Dict[str, Any]] = None, 
        skip: int = 0, 
        limit: int = 100,
        sort: Optional[Dict[str, int]] = None
    ) -> List[Dict[str, Any]]:
        """Get multiple records with filtering, pagination and sorting"""
        if not self.async_session:
            await self.connect()
            
        model_cls = self._get_model_class(collection)
        
        async with self.async_session() as session:
            # Start with a base query
            stmt = select(model_cls)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(model_cls, key):
                        stmt = stmt.where(getattr(model_cls, key) == value)
            
            # Apply sorting
            if sort:
                for key, direction in sort.items():
                    if hasattr(model_cls, key):
                        column = getattr(model_cls, key)
                        stmt = stmt.order_by(column.desc() if direction == -1 else column)
            
            # Apply pagination
            stmt = stmt.offset(skip).limit(limit)
            
            # Execute query
            result = await session.execute(stmt)
            models = result.scalars().all()
            
            # Convert models to dictionaries
            return [self._model_to_dict(model) for model in models]
    
    async def create(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        if not self.async_session:
            await self.connect()
            
        model_cls = self._get_model_class(collection)
        
        # Create model instance
        model = model_cls(**document)
        
        async with self.async_session() as session:
            session.add(model)
            await session.commit()
            await session.refresh(model)
            
            return self._model_to_dict(model)
    
    async def update(
        self, 
        collection: str, 
        id: Any, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a record"""
        if not self.async_session:
            await self.connect()
            
        model_cls = self._get_model_class(collection)
        
        async with self.async_session() as session:
            # Get the record to update
            stmt = select(model_cls).where(model_cls.id == id)
            result = await session.execute(stmt)
            model = result.scalars().first()
            
            if not model:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            
            # Commit changes
            await session.commit()
            await session.refresh(model)
            
            return self._model_to_dict(model)
    
    async def delete(self, collection: str, id: Any) -> bool:
        """Delete a record"""
        if not self.async_session:
            await self.connect()
            
        model_cls = self._get_model_class(collection)
        
        async with self.async_session() as session:
            # Get the record to delete
            stmt = select(model_cls).where(model_cls.id == id)
            result = await session.execute(stmt)
            model = result.scalars().first()
            
            if not model:
                return False
            
            # Delete the record
            await session.delete(model)
            await session.commit()
            
            return True
    
    async def count(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records in a table with optional filtering"""
        if not self.async_session:
            await self.connect()
            
        model_cls = self._get_model_class(collection)
        
        async with self.async_session() as session:
            # Start with a base count query
            stmt = select(func.count()).select_from(model_cls)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(model_cls, key):
                        stmt = stmt.where(getattr(model_cls, key) == value)
            
            # Execute query
            result = await session.execute(stmt)
            count = result.scalar()
            
            return count or 0
