from flask import Blueprint, request, jsonify
from app import db
from app.models import Paper, Lab
from sqlalchemy import or_, desc, func
from datetime import datetime, timedelta
import json

papers_bp = Blueprint('papers', __name__)


@papers_bp.route('/', methods=['GET'])
def get_papers():
    """Get papers with optional filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search')
        research_area = request.args.get('research_area')
        lab_id = request.args.get('lab_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        sort_by = request.args.get('sort_by', 'publication_date')
        
        # Build query
        query = Paper.query
        
        if search:
            query = query.filter(
                or_(
                    Paper.title.ilike(f'%{search}%'),
                    Paper.abstract.ilike(f'%{search}%'),
                    Paper.authors.ilike(f'%{search}%')
                )
            )
            
        if research_area:
            query = query.filter(Paper.research_areas.ilike(f'%{research_area}%'))
            
        if lab_id:
            query = query.filter(Paper.lab_id == lab_id)
            
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Paper.publication_date >= start)
            
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Paper.publication_date <= end)
        
        # Apply sorting
        if sort_by == 'citation_count':
            query = query.order_by(desc(Paper.citation_count))
        elif sort_by == 'title':
            query = query.order_by(Paper.title)
        else:
            query = query.order_by(desc(Paper.publication_date))
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        papers = [paper.to_dict() for paper in pagination.items]
        
        return jsonify({
            'papers': papers,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@papers_bp.route('/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    """Get a specific paper by ID"""
    try:
        paper = Paper.query.get_or_404(paper_id)
        return jsonify(paper.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@papers_bp.route('/recent', methods=['GET'])
def get_recent_papers():
    """Get recently published papers"""
    try:
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        papers = Paper.query.filter(
            Paper.publication_date >= cutoff_date
        ).order_by(
            desc(Paper.publication_date)
        ).limit(limit).all()
        
        return jsonify([paper.to_dict() for paper in papers])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@papers_bp.route('/trending', methods=['GET'])
def get_trending_papers():
    """Get trending papers based on recent citations"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # For now, sort by citation count
        # TODO: Implement more sophisticated trending algorithm
        papers = Paper.query.order_by(
            desc(Paper.citation_count)
        ).limit(limit).all()
        
        return jsonify([paper.to_dict() for paper in papers])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@papers_bp.route('/stats', methods=['GET'])
def get_paper_stats():
    """Get paper statistics"""
    try:
        stats = {
            'total_papers': Paper.query.count(),
            'total_citations': db.session.query(
                func.sum(Paper.citation_count)
            ).scalar() or 0,
            'research_areas': [],
            'publication_timeline': []
        }
        
        # Get research area distribution
        papers_with_areas = Paper.query.filter(
            Paper.research_areas.isnot(None)
        ).all()
        
        area_counts = {}
        for paper in papers_with_areas:
            for area in paper.research_areas or []:
                area_counts[area] = area_counts.get(area, 0) + 1
        
        stats['research_areas'] = [
            {'area': area, 'count': count}
            for area, count in sorted(area_counts.items(),
                                    key=lambda x: x[1], reverse=True)[:20]
        ]
        
        # Get publication timeline
        timeline_query = db.session.query(
            func.date_trunc('month', Paper.publication_date).label('month'),
            func.count(Paper.id).label('count')
        ).filter(
            Paper.publication_date.isnot(None)
        ).group_by(
            func.date_trunc('month', Paper.publication_date)
        ).order_by('month').all()
        
        stats['publication_timeline'] = [
            {
                'month': result.month.isoformat() if result.month else None,
                'count': result.count
            }
            for result in timeline_query
        ]
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@papers_bp.route('/', methods=['POST'])
def create_paper():
    """Create a new paper"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'authors', 'lab_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate lab exists
        lab = Lab.query.get(data['lab_id'])
        if not lab:
            return jsonify({'error': 'Lab not found'}), 404
        
        # Convert authors to JSON string if it's a list
        authors = data['authors']
        if isinstance(authors, list):
            authors = json.dumps(authors)
        
        # Convert research_areas to JSON string if it's a list
        research_areas = data.get('research_areas', [])
        if isinstance(research_areas, list):
            research_areas = json.dumps(research_areas)
        
        # Convert keywords to JSON string if it's a list
        keywords = data.get('keywords', [])
        if isinstance(keywords, list):
            keywords = json.dumps(keywords)
        
        # Parse publication date if provided
        publication_date = None
        if data.get('publication_date'):
            try:
                publication_date = datetime.strptime(data['publication_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid publication_date format. Use YYYY-MM-DD'}), 400
        
        paper = Paper(
            title=data['title'].strip(),
            authors=authors,
            abstract=data.get('abstract', '').strip(),
            publication_date=publication_date,
            venue=data.get('venue', '').strip(),
            paper_type=data.get('paper_type', 'journal'),
            arxiv_id=data.get('arxiv_id', '').strip(),
            doi=data.get('doi', '').strip(),
            pdf_url=data.get('pdf_url', '').strip(),
            website_url=data.get('website_url', '').strip(),
            citation_count=data.get('citation_count', 0),
            research_areas=research_areas,
            keywords=keywords,
            lab_id=data['lab_id']
        )
        
        db.session.add(paper)
        db.session.commit()
        
        return jsonify({
            'message': 'Paper created successfully',
            'paper': paper.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@papers_bp.route('/<int:paper_id>', methods=['PUT'])
def update_paper(paper_id):
    """Update an existing paper"""
    try:
        paper = Paper.query.get_or_404(paper_id)
        data = request.get_json()
        
        # Validate lab exists if lab_id is being updated
        if 'lab_id' in data:
            lab = Lab.query.get(data['lab_id'])
            if not lab:
                return jsonify({'error': 'Lab not found'}), 404
        
        # Update fields if provided
        if 'title' in data:
            paper.title = data['title'].strip()
        
        if 'authors' in data:
            authors = data['authors']
            if isinstance(authors, list):
                authors = json.dumps(authors)
            paper.authors = authors
        
        if 'abstract' in data:
            paper.abstract = data['abstract'].strip()
        
        if 'publication_date' in data:
            if data['publication_date']:
                try:
                    paper.publication_date = datetime.strptime(data['publication_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid publication_date format. Use YYYY-MM-DD'}), 400
            else:
                paper.publication_date = None
        
        if 'venue' in data:
            paper.venue = data['venue'].strip()
        
        if 'paper_type' in data:
            paper.paper_type = data['paper_type']
        
        if 'arxiv_id' in data:
            paper.arxiv_id = data['arxiv_id'].strip()
        
        if 'doi' in data:
            paper.doi = data['doi'].strip()
        
        if 'pdf_url' in data:
            paper.pdf_url = data['pdf_url'].strip()
        
        if 'website_url' in data:
            paper.website_url = data['website_url'].strip()
        
        if 'citation_count' in data:
            paper.citation_count = data['citation_count']
        
        if 'research_areas' in data:
            research_areas = data['research_areas']
            if isinstance(research_areas, list):
                research_areas = json.dumps(research_areas)
            paper.research_areas = research_areas
        
        if 'keywords' in data:
            keywords = data['keywords']
            if isinstance(keywords, list):
                keywords = json.dumps(keywords)
            paper.keywords = keywords
        
        if 'lab_id' in data:
            paper.lab_id = data['lab_id']
        
        paper.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Paper updated successfully',
            'paper': paper.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@papers_bp.route('/<int:paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    """Delete a paper"""
    try:
        paper = Paper.query.get_or_404(paper_id)
        
        # Store paper info for response
        paper_title = paper.title
        lab_name = paper.lab.name if paper.lab else 'Unknown'
        
        db.session.delete(paper)
        db.session.commit()
        
        return jsonify({
            'message': f'Paper "{paper_title}" deleted successfully',
            'deleted_paper': {
                'id': paper_id,
                'title': paper_title,
                'lab': lab_name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500