#!/usr/bin/env python3
"""
Paper Information Extractor
==========================

A comprehensive tool to extract paper information from JSON and BibTeX formats
and convert them to markdown reference format for system identification and robotics papers.

Usage:
    python paper_extractor.py input_file.json [output_file.md]
    python paper_extractor.py input_file.bib [output_file.md]
    python paper_extractor.py input_file.csv [output_file.md]

"""

import json
import re
import argparse
import sys
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
    BIBTEX_AVAILABLE = True
except ImportError:
    BIBTEX_AVAILABLE = False
    print("Warning: bibtexparser not installed. Install with: pip install bibtexparser")


@dataclass
class PaperInfo:
    """Data class to hold paper information"""
    title: str
    authors: List[str]
    venue: str
    year: Optional[int]
    abstract: str
    paper_type: str
    category: str
    tags: List[str]
    doi: Optional[str] = None
    url: Optional[str] = None
    code: Optional[str] = None
    dataset: Optional[str] = None


class PaperExtractor:
    """Main class for extracting and processing paper information"""
    
    def __init__(self):
        self.sysid_categories = {
            'Foundational Methods': [
                'calibration', 'identification', 'parameter estimation', 'system identification',
                'geometric calibration', 'kinematic calibration', 'dynamic calibration'
            ],
            'Learning Robot Dynamics': [
                'dynamics learning', 'forward dynamics', 'inverse dynamics', 'neural dynamics',
                'learning robot dynamics', 'dynamics modeling', 'physics-informed'
            ],
            'Online and Adaptive Learning': [
                'online', 'adaptive', 'real-time', 'incremental', 'self-calibration',
                'recursive', 'lifelong learning', 'continual learning'
            ],
            'Deep Learning Approaches': [
                'vision-language-action', 'vla model', 'multimodal', 'foundation model',
                'neural network', 'deep learning', 'transformer', 'attention'
            ],
            'Uncertainty Quantification': [
                'uncertainty', 'bayesian', 'gaussian process', 'stochastic', 'probabilistic',
                'monte carlo', 'variance', 'confidence', 'robust'
            ],
            'Multi-Robot and Distributed Systems': [
                'multi-robot', 'distributed', 'consensus', 'federated', 'swarm',
                'cooperative', 'collaborative robots', 'team'
            ],
            'Applications & Domains': [
                'manipulation', 'mobile robot', 'humanoid', 'locomotion', 'wheeled',
                'industrial robot', 'collaborative robot', 'service robot'
            ],
            'Benchmarks and Evaluation': [
                'benchmark', 'toolbox', 'framework', 'evaluation', 'software',
                'dataset', 'metrics', 'comparison', 'survey'
            ]
        }
        
        self.tag_mapping = {
            # System ID and Control
            'calibration': 'calibration',
            'identification': 'parameter-identification',
            'system identification': 'system-identification',
            'parameter estimation': 'parameter-estimation',
            'optimization': 'optimization',
            'control': 'control-systems',
            'adaptive control': 'adaptive-control',
            
            # Robot Types
            'robot': 'robotics',
            'mobile': 'mobile-robots',
            'humanoid': 'humanoid-robots',
            'industrial': 'industrial-robots',
            'collaborative': 'collaborative-robots',
            'manipulator': 'manipulation',
            
            # Learning and AI
            'learning': 'machine-learning',
            'deep learning': 'deep-learning',
            'neural': 'neural-networks',
            'reinforcement learning': 'reinforcement-learning',
            'imitation learning': 'imitation-learning',
            'vision': 'computer-vision',
            'language': 'natural-language',
            'multimodal': 'multimodal-learning',
            
            # Technical Approaches
            'dynamics': 'dynamics-modeling',
            'kinematics': 'kinematics',
            'screw theory': 'screw-theory',
            'lie group': 'lie-groups',
            'uncertainty': 'uncertainty-quantification',
            'bayesian': 'bayesian-methods',
            'gaussian process': 'gaussian-processes',
            
            # Applications
            'manipulation': 'manipulation',
            'locomotion': 'locomotion',
            'navigation': 'navigation',
            'slam': 'slam',
            'planning': 'motion-planning',
            
            # Tools and Resources
            'survey': 'survey',
            'toolbox': 'software-tools',
            'framework': 'framework',
            'benchmark': 'benchmark',
            'dataset': 'dataset',
            'open source': 'open-source'
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ''
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
        text = re.sub(r'\\[a-zA-Z]+', '', text)
        
        # Clean up special characters
        text = text.replace('\\pi_0', 'π₀')
        text = text.replace('\\_', '_')
        text = text.replace('\\&', '&')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()

    def extract_authors_from_json(self, authors_data: List[Dict]) -> List[str]:
        """Extract author names from JSON format"""
        authors = []
        for author in authors_data[:5]:  # Limit to first 5 authors
            if isinstance(author, dict):
                family = author.get('family', '')
                given = author.get('given', '')
                if family:
                    if given:
                        # Use first initial of given name
                        initial = given[0] if given else ''
                        authors.append(f'{family} {initial}')
                    else:
                        authors.append(family)
        
        if len(authors_data) > 5:
            authors.append('et al.')
        
        return authors

    def extract_authors_from_bibtex(self, authors_str: str) -> List[str]:
        """Extract author names from BibTeX format"""
        if not authors_str:
            return []
        
        # Split by 'and' keyword
        author_parts = re.split(r'\s+and\s+', authors_str, flags=re.IGNORECASE)
        authors = []
        
        for author in author_parts[:5]:  # Limit to first 5 authors
            author = author.strip()
            if not author:
                continue
                
            # Handle "Last, First" format
            if ',' in author:
                parts = author.split(',')
                last = parts[0].strip()
                first = parts[1].strip() if len(parts) > 1 else ''
                if first:
                    initial = first[0] if first else ''
                    authors.append(f'{last} {initial}')
                else:
                    authors.append(last)
            else:
                # Handle "First Last" format - take last word as surname
                parts = author.split()
                if len(parts) >= 2:
                    first_initial = parts[0][0] if parts[0] else ''
                    last = parts[-1]
                    authors.append(f'{last} {first_initial}')
                else:
                    authors.append(author)
        
        if len(author_parts) > 5:
            authors.append('et al.')
        
        return authors

    def categorize_paper(self, title: str, abstract: str) -> str:
        """Automatically categorize paper based on content"""
        content = (title + ' ' + abstract).lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in self.sysid_categories.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, default to Foundational Methods
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'Foundational Methods'

    def generate_tags(self, title: str, abstract: str, category: str) -> List[str]:
        """Generate relevant tags based on content"""
        content = (title + ' ' + abstract).lower()
        tags = set()
        
        # Check for tag keywords
        for keyword, tag in self.tag_mapping.items():
            if keyword in content:
                tags.add(tag)
        
        # Add category-specific tags
        category_tags = {
            'Foundational Methods': ['calibration', 'parameter-identification'],
            'Learning Robot Dynamics': ['dynamics-modeling', 'machine-learning'],
            'Online and Adaptive Learning': ['adaptive-control', 'real-time'],
            'Deep Learning Approaches': ['deep-learning', 'neural-networks'],
            'Uncertainty Quantification': ['uncertainty-quantification', 'bayesian-methods'],
            'Multi-Robot and Distributed Systems': ['multi-robot', 'distributed-systems'],
            'Applications & Domains': ['robotics', 'applications'],
            'Benchmarks and Evaluation': ['benchmark', 'evaluation']
        }
        
        if category in category_tags:
            tags.update(category_tags[category])
        
        # Ensure we always have 'robotics' tag if it's robot-related
        if any(term in content for term in ['robot', 'robotic', 'manipulation', 'locomotion']):
            tags.add('robotics')
        
        return list(tags)[:5]  # Limit to 5 tags

    def extract_contributions(self, abstract: str) -> List[str]:
        """Extract key contributions from abstract"""
        if not abstract or len(abstract) < 50:
            return ['Primary research contribution', 'Methodological development', 'Experimental validation']
        
        # Split by sentences and clean
        sentences = [s.strip() for s in abstract.split('.') if len(s.strip()) > 20]
        
        # Take first 3 meaningful sentences
        contributions = []
        for sentence in sentences[:3]:
            if sentence and not sentence.lower().startswith(('this', 'we', 'in this', 'the')):
                contributions.append(sentence)
        
        # Fill with generic contributions if needed
        while len(contributions) < 3:
            generic = [
                'Novel methodology development',
                'Theoretical framework advancement',
                'Experimental validation and results'
            ]
            contributions.append(generic[len(contributions)])
        
        return contributions[:3]

    def extract_methods(self, abstract: str) -> str:
        """Extract methodology information from abstract"""
        if not abstract:
            return 'Research methodology and experimental approach'
        
        method_indicators = ['method', 'approach', 'algorithm', 'technique', 'framework', 'model', 'system']
        
        for indicator in method_indicators:
            if indicator in abstract.lower():
                # Find sentence containing the method indicator
                for sentence in abstract.split('.'):
                    if indicator in sentence.lower() and len(sentence.strip()) > 15:
                        clean_sentence = sentence.strip()[:100]
                        return clean_sentence + ('...' if len(sentence.strip()) > 100 else '')
        
        return 'Systematic research methodology and analysis'

    def determine_applications(self, title: str, abstract: str) -> str:
        """Determine application domain from content"""
        content = (title + ' ' + abstract).lower()
        
        app_mapping = {
            'mobile robot': 'Mobile robotics platforms and systems',
            'humanoid': 'Humanoid robot systems and applications',
            'industrial': 'Industrial automation and manufacturing systems',
            'manipulation': 'Robot manipulation and grasping systems',
            'calibration': 'Robot calibration and parameter identification',
            'control': 'Robot control and automation systems',
            'navigation': 'Robot navigation and localization systems',
            'vision': 'Computer vision and perception systems',
            'learning': 'Machine learning and adaptive systems'
        }
        
        for term, application in app_mapping.items():
            if term in content:
                return application
        
        return 'Robotics and automation systems'

    def parse_json_file(self, filepath: Path) -> List[PaperInfo]:
        """Parse JSON file and extract paper information"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return []
        
        papers = []
        
        for item in data:
            if not isinstance(item, dict) or 'title' not in item:
                continue
            
            title = self.clean_text(item.get('title', ''))
            if not title or len(title) < 5:
                continue
            
            # Skip non-meaningful entries
            if title.lower() in ['team lrn', 'gr00t n1.5']:
                continue
            
            # Extract basic information
            abstract = self.clean_text(item.get('abstract', ''))
            authors = self.extract_authors_from_json(item.get('author', []))
            venue = item.get('container-title', '')
            
            # Extract year
            year = None
            if item.get('issued') and item['issued'].get('date-parts'):
                try:
                    year = int(item['issued']['date-parts'][0][0])
                except (IndexError, ValueError, TypeError):
                    pass
            
            # Determine category and generate tags
            category = self.categorize_paper(title, abstract)
            tags = self.generate_tags(title, abstract, category)
            
            # Extract DOI and URL
            doi = item.get('DOI') or item.get('doi')
            url = item.get('URL') or item.get('url')
            
            paper = PaperInfo(
                title=title,
                authors=authors,
                venue=venue,
                year=year,
                abstract=abstract,
                paper_type=item.get('type', ''),
                category=category,
                tags=tags,
                doi=doi,
                url=url
            )
            
            papers.append(paper)
        
        return papers

    def parse_bibtex_file(self, filepath: Path) -> List[PaperInfo]:
        """Parse BibTeX file and extract paper information"""
        if not BIBTEX_AVAILABLE:
            print("Error: bibtexparser is required for BibTeX files. Install with: pip install bibtexparser")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                parser = BibTexParser(common_strings=True)
                parser.customization = convert_to_unicode
                bib_database = bibtexparser.load(f, parser=parser)
        except Exception as e:
            print(f"Error reading BibTeX file: {e}")
            return []
        
        papers = []
        
        for entry in bib_database.entries:
            title = self.clean_text(entry.get('title', ''))
            if not title or len(title) < 5:
                continue
            
            # Extract basic information
            abstract = self.clean_text(entry.get('abstract', ''))
            authors = self.extract_authors_from_bibtex(entry.get('author', ''))
            
            # Extract venue information
            venue = entry.get('journal', '') or entry.get('booktitle', '') or entry.get('publisher', '')
            
            # Extract year
            year = None
            if entry.get('year'):
                try:
                    year = int(entry.get('year'))
                except ValueError:
                    pass
            
            # Determine category and generate tags
            category = self.categorize_paper(title, abstract)
            tags = self.generate_tags(title, abstract, category)
            
            # Extract DOI and URL
            doi = entry.get('doi')
            url = entry.get('url')
            
            paper = PaperInfo(
                title=title,
                authors=authors,
                venue=venue,
                year=year,
                abstract=abstract,
                paper_type=entry.get('ENTRYTYPE', ''),
                category=category,
                tags=tags,
                doi=doi,
                url=url
            )
            
            papers.append(paper)
        
        return papers

    def extract_authors_from_csv(self, authors_str: str) -> List[str]:
        """Extract author names from CSV format (various delimiters)"""
        if not authors_str:
            return []
        
        # Try different separators commonly used in CSV exports
        separators = [';', ',', '|', ' and ', ' & ']
        authors = []
        
        # Find the best separator by checking which one gives reasonable results
        best_separation = [authors_str]  # Default to single author
        for sep in separators:
            if sep in authors_str:
                parts = authors_str.split(sep)
                if len(parts) > 1 and all(len(p.strip()) > 1 for p in parts):
                    best_separation = parts
                    break
        
        for author in best_separation[:8]:  # Allow more authors for full names
            author = author.strip()
            if not author:
                continue
                
            # Clean up common CSV formatting issues
            author = author.replace('"', '').replace("'", "")
            
            # Handle "Last, First Middle" format - preserve full names
            if ',' in author:
                parts = author.split(',')
                last = parts[0].strip()
                first_middle = parts[1].strip() if len(parts) > 1 else ''
                if first_middle:
                    # Preserve full first and middle names
                    authors.append(f'{first_middle} {last}')
                else:
                    authors.append(last)
            else:
                # Keep the full name as-is for "First Middle Last" format
                authors.append(author)
        
        if len(best_separation) > 8:
            authors.append('et al.')
        
        return authors

    def parse_csv_file(self, filepath: Path) -> List[PaperInfo]:
        """Parse CSV file and extract paper information"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Try to detect the CSV dialect
                sample = f.read(1024)
                f.seek(0)
                
                # Use csv.Sniffer to detect delimiter
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    reader = csv.DictReader(f, dialect=dialect)
                except csv.Error:
                    # Fallback to comma delimiter
                    reader = csv.DictReader(f)
                
                # Get all rows
                rows = list(reader)
                
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []
        
        if not rows:
            print("No data found in CSV file")
            return []
        
        print(f"CSV file has {len(rows)} entries")
        print("Available columns:", list(rows[0].keys())[:10])  # Show first 10 columns
        
        papers = []
        
        # Common field mappings for different CSV export formats
        field_mappings = {
            'title': ['title', 'Title', 'TITLE', 'paper_title', 'article_title'],
            'authors': ['authors', 'Authors', 'AUTHORS', 'author', 'Author', 'creators', 'Creators'],
            'abstract': ['abstract', 'Abstract', 'ABSTRACT', 'description', 'Description', 'summary', 'Summary'],
            'venue': ['venue', 'Venue', 'journal', 'Journal', 'publication', 'Publication', 'source', 'Source', 'conference', 'Conference'],
            'year': ['year', 'Year', 'YEAR', 'date', 'Date', 'published_year', 'publication_year'],
            'doi': ['doi', 'DOI', 'Doi', 'digital_object_identifier'],
            'url': ['url', 'URL', 'Url', 'URLs', 'urls', 'link', 'Link',
                    'Links', 'links', 'web_address', 'website'],
            'type': ['type', 'Type', 'TYPE', 'document_type',
                     'publication_type', 'item_type', 'Item type']
        }
        
        # Auto-detect field mappings
        available_fields = list(rows[0].keys())
        field_map = {}
        
        for field, possible_names in field_mappings.items():
            for name in possible_names:
                if name in available_fields:
                    field_map[field] = name
                    break
        
        print("Detected field mappings:", field_map)
        
        for row in rows:
            # Extract title
            title = ''
            if 'title' in field_map:
                title = self.clean_text(row.get(field_map['title'], ''))
            
            if not title or len(title) < 5:
                continue
            
            # Skip non-meaningful entries
            if title.lower() in ['team lrn', 'gr00t n1.5']:
                continue
            
            # Extract other fields
            abstract = ''
            if 'abstract' in field_map:
                abstract = self.clean_text(row.get(field_map['abstract'], ''))
            
            # Extract authors
            authors = []
            if 'authors' in field_map:
                authors_str = row.get(field_map['authors'], '')
                authors = self.extract_authors_from_csv(authors_str)
            
            # Extract venue
            venue = ''
            if 'venue' in field_map:
                venue = row.get(field_map['venue'], '')
            
            # Extract year
            year = None
            if 'year' in field_map:
                year_str = row.get(field_map['year'], '')
                if year_str:
                    # Try to extract year from various formats
                    year_match = re.search(r'\b(19|20)\d{2}\b', str(year_str))
                    if year_match:
                        try:
                            year = int(year_match.group())
                        except ValueError:
                            pass
            
            # Extract DOI and URL
            doi = ''
            if 'doi' in field_map:
                doi = row.get(field_map['doi'], '')
            
            url = ''
            if 'url' in field_map:
                urls_raw = row.get(field_map['url'], '')
                if urls_raw:
                    # Handle multiple URLs separated by semicolons
                    urls = [u.strip() for u in urls_raw.split(';')
                            if u.strip()]
                    if urls:
                        # Prefer arXiv or DOI URLs, otherwise take first
                        url = urls[0]  # Default to first URL
                        for u in urls:
                            if ('arxiv.org' in u.lower() or
                                    'doi.org' in u.lower()):
                                url = u
                                break
            
            # Extract paper type
            paper_type = ''
            if 'type' in field_map:
                paper_type = row.get(field_map['type'], '')
            
            # Determine category and generate tags
            category = self.categorize_paper(title, abstract)
            tags = self.generate_tags(title, abstract, category)
            
            paper = PaperInfo(
                title=title,
                authors=authors,
                venue=venue,
                year=year,
                abstract=abstract,
                paper_type=paper_type,
                category=category,
                tags=tags,
                doi=doi,
                url=url
            )
            
            papers.append(paper)
        
        return papers

    def generate_markdown(self, papers: List[PaperInfo]) -> str:
        """Generate markdown content from paper information"""
        # Group papers by category
        categories = {}
        for paper in papers:
            if paper.category not in categories:
                categories[paper.category] = []
            categories[paper.category].append(paper)
        
        # Generate header
        markdown = f"""# Papers Collection 🤖📚

Extracted from library with {len(papers)} papers across {len(categories)} categories.

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistical Overview

"""
        
        # Add category statistics
        for category, paper_list in sorted(categories.items()):
            markdown += f"- **{category}**: {len(paper_list)} papers\n"
        
        markdown += "\n## Papers by Category\n\n"
        
        # Category order
        category_order = [
            'Foundational Methods',
            'Learning Robot Dynamics',
            'Online and Adaptive Learning',
            'Deep Learning Approaches',
            'Uncertainty Quantification',
            'Multi-Robot and Distributed Systems',
            'Applications & Domains',
            'Benchmarks and Evaluation'
        ]
        
        # Process each category
        for category in category_order:
            if category not in categories:
                continue
            
            papers_in_category = categories[category]
            markdown += f"### {category} ({len(papers_in_category)} papers)\n\n"
            
            for i, paper in enumerate(papers_in_category, 1):
                # Format authors
                authors_str = ', '.join(paper.authors) if paper.authors else 'Unknown'
                
                # Format venue and year
                venue_parts = []
                if paper.venue:
                    venue_parts.append(paper.venue)
                if paper.year:
                    venue_parts.append(str(paper.year))
                venue_str = ', '.join(venue_parts) if venue_parts else 'Unknown'
                
                # Generate link (use DOI if available, otherwise placeholder)
                if paper.doi:
                    link = f"https://doi.org/{paper.doi}"
                elif paper.url:
                    link = paper.url
                else:
                    link = "#"
                
                # Generate summary
                summary = paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract
                if not summary:
                    summary = f"Research paper in {category.lower()}"
                
                # Extract contributions
                contributions = self.extract_contributions(paper.abstract)
                
                # Extract methods and applications
                methods = self.extract_methods(paper.abstract)
                applications = self.determine_applications(paper.title, paper.abstract)
                
                # Format tags
                tags_str = ', '.join(f'`{tag}`' for tag in paper.tags) if paper.tags else '`robotics`'
                
                # Code and dataset info
                code_info = "Available" if paper.code else "N/A"
                dataset_info = "Available" if paper.dataset else "N/A"
                
                markdown += f"""#### {i}. [{paper.title}]({link})
**Authors**: {authors_str}  
**Venue**: {venue_str}  
**Category**: {category}

**Summary**: {summary}

**Key Contributions**:
"""
                
                for contrib in contributions:
                    markdown += f"- {contrib}\n"
                
                markdown += f"""
**Methods**: {methods}

**Applications**: {applications}

**Code**: {code_info} | **Dataset**: {dataset_info}

**Tags**: {tags_str}

---

"""
        
        return markdown

    def process_file(self, input_file: Path, output_file: Optional[Path] = None) -> bool:
        """Process input file and generate markdown output"""
        print(f"Processing {input_file}...")
        
        # Determine file type and parse
        if input_file.suffix.lower() == '.json':
            papers = self.parse_json_file(input_file)
        elif input_file.suffix.lower() in ['.bib', '.bibtex']:
            papers = self.parse_bibtex_file(input_file)
        elif input_file.suffix.lower() == '.csv':
            papers = self.parse_csv_file(input_file)
        else:
            print(f"Error: Unsupported file format '{input_file.suffix}'")
            print("Supported formats: .json, .bib, .bibtex, .csv")
            return False
        
        if not papers:
            print("No papers found or error in processing.")
            return False
        
        print(f"Found {len(papers)} papers")
        
        # Generate markdown
        markdown_content = self.generate_markdown(papers)
        
        # Determine output file
        if output_file is None:
            output_file = input_file.parent / f"{input_file.stem}_papers.md"
        
        # Write output
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Successfully created: {output_file}")
            return True
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description=("Extract paper information from JSON/BibTeX/CSV files "
                     "and convert to markdown"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python paper_extractor.py library.json
    python paper_extractor.py references.bib output.md
    python paper_extractor.py papers.csv --output results.md
    python paper_extractor.py library.json extracted_papers.md
        """
    )
    
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input file (JSON or BibTeX format)'
    )
    
    parser.add_argument(
        'output_file',
        type=Path,
        nargs='?',
        help='Output markdown file (optional, auto-generated if not provided)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        dest='output_file_alt',
        help='Alternative way to specify output file'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input_file.exists():
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Determine output file
    output_file = args.output_file or args.output_file_alt
    
    # Create extractor and process file
    extractor = PaperExtractor()
    success = extractor.process_file(args.input_file, output_file)
    
    if success:
        print("✓ Paper extraction completed successfully!")
        sys.exit(0)
    else:
        print("✗ Paper extraction failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
