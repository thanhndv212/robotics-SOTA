import pandas as pd
import requests
import json
from datetime import datetime
from app import db
from app.models import Lab


class LabImporter:
    """Service for importing and processing lab data"""
    
    def __init__(self):
        self.geocoding_cache = {}
    
    def import_from_csv(self, csv_path):
        """Import labs from CSV file"""
        try:
            print(f"📖 Reading CSV from: {csv_path}")
            df = pd.read_csv(csv_path)
            print(f"📊 CSV loaded with {len(df)} rows")
            print(f"🏷️ Columns: {list(df.columns)}")
            
            # Clean column names
            df.columns = df.columns.str.strip()
            print(f"🧹 Cleaned columns: {list(df.columns)}")
            
            imported_count = 0
            for idx, row in df.iterrows():
                lab_data = self._process_lab_row(row)
                if not lab_data:
                    continue
                
                # Check if lab already exists
                existing_lab = Lab.query.filter_by(
                    name=lab_data['name'],
                    institution=lab_data['institution']
                ).first()
                
                print(f"🔍 Checking for existing lab: {lab_data['name'][:20]}... at {lab_data['institution'][:20]}...")
                print(f"🔍 Found existing: {existing_lab is not None}")
                
                if not existing_lab:
                    lab = Lab(**lab_data)
                    db.session.add(lab)
                    imported_count += 1
                    print(f"✅ Added NEW lab: {lab_data['name'][:30]}...")
                else:
                    # Update existing lab
                    for key, value in lab_data.items():
                        if key != 'created_at':  # Don't update created_at
                            setattr(existing_lab, key, value)
                    print(f"🔄 Updated existing lab: {lab_data['name'][:30]}...")
            
            db.session.commit()
            print(f"💾 Committed {imported_count} labs to database")
            return {'imported': imported_count, 'total': len(df)}
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Import error: {str(e)}")
            raise Exception(f"Failed to import labs: {str(e)}")
    
    def _process_lab_row(self, row):
        """Process a single lab row"""
        try:
            # Extract data
            lab_name = str(row['Lab Name']).strip()
            pi = str(row['PI']).strip()
            institution = str(row['Institution']).strip()
            city = str(row['City']).strip()
            country = str(row['Country']).strip()
            focus = str(row['Focus']).strip()
            link = str(row['Link']).strip()
            
            print(f"🔄 Processing lab: {lab_name[:30]}...")
            
            # Create lab data dictionary
            focus_list = [area.strip() for area in focus.split(',') if area.strip()] if focus and focus != 'nan' else []
            
            lab_data = {
                'name': lab_name,
                'pi': pi,
                'institution': institution,
                'city': city,
                'country': country,
                'focus_areas': json.dumps(focus_list),
                'website': link if link and link != 'nan' else None,
                'latitude': 0.0,  # Will be filled by geocoding
                'longitude': 0.0,
                'created_at': datetime.utcnow()
            }
            
            return lab_data
            
        except Exception as e:
            print(f"❌ Error processing row: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_coordinates(self, city, country):
        """Get latitude and longitude for a city/country"""
        cache_key = f"{city},{country}"
        
        if cache_key in self.geocoding_cache:
            return self.geocoding_cache[cache_key]
        
        try:
            # Use a simple geocoding service (in production, use proper API)
            url = f"https://geocoding-api.open-meteo.com/v1/search"
            params = {'name': f"{city}, {country}", 'count': 1}
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    lat, lon = result['latitude'], result['longitude']
                    self.geocoding_cache[cache_key] = (lat, lon)
                    return lat, lon
        
        except Exception as e:
            print(f"Geocoding failed for {city}, {country}: {e}")
        
        # Fallback coordinates for major cities
        fallback_coords = {
            'Berkeley,USA': (37.8715, -122.2730),
            'Stanford,USA': (37.4275, -122.1697),
            'Cambridge,USA': (42.3736, -71.1097),
            'Pittsburgh,USA': (40.4406, -79.9959),
            'Oxford,UK': (51.7520, -1.2577),
            'Zurich,Switzerland': (47.3769, 8.5417),
            'Tokyo,Japan': (35.6762, 139.6503),
            'Beijing,China': (39.9042, 116.4074),
            'Seoul,South Korea': (37.5665, 126.9780),
            'Singapore,Singapore': (1.3521, 103.8198),
        }
        
        coords = fallback_coords.get(cache_key, (None, None))
        self.geocoding_cache[cache_key] = coords
        return coords
    
    def _generate_description(self, focus_areas):
        """Generate a description based on focus areas"""
        if not focus_areas:
            return "Leading robotics research laboratory"
        
        return f"Research focus: {', '.join(focus_areas[:3])}"
    
    def enrich_lab_data(self, lab_id):
        """Enrich lab data with additional information"""
        try:
            lab = Lab.query.get(lab_id)
            if not lab:
                return False
            
            # TODO: Implement web scraping for additional lab info
            # - Recent publications
            # - Faculty members
            # - Funding information
            # - News and updates
            
            return True
            
        except Exception as e:
            print(f"Failed to enrich lab {lab_id}: {e}")
            return False


def import_initial_data():
    """Import initial lab data from CSV"""
    importer = LabImporter()
    csv_path = '/app/data/robot_learning_labs_directory.csv'
    
    try:
        result = importer.import_from_csv(csv_path)
        print(f"Successfully imported {result['imported']} labs out of {result['total']}")
        return result
    except Exception as e:
        print(f"Failed to import initial data: {e}")
        return None