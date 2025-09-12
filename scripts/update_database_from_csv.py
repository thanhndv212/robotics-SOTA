#!/usr/bin/env python3
"""
Update database with new labs from CSV file.
This script adds any new labs from the CSV that don't already exist in the database.
"""

import sys
import os
import csv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.models import Lab


def update_database():
    """Update database with new labs from CSV"""
    app = create_app()
    
    with app.app_context():
        print("🗄️ Updating database with new labs...")
        
        # Check current state
        lab_count = Lab.query.count()
        print(f"📊 Current labs in database: {lab_count}")
        
        # Read CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'robot_learning_labs_directory.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found at {csv_path}")
            return False
        
        print(f"📂 Reading CSV file: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_labs = list(reader)
            csv_count = len(csv_labs)
        
        print(f"📊 Labs in CSV file: {csv_count}")
        
        # Get existing lab names to avoid duplicates
        existing_labs = {lab.name for lab in Lab.query.all()}
        print(f"🔍 Found {len(existing_labs)} existing lab names in database")
        
        # Add new labs
        new_labs_added = 0
        duplicates_skipped = 0
        
        for row in csv_labs:
            lab_name = row['Lab Name']
            
            if lab_name not in existing_labs:
                try:
                    lab = Lab(
                        name=lab_name,
                        pi=row['PI'],
                        institution=row['Institution'],
                        city=row['City'],
                        country=row['Country'],
                        focus_areas=row['Focus'],  # Map 'Focus' to 'focus_areas'
                        website=row['Link']        # Map 'Link' to 'website'
                    )
                    db.session.add(lab)
                    new_labs_added += 1
                    print(f"➕ Adding: {lab_name} ({row['Institution']})")
                except Exception as e:
                    print(f"❌ Error adding {lab_name}: {str(e)}")
            else:
                duplicates_skipped += 1
        
        if new_labs_added > 0:
            try:
                db.session.commit()
                print(f"\n✅ Successfully added {new_labs_added} new labs to database")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Error committing changes: {str(e)}")
                return False
        else:
            print("\n✅ No new labs to add - database is up to date")
        
        print(f"📊 Duplicates skipped: {duplicates_skipped}")
        
        # Final count
        final_count = Lab.query.count()
        print(f"📊 Total labs in database after update: {final_count}")
        
        return True


if __name__ == '__main__':
    success = update_database()
    if success:
        print("\n🎉 Database update completed successfully!")
    else:
        print("\n💥 Database update failed!")
        sys.exit(1)