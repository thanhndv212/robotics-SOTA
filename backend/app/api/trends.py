from flask import Blueprint, request, jsonify
from app import db
from app.models import Trend, Paper
from sqlalchemy import func, desc
from datetime import datetime, timedelta

trends_bp = Blueprint('trends', __name__)


@trends_bp.route('/', methods=['GET'])
def get_trends():
    """Get research trends"""
    try:
        period = request.args.get('period', '1year')
        research_area = request.args.get('research_area')
        limit = request.args.get('limit', 50, type=int)
        
        query = Trend.query
        
        if research_area:
            query = query.filter(Trend.research_area == research_area)
        
        trends = query.order_by(desc(Trend.trend_score)).limit(limit).all()
        
        return jsonify([trend.to_dict() for trend in trends])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trends_bp.route('/emerging', methods=['GET'])
def get_emerging_trends():
    """Get emerging research trends"""
    try:
        # Look for keywords that have shown significant growth
        cutoff_date = datetime.now().date() - timedelta(days=365)
        
        # Query recent papers to identify trending keywords
        recent_papers = Paper.query.filter(
            Paper.publication_date >= cutoff_date
        ).all()
        
        keyword_counts = {}
        for paper in recent_papers:
            for keyword in paper.keywords or []:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency and return top trends
        emerging_trends = [
            {'keyword': keyword, 'paper_count': count}
            for keyword, count in sorted(keyword_counts.items(),
                                       key=lambda x: x[1], reverse=True)[:20]
        ]
        
        return jsonify(emerging_trends)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trends_bp.route('/research-areas', methods=['GET'])
def get_research_area_trends():
    """Get trends by research area"""
    try:
        # Get paper counts by research area over time
        area_trends = db.session.query(
            func.unnest(Paper.research_areas).label('area'),
            func.count(Paper.id).label('count'),
            func.date_trunc('quarter', Paper.publication_date).label('quarter')
        ).filter(
            Paper.research_areas.isnot(None),
            Paper.publication_date.isnot(None)
        ).group_by(
            func.unnest(Paper.research_areas),
            func.date_trunc('quarter', Paper.publication_date)
        ).order_by('quarter', desc('count')).all()
        
        # Format results
        trends_by_area = {}
        for result in area_trends:
            area = result.area
            if area not in trends_by_area:
                trends_by_area[area] = []
            
            trends_by_area[area].append({
                'quarter': result.quarter.isoformat() if result.quarter else None,
                'count': result.count
            })
        
        return jsonify(trends_by_area)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trends_bp.route('/geographic', methods=['GET'])
def get_geographic_trends():
    """Get research trends by geographic region"""
    try:
        # Get research output by country/region
        geographic_trends = db.session.query(
            func.count(Paper.id).label('paper_count'),
            func.avg(Paper.citation_count).label('avg_citations')
        ).join(
            Paper.lab
        ).group_by(
            Paper.lab.country
        ).all()
        
        return jsonify([
            {
                'country': result.country,
                'paper_count': result.paper_count,
                'avg_citations': float(result.avg_citations or 0)
            }
            for result in geographic_trends
        ])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trends_bp.route('/collaboration', methods=['GET'])
def get_collaboration_trends():
    """Get collaboration network trends"""
    try:
        # Analyze multi-author papers to identify collaboration patterns
        collaborations = db.session.query(
            Paper.authors,
            func.count(Paper.id).label('paper_count')
        ).filter(
            func.array_length(Paper.authors, 1) > 1
        ).group_by(
            Paper.authors
        ).order_by(
            desc('paper_count')
        ).limit(100).all()
        
        # Process collaboration data
        collaboration_data = []
        for result in collaborations:
            if result.authors and len(result.authors) > 1:
                collaboration_data.append({
                    'authors': result.authors,
                    'paper_count': result.paper_count,
                    'collaboration_size': len(result.authors)
                })
        
        return jsonify(collaboration_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500