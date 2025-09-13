#!/usr/bin/env python3
"""
Script to export lab data from the database to CSV format
"""

import requests
import csv
import json

API_BASE = "http://127.0.0.1:8080/api"

def export_labs_to_csv():
    """Export all labs from database to CSV file"""
    try:
        # Fetch all labs from API
        response = requests.get(f"{API_BASE}/labs")
        if response.status_code != 200:
            print(f"Error fetching labs: {response.status_code}")
            return
        
        labs = response.json()
        print(f"📊 Fetched {len(labs)} labs from database")
        
        # Prepare CSV data
        csv_file = '/Users/thanhndv212/Develop/robotics-SOTA/data/robot_learning_labs_directory.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Lab Name', 'PI', 'Institution', 'City', 'Country', 'Focus', 'Link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write lab data
            for lab in labs:
                # Format focus areas
                focus_areas = lab.get('focus_areas', [])
                if isinstance(focus_areas, str):
                    try:
                        focus_areas = json.loads(focus_areas)
                    except:
                        focus_areas = [focus_areas]
                elif not isinstance(focus_areas, list):
                    focus_areas = []
                
                focus_str = ', '.join(focus_areas) if focus_areas else ""
                
                writer.writerow({
                    'Lab Name': lab.get('name', ''),
                    'PI': lab.get('pi', ''),
                    'Institution': lab.get('institution', ''),
                    'City': lab.get('city', ''),
                    'Country': lab.get('country', ''),
                    'Focus': focus_str,
                    'Link': lab.get('website', '')
                })
        
        print(f"✅ Successfully exported {len(labs)} labs to {csv_file}")
        
        # Show summary by institution
        institution_counts = {}
        for lab in labs:
            inst = lab.get('institution', 'Unknown')
            institution_counts[inst] = institution_counts.get(inst, 0) + 1
        
        print("\n📈 Labs by Institution:")
        for inst, count in sorted(institution_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {inst}: {count} labs")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    export_labs_to_csv()