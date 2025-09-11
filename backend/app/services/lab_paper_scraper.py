import asyncio
import aiohttp
import arxiv
import re
from typing import List
from datetime import datetime
from scholarly import scholarly
from bs4 import BeautifulSoup
from app import db
from app.models import Paper, Lab


class LabPaperScraper:
    """Enhanced paper scraper for robotics labs"""
    
    def __init__(self):
        self.rate_limit_delay = 2  # seconds between requests
        self.max_papers_per_lab = 10
        self.session = None
    
    async def scrape_all_labs(self):
        """Scrape papers for all labs in the database"""
        labs = Lab.query.all()
        print(f"🔍 Starting paper scraping for {len(labs)} labs...")
        
        total_papers = 0
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            for i, lab in enumerate(labs, 1):
                print(f"\n📚 [{i}/{len(labs)}] Processing {lab.name}...")
                
                try:
                    lab_papers = await self.scrape_lab_papers(lab)
                    total_papers += lab_papers
                    print(f"✅ Found {lab_papers} papers for {lab.name}")
                    
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    print(f"❌ Error scraping {lab.name}: {e}")
                    continue
        
        print(f"\n🎉 Scraping complete! Total papers found: {total_papers}")
        return total_papers
    
    async def scrape_lab_papers(self, lab: Lab) -> int:
        """Scrape papers for a specific lab using multiple strategies"""
        papers_found = 0
        
        # Strategy 1: ArXiv search by PI name and institution
        papers_found += await self.search_arxiv_papers(lab)
        
        # Strategy 2: Google Scholar search
        papers_found += await self.search_scholar_papers(lab)
        
        # Strategy 3: Lab website scraping
        if lab.website:
            papers_found += await self.scrape_website_papers(lab)
        
        return papers_found
    
    async def search_arxiv_papers(self, lab: Lab) -> int:
        """Search ArXiv for papers by lab PI and focus areas"""
        papers_found = 0
        
        try:
            # Create search queries
            queries = self._build_arxiv_queries(lab)
            
            for query in queries:
                try:
                    search = arxiv.Search(
                        query=query,
                        max_results=5,
                        sort_by=arxiv.SortCriterion.Relevance
                    )
                    
                    for paper in search.results():
                        if await self._import_arxiv_paper(paper, lab):
                            papers_found += 1
                            if papers_found >= self.max_papers_per_lab:
                                break
                    
                    if papers_found >= self.max_papers_per_lab:
                        break
                        
                    await asyncio.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"  ArXiv query failed: {query} - {e}")
                    continue
                    
        except Exception as e:
            print(f"  ArXiv search failed for {lab.name}: {e}")
        
        return papers_found
    
    async def search_scholar_papers(self, lab: Lab) -> int:
        """Search Google Scholar for papers"""
        papers_found = 0
        
        try:
            # Search for the PI
            search_query = f"{lab.pi} robotics {lab.institution}"
            search_query = search_query.replace('"', '').strip()
            
            # Use scholarly library
            search_query = scholarly.search_pubs(search_query)
            
            count = 0
            for pub in search_query:
                if count >= 5:  # Limit to avoid rate limiting
                    break
                
                try:
                    # Get publication details
                    pub_filled = scholarly.fill(pub)
                    
                    if await self._import_scholar_paper(pub_filled, lab):
                        papers_found += 1
                        
                    count += 1
                    await asyncio.sleep(2)  # Rate limiting for Scholar
                    
                except Exception as e:
                    print(f"    Scholar paper import failed: {e}")
                    continue
                    
        except Exception as e:
            print(f"  Scholar search failed for {lab.name}: {e}")
        
        return papers_found
    
    async def scrape_website_papers(self, lab: Lab) -> int:
        """Scrape papers from lab website"""
        papers_found = 0
        
        if not lab.website:
            return 0
        
        try:
            # Try common publication page patterns
            pub_urls = [
                f"{lab.website}/publications",
                f"{lab.website}/papers",
                f"{lab.website}/research/publications",
                f"{lab.website}/publications.html",
                f"{lab.website}/papers.html"
            ]
            
            for url in pub_urls:
                try:
                    async with self.session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            papers_found += await self._parse_publication_page(html, lab, url)
                            if papers_found > 0:
                                break  # Found a working publications page
                                
                except Exception as e:
                    continue  # Try next URL pattern
                    
        except Exception as e:
            print(f"  Website scraping failed for {lab.name}: {e}")
        
        return papers_found
    
    def _build_arxiv_queries(self, lab: Lab) -> List[str]:
        """Build ArXiv search queries for a lab"""
        queries = []
        
        # PI name query
        pi_name = lab.pi.replace('"', '').strip()
        if ' ' in pi_name:
            last_name = pi_name.split()[-1]
            queries.append(f'au:"{last_name}" AND (robot OR robotics)')
        
        # Institution + focus areas
        institution_short = lab.institution.split()[0]  # First word of institution
        focus_terms = []
        
        if lab.focus_areas:
            for area in lab.focus_areas[:3]:  # Limit to top 3 focus areas
                area_clean = area.lower().replace('"', '')
                if 'robot' in area_clean or 'learning' in area_clean:
                    focus_terms.append(area_clean)
        
        if focus_terms:
            focus_query = ' OR '.join([f'"{term}"' for term in focus_terms])
            queries.append(f'({focus_query}) AND {institution_short}')
        
        # Generic robotics query for the institution
        queries.append(f'{institution_short} AND (robot learning OR robot manipulation)')
        
        return queries[:3]  # Limit to 3 queries
    
    async def _import_arxiv_paper(self, arxiv_paper, lab: Lab) -> bool:
        """Import a paper from ArXiv"""
        try:
            arxiv_id = arxiv_paper.entry_id.split('/')[-1]
            
            # Check if paper already exists
            existing_paper = Paper.query.filter_by(arxiv_id=arxiv_id).first()
            if existing_paper:
                return False
            
            # Extract paper data
            authors = [str(author) for author in arxiv_paper.authors]
            title = arxiv_paper.title.strip()
            abstract = arxiv_paper.summary.strip()
            
            # Verify relevance to robotics
            if not self._is_robotics_paper(title, abstract):
                return False
            
            paper = Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                publication_date=arxiv_paper.published.date(),
                venue='arXiv',
                paper_type='preprint',
                arxiv_id=arxiv_id,
                pdf_url=arxiv_paper.pdf_url,
                research_areas=self._extract_research_areas(title + " " + abstract),
                keywords=self._extract_keywords(title + " " + abstract),
                lab_id=lab.id,
                citation_count=0
            )
            
            db.session.add(paper)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"    Failed to import ArXiv paper: {e}")
            db.session.rollback()
            return False
    
    async def _import_scholar_paper(self, scholar_paper, lab: Lab) -> bool:
        """Import a paper from Google Scholar"""
        try:
            title = scholar_paper.get('title', '').strip()
            
            if not title:
                return False
            
            # Check if paper already exists
            existing_paper = Paper.query.filter_by(title=title).first()
            if existing_paper:
                return False
            
            # Extract data
            authors = scholar_paper.get('author', '').split(' and ')
            abstract = scholar_paper.get('abstract', '')
            year = scholar_paper.get('year')
            venue = scholar_paper.get('venue', 'Unknown')
            citation_count = scholar_paper.get('num_citations', 0)
            
            # Verify relevance
            if not self._is_robotics_paper(title, abstract):
                return False
            
            # Try to get publication date
            pub_date = None
            if year:
                try:
                    pub_date = datetime(int(year), 1, 1).date()
                except:
                    pub_date = datetime.now().date()
            else:
                pub_date = datetime.now().date()
            
            paper = Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                publication_date=pub_date,
                venue=venue,
                paper_type='journal' if 'journal' in venue.lower() else 'conference',
                research_areas=self._extract_research_areas(title + " " + abstract),
                keywords=self._extract_keywords(title + " " + abstract),
                lab_id=lab.id,
                citation_count=citation_count or 0
            )
            
            db.session.add(paper)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"    Failed to import Scholar paper: {e}")
            db.session.rollback()
            return False
    
    async def _parse_publication_page(self, html: str, lab: Lab, url: str) -> int:
        """Parse a lab's publication page for papers"""
        papers_found = 0
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for paper titles in common patterns
            paper_patterns = [
                'h3',  # Common heading for paper titles
                'h4',
                '.paper-title',
                '.publication-title',
                '.title',
                'strong',
                'b'
            ]
            
            for pattern in paper_patterns:
                elements = soup.select(pattern)
                
                for element in elements[:10]:  # Limit to avoid too many false positives
                    text = element.get_text().strip()
                    
                    # Check if this looks like a paper title
                    if self._looks_like_paper_title(text):
                        if await self._import_website_paper(text, lab, url):
                            papers_found += 1
                            if papers_found >= 5:  # Limit from website scraping
                                break
                
                if papers_found >= 5:
                    break
                    
        except Exception as e:
            print(f"    Failed to parse publication page: {e}")
        
        return papers_found
    
    async def _import_website_paper(self, title: str, lab: Lab, source_url: str) -> bool:
        """Import a paper found on lab website"""
        try:
            # Check if paper already exists
            existing_paper = Paper.query.filter_by(title=title).first()
            if existing_paper:
                return False
            
            paper = Paper(
                title=title,
                authors=[lab.pi],  # Default to PI, could be enhanced
                abstract='',  # Would need additional scraping
                publication_date=datetime.now().date(),
                venue='Lab Website',
                paper_type='website',
                website_url=source_url,
                research_areas=self._extract_research_areas(title),
                keywords=self._extract_keywords(title),
                lab_id=lab.id,
                citation_count=0
            )
            
            db.session.add(paper)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"    Failed to import website paper: {e}")
            db.session.rollback()
            return False
    
    def _is_robotics_paper(self, title: str, abstract: str) -> bool:
        """Check if a paper is related to robotics"""
        text = (title + " " + abstract).lower()
        
        robotics_keywords = [
            'robot', 'robotics', 'robotic', 'manipulation', 'grasp', 'grasping',
            'locomotion', 'navigation', 'slam', 'autonomous', 'reinforcement learning',
            'imitation learning', 'robot learning', 'embodied', 'dexterous',
            'humanoid', 'mobile robot', 'arm', 'gripper', 'actuator', 'sensor fusion'
        ]
        
        return any(keyword in text for keyword in robotics_keywords)
    
    def _looks_like_paper_title(self, text: str) -> bool:
        """Check if text looks like a paper title"""
        if len(text) < 10 or len(text) > 200:
            return False
        
        # Should contain some academic indicators
        indicators = ['learning', 'algorithm', 'method', 'approach', 'system', 'analysis', 'framework']
        has_indicator = any(word in text.lower() for word in indicators)
        
        # Should be properly capitalized
        words = text.split()
        properly_capitalized = sum(1 for word in words if word[0].isupper()) >= len(words) * 0.5
        
        return has_indicator and properly_capitalized and self._is_robotics_paper(text, '')
    
    def _extract_research_areas(self, text: str) -> List[str]:
        """Extract research areas from text"""
        areas = []
        text_lower = text.lower()
        
        area_keywords = {
            'manipulation': ['manipulation', 'grasp', 'grasping', 'pick', 'place'],
            'locomotion': ['locomotion', 'walking', 'running', 'gait', 'legged'],
            'learning': ['learning', 'reinforcement', 'imitation', 'supervised'],
            'perception': ['perception', 'vision', 'visual', 'camera', 'lidar'],
            'navigation': ['navigation', 'path planning', 'slam', 'mapping'],
            'control': ['control', 'controller', 'feedback', 'pid', 'mpc']
        }
        
        for area, keywords in area_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                areas.append(area)
        
        return areas[:5]  # Limit to top 5
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        keywords = [word for word in words if word not in common_words]
        
        # Get most common keywords
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]


async def run_paper_scraper():
    """Main function to run the paper scraper"""
    scraper = LabPaperScraper()
    total_papers = await scraper.scrape_all_labs()
    return total_papers


if __name__ == "__main__":
    # For testing
    import sys
    sys.path.append('..')
    
    # Run the scraper
    total = asyncio.run(run_paper_scraper())
    print(f"Total papers scraped: {total}")