from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel


# Type variables for models and schemas
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=BaseModel)


class DatabaseClient(ABC):
    """Abstract database client interface that can be implemented for different database types"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    async def get_by_id(self, collection: str, id: Any) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        pass
    
    @abstractmethod
    async def get_many(
        self, 
        collection: str, 
        filters: Optional[Dict[str, Any]] = None, 
        skip: int = 0, 
        limit: int = 100,
        sort: Optional[Dict[str, int]] = None
    ) -> List[Dict[str, Any]]:
        """Get multiple documents with filtering, pagination and sorting"""
        pass
    
    @abstractmethod
    async def create(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        pass
    
    @abstractmethod
    async def update(
        self, 
        collection: str, 
        id: Any, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a document"""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, id: Any) -> bool:
        """Delete a document"""
        pass
    
    @abstractmethod
    async def count(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents in a collection with optional filtering"""
        pass


class Repository(Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]):
    """
    Generic repository for database operations.
    This class provides a consistent interface regardless of the underlying database.
    """
    
    def __init__(
        self, 
        db_client: DatabaseClient,
        collection: str,
        model_cls: Type[ModelType]
    ):
        """
        Initialize repository with database client and collection/table name
        
        Args:
            db_client: Database client implementation
            collection: Collection or table name
            model_cls: Model class for converting database results
        """
        self.db = db_client
        self.collection = collection
        self.model_cls = model_cls
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get a single item by ID
        
        Args:
            id: The ID of the item to retrieve
            
        Returns:
            The item if found, None otherwise
        """
        result = await self.db.get_by_id(self.collection, id)
        if result:
            return self.model_cls(**result)
        return None
    
    async def get_many(
        self,
        *,
        filters: Optional[FilterSchemaType] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ) -> List[ModelType]:
        """
        Get multiple items with filtering and pagination
        
        Args:
            filters: Optional filter criteria
            skip: Number of items to skip
            limit: Maximum number of items to return
            sort_by: Field to sort by
            sort_desc: Sort in descending order if True
            
        Returns:
            List of items matching the criteria
        """
        filter_dict = filters.dict(exclude_unset=True) if filters else None
        
        # Handle sorting
        sort_dict = None
        if sort_by:
            sort_dict = {sort_by: -1 if sort_desc else 1}
            
        results = await self.db.get_many(
            self.collection, 
            filters=filter_dict, 
            skip=skip, 
            limit=limit,
            sort=sort_dict
        )
        
        return [self.model_cls(**item) for item in results]
    
    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new item
        
        Args:
            obj_in: The data to create the item with
            
        Returns:
            The created item
        """
        obj_data = obj_in.dict()
        result = await self.db.create(self.collection, obj_data)
        return self.model_cls(**result)
    
    async def update(
        self,
        *,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Update an item
        
        Args:
            id: The ID of the item to update
            obj_in: The data to update the item with
            
        Returns:
            The updated item if found, None otherwise
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        result = await self.db.update(self.collection, id, update_data)
        if result:
            return self.model_cls(**result)
        return None
    
    async def delete(self, *, id: Any) -> bool:
        """
        Delete an item
        
        Args:
            id: The ID of the item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        return await self.db.delete(self.collection, id)
    
    async def count(self, *, filters: Optional[FilterSchemaType] = None) -> int:
        """
        Count items matching the filter criteria
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            Number of items matching the criteria
        """
        filter_dict = filters.dict(exclude_unset=True) if filters else None
        return await self.db.count(self.collection, filter_dict)