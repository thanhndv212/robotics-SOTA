#!/usr/bin/env python3
"""
Database migration script to add hierarchical support to labs table
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from sqlalchemy import text


def migrate_database():
    """Add hierarchical columns to existing labs table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting database migration...")
            
            # Check if columns already exist
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(labs)"))
                columns = [row[1] for row in result]
            
                # Add parent_lab_id column if it doesn't exist
                if 'parent_lab_id' not in columns:
                    conn.execute(text(
                        "ALTER TABLE labs ADD COLUMN parent_lab_id INTEGER"
                    ))
                    print("✅ Added parent_lab_id column")
                else:
                    print("ℹ️  parent_lab_id column already exists")
                
                # Add lab_type column if it doesn't exist
                if 'lab_type' not in columns:
                    conn.execute(text(
                        "ALTER TABLE labs ADD COLUMN lab_type VARCHAR(50) "
                        "DEFAULT 'independent'"
                    ))
                    print("✅ Added lab_type column")
                else:
                    print("ℹ️  lab_type column already exists")
                
                # Update existing labs to have 'independent' type
                result = conn.execute(text(
                    "UPDATE labs SET lab_type = 'independent' "
                    "WHERE lab_type IS NULL OR lab_type = ''"
                ))
                print(f"✅ Updated {result.rowcount} labs with 'independent' type")
                
                # Commit the transaction
                conn.commit()
            
            print("🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)