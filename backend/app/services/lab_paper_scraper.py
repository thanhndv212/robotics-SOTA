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
        self.rate_limit_delay = 1  # Reduced from 2 to 1 second
        self.max_papers_per_lab = 15  # Increased from 10 to 15
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
    
    async def scrape_lab_papers(self, lab: Lab, sources: List[str] = None, max_papers: int = None) -> int:
        """Scrape papers for a specific lab using multiple strategies"""
        if sources is None:
            sources = ['arxiv', 'scholar', 'website']
        if max_papers is not None:
            self.max_papers_per_lab = max_papers
            
        papers_found = 0
        
        # Strategy 1: ArXiv search by PI name and institution
        if 'arxiv' in sources:
            papers_found += await self.search_arxiv_papers(lab)
        
        # Strategy 2: Google Scholar search
        if 'scholar' in sources:
            papers_found += await self.search_scholar_papers(lab)
        
        # Strategy 3: Lab website scraping
        if 'website' in sources and lab.website:
            papers_found += await self.scrape_website_papers(lab)
        
        return papers_found
    
    async def search_arxiv_papers(self, lab: Lab) -> int:
        """Search ArXiv for papers by lab PI and focus areas"""
        papers_found = 0
        
        try:
            # Create search queries
            queries = self._build_arxiv_queries(lab)
            print(f"  🔍 ArXiv queries for {lab.name}: {queries}")
            
            for query in queries:
                try:
                    print(f"  📝 Executing query: {query}")
                    search = arxiv.Search(
                        query=query,
                        max_results=min(10, self.max_papers_per_lab),  # Increased from 5 to 10
                        sort_by=arxiv.SortCriterion.SubmittedDate  # Changed to submitted date for more recent papers
                    )
                    
                    query_papers = 0
                    for paper in search.results():
                        print(f"    📄 Found paper: {paper.title}")
                        if await self._import_arxiv_paper(paper, lab):
                            papers_found += 1
                            query_papers += 1
                            print(f"    ✅ Imported paper")
                        else:
                            print(f"    ⏭️  Skipped paper (duplicate or not robotics-related)")
                            
                        if papers_found >= self.max_papers_per_lab:
                            break
                    
                    print(f"  📊 Query found {query_papers} new papers")
                    
                    if papers_found >= self.max_papers_per_lab:
                        break
                        
                    await asyncio.sleep(0.5)  # Reduced rate limiting from 1s to 0.5s
                    
                except Exception as e:
                    print(f"  ❌ ArXiv query failed: {query} - {e}")
                    continue
                    
        except Exception as e:
            print(f"  ❌ ArXiv search failed for {lab.name}: {e}")
        
        print(f"  📚 Total ArXiv papers found for {lab.name}: {papers_found}")
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
    
    async def scrape_institutional_papers(self, institution: str, max_papers: int = 10) -> List[dict]:
        """Scrape papers from an institution that might not belong to existing labs"""
        papers = []
        
        try:
            # Build institutional queries
            queries = self._build_institutional_queries(institution)
            print(f"  🔍 Institutional queries for {institution}: {queries}")
            
            for query in queries:
                try:
                    print(f"  📝 Executing institutional query: {query}")
                    search = arxiv.Search(
                        query=query,
                        max_results=max_papers // len(queries) + 1,  # Distribute across queries
                        sort_by=arxiv.SortCriterion.SubmittedDate
                    )
                    
                    for paper in search.results():
                        print(f"    📄 Found institutional paper: {paper.title}")
                        
                        # Check if this paper belongs to any existing lab
                        if await self._paper_belongs_to_existing_lab(paper):
                            print(f"    ⏭️  Paper belongs to existing lab, skipping")
                            continue
                        
                        # Verify relevance to robotics (stricter filter for institutional search)
                        if not self._is_robotics_paper(paper.title, paper.summary, relaxed=False):
                            print(f"    ⏭️  Paper not relevant to robotics")
                            continue
                        
                        # Extract paper data
                        authors = [str(author) for author in paper.authors]
                        paper_data = {
                            'title': paper.title.strip(),
                            'authors': authors,
                            'abstract': paper.summary.strip(),
                            'publication_date': paper.published.date().isoformat(),
                            'venue': 'arXiv',
                            'paper_type': 'preprint',
                            'arxiv_id': paper.entry_id.split('/')[-1],
                            'pdf_url': paper.pdf_url,
                            'institution': institution,
                            'discovered_via': 'institutional_search'
                        }
                        
                        papers.append(paper_data)
                        print(f"    ✅ Added institutional paper")
                        
                        if len(papers) >= max_papers:
                            break
                    
                    if len(papers) >= max_papers:
                        break
                        
                    await asyncio.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"  ❌ Institutional query failed: {query} - {e}")
                    continue
                    
        except Exception as e:
            print(f"  ❌ Institutional search failed for {institution}: {e}")
        
        print(f"  📚 Total institutional papers found for {institution}: {len(papers)}")
        return papers
    
    def _build_institutional_queries(self, institution: str) -> List[str]:
        """Build queries to find robotics papers from an institution"""
        institution_short = institution.split()[0]  # First word
        
        queries = [
            f'{institution_short} AND (robot learning)',
            f'{institution_short} AND (robot manipulation)', 
            f'{institution_short} AND (autonomous robot)',
            f'{institution_short} AND (robotics AND learning)',
            f'{institution_short} AND (embodied ai)',
            f'{institution_short} AND (robot perception)',
        ]
        
        return queries[:4]  # Limit to 4 queries
    
    async def _paper_belongs_to_existing_lab(self, arxiv_paper) -> bool:
        """Check if a paper belongs to any existing lab by checking authors"""
        from app.models import Lab
        
        # Get all lab PIs
        labs = Lab.query.all()
        pi_last_names = set()
        
        for lab in labs:
            if lab.pi and lab.pi != 'Multiple PIs':
                pi_name = lab.pi.strip()
                if ' ' in pi_name:
                    last_name = pi_name.split()[-1].lower()
                    pi_last_names.add(last_name)
        
        # Check if any paper author matches a known PI
        paper_authors = [str(author).lower() for author in arxiv_paper.authors]
        
        for author in paper_authors:
            author_last_name = author.split()[-1] if ' ' in author else author
            if author_last_name in pi_last_names:
                return True
        
        return False
    
    def _build_arxiv_queries(self, lab: Lab) -> List[str]:
        """Build ArXiv search queries for a lab"""
        import json
        queries = []
        
        # PI name query (more specific)
        pi_name = lab.pi.replace('"', '').strip()
        if ' ' in pi_name:
            last_name = pi_name.split()[-1]
            # More focused query - author + robotics terms
            queries.append(f'au:"{last_name}" AND (robot OR robotics OR autonomous OR manipulation)')
            
            # Also try full name for highly prolific authors
            if len(pi_name.split()) == 2:
                first_name = pi_name.split()[0][:3]  # First 3 letters to handle variations
                queries.append(f'au:"{first_name}*{last_name}" AND (robot OR learning)')
        
        # Focus area queries (without institution restriction)
        if lab.focus_areas:
            try:
                # Parse JSON string to list
                focus_list = json.loads(lab.focus_areas)
                for area in focus_list[:2]:  # Top 2 focus areas only
                    area_clean = area.lower().replace('"', '').strip()
                    if len(area_clean) > 3:  # Avoid very short terms
                        # Create focused search for this area
                        if 'learning' in area_clean:
                            queries.append(f'"{area_clean}" AND robot')
                        elif 'robot' in area_clean:
                            queries.append(f'"{area_clean}"')
                        elif any(term in area_clean for term in ['manipulation', 'perception', 'navigation', 'control']):
                            queries.append(f'"{area_clean}" AND (robot OR robotics)')
            except (json.JSONDecodeError, TypeError):
                # Fallback: treat as comma-separated string
                focus_list = lab.focus_areas.split(',')
                for area in focus_list[:2]:
                    area_clean = area.strip().lower().replace('"', '')
                    if len(area_clean) > 3:
                        queries.append(f'"{area_clean}" AND robot')
        
        # Lab name based query (extract meaningful terms)
        lab_name_clean = lab.name.lower()
        lab_terms = []
        
        # Extract specific robotics terms from lab name
        robotics_terms = ['manipulation', 'perception', 'learning', 'locomotion', 'navigation', 'vision', 'control']
        for term in robotics_terms:
            if term in lab_name_clean:
                lab_terms.append(term)
        
        if lab_terms:
            # Create a focused query with lab-specific terms
            lab_query = ' OR '.join(lab_terms)
            queries.append(f'({lab_query}) AND robot')
        
        # Generic robotics query with PI if no specific terms found
        if not queries or len(queries) < 2:
            if pi_name and ' ' in pi_name:
                last_name = pi_name.split()[-1]
                queries.append(f'au:"{last_name}" AND (deep learning OR reinforcement learning)')
        
        # Remove duplicates and limit
        unique_queries = []
        for q in queries:
            if q not in unique_queries:
                unique_queries.append(q)
        
        return unique_queries[:3]  # Limit to 3 most relevant queries
    
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
            
            # Verify relevance to robotics - relaxed filter for author-based search
            if not self._is_robotics_paper(title, abstract, relaxed=True):
                return False
            
            import json
            
            paper = Paper(
                title=title,
                authors=json.dumps(authors),  # Convert list to JSON string
                abstract=abstract,
                publication_date=arxiv_paper.published.date(),
                venue='arXiv',
                paper_type='preprint',
                arxiv_id=arxiv_id,
                pdf_url=arxiv_paper.pdf_url,
                research_areas=json.dumps(self._extract_research_areas(title + " " + abstract)),  # Convert to JSON
                keywords=json.dumps(self._extract_keywords(title + " " + abstract)),  # Convert to JSON
                lab_id=lab.id,
                citation_count=0
            )
            
            db.session.add(paper)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"    Failed to import ArXiv paper: {e}")
            try:
                db.session.rollback()
            except:
                pass
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
            
            # Verify relevance - relaxed filter for scholar search
            if not self._is_robotics_paper(title, abstract, relaxed=True):
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
            
            import json
            
            paper = Paper(
                title=title,
                authors=json.dumps(authors),  # Convert list to JSON string
                abstract=abstract,
                publication_date=pub_date,
                venue=venue,
                paper_type='journal' if 'journal' in venue.lower() else 'conference',
                research_areas=json.dumps(self._extract_research_areas(title + " " + abstract)),  # Convert to JSON
                keywords=json.dumps(self._extract_keywords(title + " " + abstract)),  # Convert to JSON
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
    
    def _is_robotics_paper(self, title: str, abstract: str, relaxed: bool = False) -> bool:
        """Check if a paper is related to robotics
        
        Args:
            title: Paper title
            abstract: Paper abstract  
            relaxed: If True, use more lenient filtering (for author-based searches)
        """
        text = (title + " " + abstract).lower()
        
        if relaxed:
            # More relaxed filter for papers by known robotics researchers
            relaxed_keywords = [
                # Core robotics terms
                'robot', 'robotics', 'robotic', 'automation', 'autonomous', 'humanoid', 'android',
                'cyborg', 'mechatronic', 'mechatronics', 'mobile robot', 'service robot',
                
                # Manipulation & grasping
                'manipulation', 'grasp', 'grasping', 'gripping', 'gripper', 'end-effector',
                'pick and place', 'pick-and-place', 'dexterous', 'dexterity', 'fine motor',
                'object handling', 'tactile', 'haptic', 'force feedback', 'torque control',
                
                # Locomotion & movement
                'locomotion', 'walking', 'running', 'jumping', 'climbing', 'swimming',
                'flying', 'hovering', 'gait', 'legged', 'bipedal', 'quadrupedal',
                'wheeled', 'tracked', 'aerial', 'underwater', 'ground vehicle',
                
                # Navigation & mapping
                'navigation', 'path planning', 'route planning', 'slam', 'mapping',
                'localization', 'odometry', 'waypoint', 'obstacle avoidance',
                'collision avoidance', 'motion planning', 'trajectory', 'pathfinding',
                
                # Learning & AI
                'reinforcement learning', 'imitation learning', 'robot learning',
                'embodied learning', 'transfer learning', 'meta-learning',
                'neural', 'deep learning', 'machine learning', 'ai', 'artificial intelligence',
                'neural network', 'deep neural', 'convolutional', 'recurrent', 'transformer',
                'policy', 'policy gradient', 'q-learning', 'actor-critic', 'supervised learning',
                'unsupervised learning', 'semi-supervised', 'self-supervised',
                
                # Perception & sensing
                'perception', 'vision', 'computer vision', 'visual', 'camera', 'stereo vision',
                'lidar', 'radar', 'sonar', 'ultrasonic', 'sensor fusion', 'multi-modal',
                'rgb-d', 'point cloud', 'depth estimation', 'object detection',
                'object recognition', 'scene understanding', 'semantic segmentation',
                
                # Control & dynamics
                'control', 'optimal control', 'adaptive control', 'robust control',
                'model predictive control', 'mpc', 'pid', 'feedback control',
                'dynamics', 'kinematics', 'actuator', 'servo', 'motor control',
                'force control', 'impedance control', 'admittance control',
                
                # Simulation & modeling
                'simulation', 'simulator', 'virtual', 'digital twin', 'modeling',
                'physics simulation', 'gazebo', 'unity', 'unreal', 'mujoco',
                'real-to-sim', 'sim-to-real', 'domain adaptation',
                
                # Human-robot interaction
                'human-robot interaction', 'hri', 'human-robot collaboration',
                'social robot', 'assistive robot', 'companion robot',
                'gesture recognition', 'speech recognition', 'natural language',
                
                # Specific applications
                'industrial robot', 'manufacturing', 'assembly', 'welding',
                'medical robot', 'surgical robot', 'rehabilitation robot',
                'agricultural robot', 'cleaning robot', 'security robot',
                'search and rescue', 'exploration', 'inspection',
                
                # Advanced concepts
                'swarm robotics', 'multi-robot', 'distributed', 'cooperative',
                'bio-inspired', 'biomimetic', 'soft robotics', 'continuum robot',
                'compliant', 'elastic', 'morphology', 'embodied intelligence'
            ]
        else:
            # Stricter filter for general searches
            relaxed_keywords = [
                # Core robotics terms
                'robot', 'robotics', 'robotic', 'autonomous', 'humanoid',
                'mobile robot', 'service robot', 'industrial robot',
                
                # Manipulation
                'manipulation', 'grasp', 'grasping', 'gripper', 'dexterous',
                'pick and place', 'end-effector', 'tactile', 'haptic',
                
                # Locomotion
                'locomotion', 'walking', 'gait', 'legged', 'bipedal', 'quadrupedal',
                'navigation', 'path planning', 'slam', 'mapping', 'localization',
                
                # Learning & control
                'reinforcement learning', 'imitation learning', 'robot learning',
                'embodied', 'control', 'optimal control', 'planning', 'policy',
                'actuator', 'sensor fusion', 'perception', 'vision',
                
                # Key applications
                'human-robot interaction', 'manipulation', 'navigation',
                'autonomous vehicle', 'medical robot', 'assembly robot'
            ]
        
        return any(keyword in text for keyword in relaxed_keywords)
    
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
        
        return has_indicator and properly_capitalized and self._is_robotics_paper(text, '', relaxed=False)
    
    def _extract_research_areas(self, text: str) -> List[str]:
        """Extract research areas from text"""
        areas = []
        text_lower = text.lower()
        
        area_keywords = {
            'manipulation': [
                'manipulation', 'grasp', 'grasping', 'gripping', 'gripper', 'pick', 'place',
                'pick and place', 'pick-and-place', 'dexterous', 'dexterity', 'end-effector',
                'tactile', 'haptic', 'force feedback', 'object handling', 'fine motor',
                'assembly', 'welding', 'sorting', 'bin picking'
            ],
            'locomotion': [
                'locomotion', 'walking', 'running', 'jumping', 'climbing', 'gait', 'legged',
                'bipedal', 'quadrupedal', 'hexapod', 'wheeled', 'tracked', 'flying',
                'aerial', 'drone', 'uav', 'underwater', 'swimming', 'hovering',
                'balance', 'stability', 'dynamic walking', 'terrain adaptation'
            ],
            'learning': [
                'learning', 'reinforcement learning', 'imitation learning', 'supervised learning',
                'unsupervised learning', 'transfer learning', 'meta-learning', 'few-shot learning',
                'neural network', 'deep learning', 'machine learning', 'policy learning',
                'reward', 'q-learning', 'actor-critic', 'policy gradient', 'demonstration',
                'self-supervised', 'continual learning', 'lifelong learning'
            ],
            'perception': [
                'perception', 'vision', 'computer vision', 'visual', 'camera', 'stereo vision',
                'lidar', 'radar', 'sonar', 'rgb-d', 'depth', 'point cloud', 'sensor fusion',
                'object detection', 'object recognition', 'segmentation', 'tracking',
                'scene understanding', 'semantic mapping', 'visual odometry', 'feature extraction'
            ],
            'navigation': [
                'navigation', 'path planning', 'route planning', 'slam', 'mapping', 'localization',
                'waypoint', 'obstacle avoidance', 'collision avoidance', 'motion planning',
                'trajectory planning', 'pathfinding', 'exploration', 'coverage',
                'autonomous navigation', 'gps', 'indoor navigation', 'outdoor navigation'
            ],
            'control': [
                'control', 'controller', 'feedback', 'pid', 'mpc', 'model predictive control',
                'optimal control', 'adaptive control', 'robust control', 'force control',
                'position control', 'velocity control', 'impedance control', 'admittance control',
                'dynamics', 'kinematics', 'actuator', 'servo', 'motor control', 'stabilization'
            ],
            'human_robot_interaction': [
                'human-robot interaction', 'hri', 'human-robot collaboration', 'social robot',
                'assistive robot', 'companion robot', 'gesture recognition', 'speech recognition',
                'natural language', 'emotion recognition', 'eye tracking', 'telepresence',
                'shared control', 'cooperative', 'collaborative'
            ],
            'simulation': [
                'simulation', 'simulator', 'virtual', 'digital twin', 'modeling', 'gazebo',
                'unity', 'unreal', 'mujoco', 'bullet', 'physics simulation', 'real-to-sim',
                'sim-to-real', 'domain adaptation', 'synthetic data', 'virtual environment'
            ],
            'swarm_robotics': [
                'swarm robotics', 'multi-robot', 'distributed', 'cooperative', 'collective',
                'consensus', 'formation control', 'flocking', 'coordination', 'multi-agent',
                'decentralized', 'emergent behavior', 'self-organization'
            ],
            'soft_robotics': [
                'soft robotics', 'soft robot', 'continuum robot', 'compliant', 'elastic',
                'pneumatic', 'hydraulic', 'shape memory', 'bio-inspired', 'biomimetic',
                'morphology', 'deformable', 'flexible', 'cable-driven'
            ]
        }
        
        for area, keywords in area_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                areas.append(area)
        
        return areas[:8]  # Limit to top 8 areas (increased from 5 to accommodate new categories)
    
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