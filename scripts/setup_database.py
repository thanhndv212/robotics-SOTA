#!/usr/bin/env python3
"""
Script to import initial lab data and set up the database
"""
import sys
import os

# Add the backend app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.services.lab_importer import LabImporter


def main():
    """Main function to set up database and import data"""
    print("🚀 Setting up Robotics SOTA database...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create database tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Import lab data
            print("🏢 Importing lab data...")
            importer = LabImporter()
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'robot_learning_labs_directory.csv')
            csv_path = os.path.abspath(csv_path)  # Convert to absolute path
            print(f"📁 Looking for CSV at: {csv_path}")
            
            if os.path.exists(csv_path):
                result = importer.import_from_csv(csv_path)
                print(f"✅ Successfully imported {result['imported']} labs out of {result['total']}")
            else:
                print(f"❌ CSV file not found at {csv_path}")
                return False
            
            print("🎉 Setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Start the backend: cd backend && python run.py")
            print("2. Start the frontend: cd frontend && npm start")
            print("3. Visit http://localhost:3000 to see the application")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)