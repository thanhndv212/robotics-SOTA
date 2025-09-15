#!/usr/bin/env python3
"""
Debug script to test paper scraping for a specific lab
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.models import Lab, Paper
from app.services.lab_paper_scraper import LabPaperScraper


async def debug_scraping():
    """Debug the scraping process"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Debug Paper Scraping")
        print("=" * 50)
        
        # Get Berkeley lab
        lab = Lab.query.filter_by(name='Berkeley Robot Learning Lab (RLL)').first()
        if not lab:
            print("❌ Lab not found")
            return
        
        print(f"Lab: {lab.name}")
        print(f"PI: {lab.pi}")
        print(f"Institution: {lab.institution}")
        print(f"Focus Areas: {lab.focus_areas}")
        print(f"Website: {lab.website}")
        print()
        
        # Create scraper with app context
        scraper = LabPaperScraper(app)
        scraper.max_papers_per_lab = 2  # Limit for testing
        
        # Test query building
        queries = scraper._build_arxiv_queries(lab)
        print(f"📝 Generated queries:")
        for i, query in enumerate(queries):
            print(f"  {i+1}. {query}")
        print()
        
        # Test ArXiv search
        print("🔍 Testing ArXiv search...")
        papers_found = await scraper.search_arxiv_papers(lab)
        print(f"Papers found: {papers_found}")
        print()
        
        # Check what papers were imported
        lab_papers = Paper.query.filter_by(lab_id=lab.id).order_by(Paper.publication_date.desc()).all()
        print(f"📚 Papers in database for this lab: {len(lab_papers)}")
        for paper in lab_papers:
            print(f"  - {paper.title}")
            print(f"    ArXiv ID: {paper.arxiv_id}")
            print(f"    Date: {paper.publication_date}")
            print()


if __name__ == '__main__':
    asyncio.run(debug_scraping())