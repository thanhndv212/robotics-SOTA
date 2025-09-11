import nltk
import spacy
from collections import Counter
import re
from typing import List


class NLPProcessor:
    """Service for natural language processing of research papers"""
    
    def __init__(self):
        self._setup_nlp()
        self.research_area_keywords = {
            'manipulation': [
                'manipulation', 'grasping', 'pick and place', 'dexterous',
                'hand', 'gripper', 'robotic arm', 'end effector'
            ],
            'locomotion': [
                'locomotion', 'walking', 'running', 'legged', 'quadruped',
                'biped', 'gait', 'balance', 'dynamic walking'
            ],
            'perception': [
                'perception', 'vision', 'computer vision', 'object detection',
                'semantic segmentation', 'depth estimation', 'slam', 'mapping'
            ],
            'learning': [
                'machine learning', 'deep learning', 'reinforcement learning',
                'imitation learning', 'transfer learning', 'meta learning',
                'neural network', 'policy learning'
            ],
            'control': [
                'control', 'feedback control', 'optimal control', 'mpc',
                'pid', 'adaptive control', 'robust control', 'trajectory'
            ],
            'human_robot_interaction': [
                'human robot interaction', 'hri', 'social robot',
                'assistive robot', 'collaborative robot', 'cobot'
            ],
            'navigation': [
                'navigation', 'path planning', 'motion planning',
                'obstacle avoidance', 'autonomous navigation', 'mapping'
            ],
            'simulation': [
                'simulation', 'sim2real', 'physics simulation',
                'gazebo', 'unity', 'virtual environment'
            ]
        }
    
    def _setup_nlp(self):
        """Setup NLP tools and download required data"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Load spaCy model (fallback to smaller model if large not available)
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
                
        except Exception as e:
            print(f"Failed to setup NLP: {e}")
            self.nlp = None
    
    def extract_research_areas(self, text: str) -> List[str]:
        """Extract research areas from paper text"""
        try:
            text_lower = text.lower()
            found_areas = []
            
            for area, keywords in self.research_area_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        found_areas.append(area)
                        break
            
            return list(set(found_areas))  # Remove duplicates
            
        except Exception as e:
            print(f"Failed to extract research areas: {e}")
            return []
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from paper text"""
        try:
            if not self.nlp:
                return self._extract_keywords_simple(text, max_keywords)
            
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract meaningful phrases
            keywords = []
            
            # Get noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Keep short phrases
                    cleaned = self._clean_keyword(chunk.text)
                    if cleaned and len(cleaned) > 2:
                        keywords.append(cleaned)
            
            # Get important single words
            for token in doc:
                if (token.pos_ in ['NOUN', 'ADJ'] and 
                    not token.is_stop and 
                    not token.is_punct and
                    len(token.text) > 3):
                    cleaned = self._clean_keyword(token.text)
                    if cleaned:
                        keywords.append(cleaned)
            
            # Count and return most common
            keyword_counts = Counter(keywords)
            return [kw for kw, _ in keyword_counts.most_common(max_keywords)]
            
        except Exception as e:
            print(f"Failed to extract keywords: {e}")
            return self._extract_keywords_simple(text, max_keywords)
    
    def _extract_keywords_simple(self, text: str, max_keywords: int) -> List[str]:
        """Simple keyword extraction without spaCy"""
        try:
            # Clean text
            text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = text.split()
            
            # Filter words
            stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 
                            'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are',
                            'was', 'were', 'be', 'been', 'have', 'has', 'had',
                            'do', 'does', 'did', 'will', 'would', 'could',
                            'this', 'that', 'these', 'those'])
            
            filtered_words = [
                word for word in words 
                if len(word) > 3 and word not in stop_words
            ]
            
            # Count and return most common
            word_counts = Counter(filtered_words)
            return [word for word, _ in word_counts.most_common(max_keywords)]
            
        except Exception as e:
            print(f"Failed simple keyword extraction: {e}")
            return []
    
    def _clean_keyword(self, keyword: str) -> str:
        """Clean and normalize a keyword"""
        try:
            # Remove special characters and normalize
            cleaned = re.sub(r'[^\w\s]', '', keyword.strip().lower())
            
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            
            return cleaned if len(cleaned) > 2 else None
            
        except Exception as e:
            return None
    
    def classify_paper_type(self, title: str, venue: str = '') -> str:
        """Classify paper type based on title and venue"""
        try:
            text = (title + ' ' + venue).lower()
            
            if any(word in text for word in ['conference', 'workshop', 'icra', 'iros', 'rss']):
                return 'conference'
            elif any(word in text for word in ['journal', 'transactions', 'ieee', 'acm']):
                return 'journal'
            elif 'arxiv' in text:
                return 'preprint'
            else:
                return 'unknown'
                
        except Exception as e:
            return 'unknown'
    
    def extract_methodology(self, abstract: str) -> List[str]:
        """Extract methodology keywords from abstract"""
        methodology_keywords = {
            'deep_learning': ['deep learning', 'neural network', 'cnn', 'rnn', 'transformer'],
            'reinforcement_learning': ['reinforcement learning', 'q-learning', 'policy gradient', 'actor-critic'],
            'computer_vision': ['computer vision', 'image processing', 'object detection', 'segmentation'],
            'control_theory': ['control theory', 'pid', 'mpc', 'optimal control', 'feedback'],
            'optimization': ['optimization', 'genetic algorithm', 'gradient descent', 'evolutionary'],
            'simulation': ['simulation', 'gazebo', 'unity', 'physics engine', 'virtual']
        }
        
        abstract_lower = abstract.lower()
        found_methods = []
        
        for method, keywords in methodology_keywords.items():
            for keyword in keywords:
                if keyword in abstract_lower:
                    found_methods.append(method)
                    break
        
        return found_methods