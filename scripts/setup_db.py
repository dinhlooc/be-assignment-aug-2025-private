import os
import sys
from pathlib import Path

# Add project root to Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from alembic import command
from alembic.config import Config
from app.database import engine, Base
from app.models import *  # Import all models to ensure they're registered

def setup_database():
    """
    Initialize the database and run migrations.
    """
    print("Setting up database...")
    
    try:
        # Create tables directly (optional backup if alembic fails)
        # Base.metadata.create_all(bind=engine)
        # print("Tables created directly via SQLAlchemy")
        
        # Run alembic migrations (preferred approach)
        alembic_cfg = Config(os.path.join(root_dir, "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
        print("Database migrations completed successfully!")
        
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("Database setup completed successfully!")
    else:
        print("Database setup failed.")
        sys.exit(1)