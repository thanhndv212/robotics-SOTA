#!/usr/bin/env python3
"""
Paper Scraper Script for Robotics SOTA
Scrapes 5-10 highlight papers for each lab in the database
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up Flask app context
from app import create_app, db
from app.services.lab_paper_scraper import LabPaperScraper
from app.models import Lab, Paper

def print_header():
    print("=" * 80)
    print("🤖 ROBOTICS SOTA - PAPER SCRAPING SYSTEM")
    print("=" * 80)
    print("📚 Scraping highlight papers for robotics research labs...")
    print("🎯 Target: 5-10 papers per lab")
    print("🔍 Sources: ArXiv, Google Scholar, Lab websites")
    print("=" * 80)

async def main():
    """Main scraping function"""
    print_header()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Check database connection
        try:
            lab_count = Lab.query.count()
            existing_papers = Paper.query.count()
            
            print(f"📊 Database Status:")
            print(f"   • Labs in database: {lab_count}")
            print(f"   • Existing papers: {existing_papers}")
            print()
            
            if lab_count == 0:
                print("❌ No labs found in database!")
                print("   Please run the lab import script first.")
                return
            
            # Show sample labs
            sample_labs = Lab.query.limit(5).all()
            print("🏢 Sample labs to process:")
            for lab in sample_labs:
                print(f"   • {lab.name} ({lab.institution})")
            if lab_count > 5:
                print(f"   ... and {lab_count - 5} more labs")
            print()
            
            # Confirm before starting
            response = input("🚀 Start paper scraping? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ Scraping cancelled by user")
                return
            
            print("\n" + "=" * 80)
            print("🔍 STARTING PAPER SCRAPING...")
            print("=" * 80)
            
            # Initialize scraper with app context
            scraper = LabPaperScraper(app)
            
            # Run scraping
            total_papers = await scraper.scrape_all_labs()
            
            # Final statistics
            final_paper_count = Paper.query.count()
            new_papers = final_paper_count - existing_papers
            
            print("\n" + "=" * 80)
            print("🎉 SCRAPING COMPLETED!")
            print("=" * 80)
            print(f"📈 Results:")
            print(f"   • Papers found: {total_papers}")
            print(f"   • New papers added: {new_papers}")
            print(f"   • Total papers in DB: {final_paper_count}")
            print()
            
            # Show sample results
            if new_papers > 0:
                print("📚 Sample new papers:")
                recent_papers = Paper.query.filter_by(lab_id=sample_labs[0].id).order_by(Paper.publication_date.desc()).limit(3).all()
                for paper in recent_papers:
                    print(f"   • {paper.title[:60]}...")
                    print(f"     {paper.venue} | {paper.publication_date}")
                print()
            
            print("✅ Paper scraping completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Scraping interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)