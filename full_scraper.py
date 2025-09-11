#!/usr/bin/env python3
"""
Full Paper Scraper - All 50 labs
"""

import arxiv
import time
import json
import sys

# Add backend to path
sys.path.insert(0, 'backend')

def scrape_all_labs():
    """Scrape papers for all 50 labs"""
    
    from app import create_app
    from app.models import Lab, Paper
    from app import db
    
    app = create_app()
    
    with app.app_context():
        labs = Lab.query.all()
        print(f"🔍 Scraping papers for all {len(labs)} labs...")
        
        total_new_papers = 0
        existing_papers = Paper.query.count()
        
        for i, lab in enumerate(labs, 1):
            print(f"\n📚 [{i}/{len(labs)}] {lab.name}")
            
            # Skip if we already have papers for this lab
            existing_lab_papers = Paper.query.filter_by(lab_id=lab.id).count()
            if existing_lab_papers >= 3:
                print(f"   📄 Already has {existing_lab_papers} papers, skipping...")
                continue
            
            # Search ArXiv
            pi_name = lab.pi.replace('"', '').replace('Multiple', '').replace('(e.g.', '').strip()
            if ' ' in pi_name and len(pi_name) > 3:
                last_name = pi_name.split()[-1].replace(')', '').strip()
                
                if len(last_name) > 2:
                    query = f'au:"{last_name}" AND (robot OR robotics)'
                    print(f"   🔎 {query}")
                    
                    try:
                        search = arxiv.Search(
                            query=query,
                            max_results=3,
                            sort_by=arxiv.SortCriterion.Relevance
                        )
                        
                        papers_added = 0
                        for paper in search.results():
                            arxiv_id = paper.entry_id.split('/')[-1]
                            existing = Paper.query.filter_by(arxiv_id=arxiv_id).first()
                            
                            if not existing:
                                new_paper = Paper(
                                    title=paper.title.strip(),
                                    authors=json.dumps([str(author) for author in paper.authors]),
                                    abstract=paper.summary.strip() if paper.summary else '',
                                    publication_date=paper.published.date(),
                                    venue='arXiv',
                                    paper_type='preprint',
                                    arxiv_id=arxiv_id,
                                    pdf_url=paper.pdf_url,
                                    research_areas=json.dumps(['robotics']),
                                    keywords=json.dumps(['robot']),
                                    lab_id=lab.id,
                                    citation_count=0
                                )
                                
                                db.session.add(new_paper)
                                papers_added += 1
                                total_new_papers += 1
                                
                                if papers_added >= 3:  # Limit per lab
                                    break
                        
                        if papers_added > 0:
                            db.session.commit()
                            print(f"   ✅ Added {papers_added} papers")
                        else:
                            print(f"   📄 No new papers found")
                        
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        db.session.rollback()
                else:
                    print(f"   ⏭️  Skipping (short name)")
            else:
                print(f"   ⏭️  Skipping (no clear PI name)")
        
        final_count = Paper.query.count()
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Papers before: {existing_papers}")
        print(f"📊 Papers added: {total_new_papers}")
        print(f"📊 Papers now: {final_count}")

if __name__ == "__main__":
    scrape_all_labs()