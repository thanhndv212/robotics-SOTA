from app import db
from datetime import datetime
import json


class Lab(db.Model):
    __tablename__ = 'labs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    pi = db.Column(db.String(100), nullable=True)
    institution = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    focus_areas = db.Column(db.Text, nullable=True)  # JSON string
    website = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    established_year = db.Column(db.Integer, nullable=True)
    funding_sources = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    papers = db.relationship('Paper', backref='lab', lazy=True)
    researchers = db.relationship('Researcher', backref='lab', lazy=True)
    
    @property
    def focus_areas_list(self):
        """Get focus areas as list"""
        if self.focus_areas:
            try:
                return json.loads(self.focus_areas)
            except:
                return []
        return []
    
    @focus_areas_list.setter
    def focus_areas_list(self, value):
        """Set focus areas from list"""
        if value:
            self.focus_areas = json.dumps(value)
        else:
            self.focus_areas = None
    
    @property
    def funding_sources_list(self):
        """Get funding sources as list"""
        if self.funding_sources:
            try:
                return json.loads(self.funding_sources)
            except:
                return []
        return []
    
    @funding_sources_list.setter
    def funding_sources_list(self, value):
        """Set funding sources from list"""
        if value:
            self.funding_sources = json.dumps(value)
        else:
            self.funding_sources = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pi': self.pi,
            'institution': self.institution,
            'city': self.city,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'focus_areas': self.focus_areas_list,
            'website': self.website,
            'description': self.description,
            'established_year': self.established_year,
            'funding_sources': self.funding_sources_list,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Paper(db.Model):
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.Text, nullable=False)  # JSON string
    abstract = db.Column(db.Text, nullable=True)
    publication_date = db.Column(db.Date, nullable=True)
    venue = db.Column(db.String(200), nullable=True)
    paper_type = db.Column(db.String(50), nullable=True)  # conference, journal, preprint
    arxiv_id = db.Column(db.String(50), nullable=True, unique=True)
    doi = db.Column(db.String(100), nullable=True)
    pdf_url = db.Column(db.String(500), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    citation_count = db.Column(db.Integer, default=0)
    research_areas = db.Column(db.Text, nullable=True)  # JSON string
    keywords = db.Column(db.Text, nullable=True)  # JSON string
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    citations = db.relationship('Citation', foreign_keys='Citation.citing_paper_id', backref='citing_paper', lazy=True)
    cited_by = db.relationship('Citation', foreign_keys='Citation.cited_paper_id', backref='cited_paper', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'venue': self.venue,
            'paper_type': self.paper_type,
            'arxiv_id': self.arxiv_id,
            'doi': self.doi,
            'pdf_url': self.pdf_url,
            'citation_count': self.citation_count,
            'research_areas': self.research_areas,
            'keywords': self.keywords,
            'lab_id': self.lab_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Researcher(db.Model):
    __tablename__ = 'researchers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    research_interests = db.Column(db.Text, nullable=True)  # JSON string
    google_scholar_id = db.Column(db.String(50), nullable=True)
    orcid_id = db.Column(db.String(50), nullable=True)
    homepage = db.Column(db.String(500), nullable=True)
    h_index = db.Column(db.Integer, nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'position': self.position,
            'research_interests': self.research_interests,
            'google_scholar_id': self.google_scholar_id,
            'orcid_id': self.orcid_id,
            'homepage': self.homepage,
            'h_index': self.h_index,
            'lab_id': self.lab_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Citation(db.Model):
    __tablename__ = 'citations'
    
    id = db.Column(db.Integer, primary_key=True)
    citing_paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    cited_paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('citing_paper_id', 'cited_paper_id'),)


class Trend(db.Model):
    __tablename__ = 'trends'
    
    id = db.Column(db.Integer, primary_key=True)
    research_area = db.Column(db.String(100), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    paper_count = db.Column(db.Integer, default=0)
    growth_rate = db.Column(db.Float, nullable=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    trend_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'research_area': self.research_area,
            'keyword': self.keyword,
            'paper_count': self.paper_count,
            'growth_rate': self.growth_rate,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'trend_score': self.trend_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }