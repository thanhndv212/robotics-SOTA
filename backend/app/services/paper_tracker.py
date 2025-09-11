import requests
import arxiv
import feedparser
from datetime import datetime, timedelta
from app import db
from app.models import Paper, Lab
from app.services.nlp_processor import NLPProcessor
import time
import re


class PaperTracker:
    """Service for tracking and importing research papers"""
    
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.rate_limit_delay = 1  # seconds between requests
    
    def track_arxiv_papers(self, max_results=100):
        """Track papers from arXiv"""
        try:
            # Search for robotics and machine learning papers
            search_queries = [
                'cat:cs.RO',  # Robotics
                'cat:cs.LG AND robot',  # ML + robotics
                'cat:cs.AI AND robot',  # AI + robotics
                'manipulation AND robot',
                'reinforcement learning AND robot',
                'robot learning'
            ]
            
            imported_count = 0
            
            for query in search_queries:
                try:
                    search = arxiv.Search(
                        query=query,
                        max_results=max_results // len(search_queries),
                        sort_by=arxiv.SortCriterion.SubmittedDate,
                        sort_order=arxiv.SortOrder.Descending
                    )
                    
                    for paper in search.results():
                        if self._import_arxiv_paper(paper):
                            imported_count += 1
                        
                        time.sleep(self.rate_limit_delay)
                
                except Exception as e:
                    print(f"Error processing query '{query}': {e}")
                    continue
            
            db.session.commit()
            return imported_count
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to track arXiv papers: {str(e)}")
    
    def _import_arxiv_paper(self, arxiv_paper):
        """Import a single paper from arXiv"""
        try:
            arxiv_id = arxiv_paper.entry_id.split('/')[-1]
            
            # Check if paper already exists
            existing_paper = Paper.query.filter_by(arxiv_id=arxiv_id).first()
            if existing_paper:
                return False
            
            # Extract and process paper data
            authors = [str(author) for author in arxiv_paper.authors]
            title = arxiv_paper.title.strip()
            abstract = arxiv_paper.summary.strip()
            
            # Use NLP to extract research areas and keywords
            research_areas = self.nlp_processor.extract_research_areas(
                title + " " + abstract
            )
            keywords = self.nlp_processor.extract_keywords(
                title + " " + abstract
            )
            
            # Try to match with existing labs
            lab_id = self._match_paper_to_lab(authors, title, abstract)
            
            paper = Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                publication_date=arxiv_paper.published.date(),
                venue='arXiv',
                paper_type='preprint',
                arxiv_id=arxiv_id,
                pdf_url=arxiv_paper.pdf_url,
                research_areas=research_areas,
                keywords=keywords,
                lab_id=lab_id
            )
            
            db.session.add(paper)
            return True
            
        except Exception as e:
            print(f"Failed to import arXiv paper {arxiv_paper.entry_id}: {e}")
            return False
    
    def track_lab_papers(self, lab_id):
        """Track papers from a specific lab's website"""
        try:
            lab = Lab.query.get(lab_id)
            if not lab or not lab.website:
                return 0
            
            # Try to find RSS feeds or publication pages
            papers_found = 0
            
            # Check for common RSS feed patterns
            feed_urls = [
                f"{lab.website}/feed",
                f"{lab.website}/rss",
                f"{lab.website}/publications/feed",
                f"{lab.website}/news/feed"
            ]
            
            for feed_url in feed_urls:
                try:
                    papers_found += self._process_rss_feed(feed_url, lab_id)
                except Exception as e:
                    print(f"Failed to process feed {feed_url}: {e}")
                    continue
            
            return papers_found
            
        except Exception as e:
            print(f"Failed to track papers for lab {lab_id}: {e}")
            return 0
    
    def _process_rss_feed(self, feed_url, lab_id):
        """Process RSS feed for papers"""
        try:
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                return 0
            
            papers_added = 0
            
            for entry in feed.entries[:20]:  # Limit to recent entries
                # Check if this looks like a paper
                if self._is_paper_entry(entry):
                    if self._import_feed_paper(entry, lab_id):
                        papers_added += 1
                
                time.sleep(self.rate_limit_delay)
            
            return papers_added
            
        except Exception as e:
            print(f"Failed to process RSS feed {feed_url}: {e}")
            return 0
    
    def _is_paper_entry(self, entry):
        """Check if RSS entry represents a paper"""
        title = entry.title.lower()
        
        # Look for paper-like keywords
        paper_indicators = [
            'paper', 'publication', 'accepted', 'published',
            'conference', 'journal', 'arxiv', 'preprint'
        ]
        
        return any(indicator in title for indicator in paper_indicators)
    
    def _import_feed_paper(self, entry, lab_id):
        """Import paper from RSS feed entry"""
        try:
            title = entry.title.strip()
            
            # Check if paper already exists
            existing_paper = Paper.query.filter_by(
                title=title, lab_id=lab_id
            ).first()
            if existing_paper:
                return False
            
            # Extract publication date
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:3]).date()
            
            # Extract abstract/summary
            abstract = ""
            if hasattr(entry, 'summary'):
                abstract = entry.summary.strip()
            
            # Use NLP processing
            research_areas = self.nlp_processor.extract_research_areas(
                title + " " + abstract
            )
            keywords = self.nlp_processor.extract_keywords(
                title + " " + abstract
            )
            
            paper = Paper(
                title=title,
                authors=[],  # Authors not typically in RSS feeds
                abstract=abstract,
                publication_date=pub_date,
                venue='Unknown',
                paper_type='publication',
                pdf_url=entry.link if hasattr(entry, 'link') else None,
                research_areas=research_areas,
                keywords=keywords,
                lab_id=lab_id
            )
            
            db.session.add(paper)
            return True
            
        except Exception as e:
            print(f"Failed to import feed paper: {e}")
            return False
    
    def _match_paper_to_lab(self, authors, title, abstract):
        """Try to match a paper to a lab based on authors or content"""
        try:
            # Simple matching based on author affiliation keywords
            text_to_search = " ".join(authors).lower()
            
            labs = Lab.query.all()
            
            for lab in labs:
                # Check if lab name or institution appears in author info
                if (lab.institution.lower() in text_to_search or
                    lab.name.lower() in text_to_search):
                    return lab.id
                
                # Check PI name
                if lab.pi and lab.pi.lower() in text_to_search:
                    return lab.id
            
            return None
            
        except Exception as e:
            print(f"Failed to match paper to lab: {e}")
            return None
    
    def update_citation_counts(self):
        """Update citation counts for papers"""
        # This would integrate with Google Scholar or similar
        # For now, just a placeholder
        pass