#!/usr/bin/env python3
"""
Test Paper Scraper - Limited run for testing
"""

import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

async def test_scraper():
    """Test the paper scraper with a limited number of labs"""
    
    # Set up Flask app context
    from app import create_app
    from app.services.lab_paper_scraper import LabPaperScraper
    from app.models import Lab, Paper
    
    app = create_app()
    
    with app.app_context():
        # Get first 3 labs for testing
        test_labs = Lab.query.limit(3).all()
        
        if not test_labs:
            print("❌ No labs found in database!")
            return
        
        print(f"🧪 Testing paper scraper with {len(test_labs)} labs:")
        for lab in test_labs:
            print(f"   • {lab.name}")
        print()
        
        # Initialize scraper
        scraper = LabPaperScraper()
        
        # Test each lab individually
        total_papers = 0
        for lab in test_labs:
            print(f"🔍 Processing {lab.name}...")
            try:
                papers_found = await scraper.scrape_lab_papers(lab)
                total_papers += papers_found
                print(f"   ✅ Found {papers_found} papers")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n🎉 Test completed! Total papers found: {total_papers}")

if __name__ == "__main__":
    asyncio.run(test_scraper())