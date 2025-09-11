#!/usr/bin/env python3
"""
Simple Paper Scraper - ArXiv only for quick testing
"""

import arxiv
import time
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

def scrape_papers_simple():
    """Simple paper scraping using ArXiv only"""
    
    from app import create_app
    from app.models import Lab, Paper
    from app import db
    
    app = create_app()
    
    with app.app_context():
        # Get first 5 labs
        labs = Lab.query.limit(5).all()
        
        print(f"🔍 Scraping papers for {len(labs)} labs using ArXiv...")
        
        total_papers = 0
        
        for i, lab in enumerate(labs, 1):
            print(f"\n📚 [{i}/{len(labs)}] {lab.name}")
            print(f"   PI: {lab.pi}")
            
            # Search ArXiv for papers by PI
            pi_name = lab.pi.replace('"', '').strip()
            if ' ' in pi_name:
                last_name = pi_name.split()[-1]
                query = f'au:"{last_name}" AND (robot OR robotics OR manipulation OR learning)'
                
                print(f"   🔎 Searching: {query}")
                
                try:
                    search = arxiv.Search(
                        query=query,
                        max_results=5,
                        sort_by=arxiv.SortCriterion.Relevance
                    )
                    
                    papers_found = 0
                    for paper in search.results():
                        # Check if paper already exists
                        arxiv_id = paper.entry_id.split('/')[-1]
                        existing = Paper.query.filter_by(arxiv_id=arxiv_id).first()
                        
                        if not existing:
                            # Create new paper
                            import json
                            new_paper = Paper(
                                title=paper.title.strip(),
                                authors=json.dumps([str(author) for author in paper.authors]),
                                abstract=paper.summary.strip() if paper.summary else '',
                                publication_date=paper.published.date(),
                                venue='arXiv',
                                paper_type='preprint',
                                arxiv_id=arxiv_id,
                                pdf_url=paper.pdf_url,
                                research_areas=json.dumps(['robotics', 'machine learning']),
                                keywords=json.dumps(['robot', 'learning']),
                                lab_id=lab.id,
                                citation_count=0
                            )
                            
                            db.session.add(new_paper)
                            papers_found += 1
                            total_papers += 1
                            
                            print(f"      ✅ {paper.title[:60]}...")
                    
                    if papers_found > 0:
                        db.session.commit()
                        print(f"   📄 Added {papers_found} papers")
                    else:
                        print(f"   📄 No new papers found")
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    db.session.rollback()
        
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Total papers added: {total_papers}")
        
        # Show final count
        total_in_db = Paper.query.count()
        print(f"📚 Total papers in database: {total_in_db}")

if __name__ == "__main__":
    scrape_papers_simple()