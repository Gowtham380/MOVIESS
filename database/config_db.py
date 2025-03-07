from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME

class Database:
    def __init__(self, uri, db_name, collection_name):
        try:
            self.client = AsyncIOMotorClient(uri)
            self.db = self.client[db_name]
            self.col = self.db[collection_name]
            self.config_col = self.db["configuration"]
            print("✅ MongoDB Connected Successfully!")
        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {e}")

    async def save_file(self, file_id, file_name):
        """Save file details in MongoDB"""
        try:
            existing_file = await self.col.find_one({"file_id": file_id})
            if existing_file:
                print(f"⚠️ File already exists: {file_name}")
                return

            await self.col.insert_one({"file_id": file_id, "file_name": file_name})
            print(f"✅ Successfully saved: {file_name}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")

    async def get_files(self):
        """Retrieve all indexed files"""
        return await self.col.find().to_list(None)

    async def delete_all_files(self):
        """Delete all indexed files"""
        await self.col.delete_many({})
        print("🗑️ All indexed files deleted!")

    async def update_configuration(self, key, value):
        """Update bot settings"""
        await self.config_col.update_one({}, {'$set': {key: value}}, upsert=True)

    async def get_configuration_value(self, key):
        """Retrieve a bot setting"""
        configuration = await self.config_col.find_one({})
        return configuration.get(key, False) if configuration else None

    async def update_advertisement(self, ads_string, ads_name, expiry, impression):
        """Update advertisement details"""
        await self.config_col.update_one(
            {},
            {'$set': {'advertisement': {
                'ads_string': ads_string,
                'ads_name': ads_name,
                'expiry': expiry,
                'impression_count': impression
            }}},
            upsert=True
        )

    async def reset_advertisement_if_expired(self):
        """Reset advertisement if expired"""
        configuration = await self.config_col.find_one({})
        if configuration:
            advertisement = configuration.get('advertisement', {})
            impression_count = advertisement.get('impression_count', 0)
            expiry = advertisement.get('expiry')

            if (impression_count == 0) or (expiry and datetime.now() > expiry):
                await self.config_col.update_one({}, {'$set': {'advertisement': None}})

mdb = Database(DATABASE_URI, DATABASE_NAME, COLLECTION_NAME)