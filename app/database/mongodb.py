from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

from app.database.db import DatabaseClient


class MongoDBClient(DatabaseClient):
    """MongoDB implementation of the DatabaseClient interface"""
    
    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize MongoDB client
        
        Args:
            connection_string: MongoDB connection string
            database_name: Database name
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database_name]
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def get_by_id(self, collection: str, id: Any) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        if not self.db:
            await self.connect()
            
        # Convert string ID to ObjectId if needed
        if isinstance(id, str) and ObjectId.is_valid(id):
            id = ObjectId(id)
            
        result = await self.db[collection].find_one({"_id": id})
        if result:
            # Convert ObjectId to string for serialization
            result["id"] = str(result.pop("_id"))
            return result
        return None
    
    async def get_many(
        self, 
        collection: str, 
        filters: Optional[Dict[str, Any]] = None, 
        skip: int = 0, 
        limit: int = 100,
        sort: Optional[Dict[str, int]] = None
    ) -> List[Dict[str, Any]]:
        """Get multiple documents with filtering, pagination and sorting"""
        if not self.db:
            await self.connect()
            
        # Process filters for MongoDB
        query = filters or {}
        
        # Apply sorting if provided
        cursor = self.db[collection].find(query).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(list(sort.items()))
            
        # Convert results
        results = []
        async for doc in cursor:
            # Convert ObjectId to string for serialization
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
            
        return results
    
    async def create(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        if not self.db:
            await self.connect()
            
        # Handle id/ID field conversion
        if "id" in document:
            document["_id"] = document.pop("id")
            
        result = await self.db[collection].insert_one(document)
        
        # Return the created document
        created_doc = await self.get_by_id(collection, result.inserted_id)
        return created_doc
    
    async def update(
        self, 
        collection: str, 
        id: Any, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a document"""
        if not self.db:
            await self.connect()
            
        # Convert string ID to ObjectId if needed
        if isinstance(id, str) and ObjectId.is_valid(id):
            id = ObjectId(id)
            
        # Remove id from update data if present
        if "id" in update_data:
            del update_data["id"]
            
        # Update the document
        await self.db[collection].update_one(
            {"_id": id},
            {"$set": update_data}
        )
        
        # Return the updated document
        return await self.get_by_id(collection, id)
    
    async def delete(self, collection: str, id: Any) -> bool:
        """Delete a document"""
        if not self.db:
            await self.connect()
            
        # Convert string ID to ObjectId if needed
        if isinstance(id, str) and ObjectId.is_valid(id):
            id = ObjectId(id)
            
        result = await self.db[collection].delete_one({"_id": id})
        return result.deleted_count > 0
    
    async def count(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents in a collection with optional filtering"""
        if not self.db:
            await self.connect()
            
        query = filters or {}
        return await self.db[collection].count_documents(query)
