from Backend.database.database_manager import DatabaseManager


db = DatabaseManager()
db.create_tables()

print("GHOSTLAB database created successfully!")