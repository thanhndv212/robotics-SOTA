from flask import Blueprint, request, jsonify
from app import db
from app.models import Lab
from sqlalchemy import or_
import asyncio
import threading
from app.services.lab_paper_scraper import LabPaperScraper

labs_bp = Blueprint('labs', __name__)


@labs_bp.route('/', methods=['GET'])
def get_labs():
    """Get all labs with optional filtering"""
    try:
        # Get query parameters
        country = request.args.get('country')
        focus_area = request.args.get('focus_area')
        search = request.args.get('search')
        include_papers = request.args.get('include_papers', 'false').lower() == 'true'
        
        # Build query
        query = Lab.query
        
        if country:
            query = query.filter(Lab.country == country)
            
        if focus_area:
            query = query.filter(Lab.focus_areas.any(focus_area))
            
        if search:
            query = query.filter(
                or_(
                    Lab.name.ilike(f'%{search}%'),
                    Lab.institution.ilike(f'%{search}%'),
                    Lab.pi.ilike(f'%{search}%')
                )
            )
        
        labs = query.all()
        return jsonify([lab.to_dict(include_papers=include_papers) for lab in labs])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/<int:lab_id>', methods=['GET'])
def get_lab(lab_id):
    """Get a specific lab by ID"""
    try:
        include_papers = request.args.get('include_papers', 'true').lower() == 'true'
        lab = Lab.query.get_or_404(lab_id)
        return jsonify(lab.to_dict(include_papers=include_papers))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/', methods=['POST'])
def create_lab():
    """Create a new lab"""
    try:
        data = request.get_json()
        
        lab = Lab(
            name=data.get('name'),
            pi=data.get('pi'),
            institution=data.get('institution'),
            city=data.get('city'),
            country=data.get('country'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            focus_areas=data.get('focus_areas', []),
            website=data.get('website'),
            description=data.get('description'),
            established_year=data.get('established_year'),
            funding_sources=data.get('funding_sources', [])
        )
        
        db.session.add(lab)
        db.session.commit()
        
        return jsonify(lab.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/stats', methods=['GET'])
def get_lab_stats():
    """Get lab statistics"""
    try:
        stats = {
            'total_labs': Lab.query.count(),
            'countries': Lab.query.with_entities(Lab.country).distinct().count(),
            'focus_areas': []
        }
        
        # Get focus area distribution
        labs_with_areas = Lab.query.filter(Lab.focus_areas.isnot(None)).all()
        area_counts = {}
        
        for lab in labs_with_areas:
            for area in lab.focus_areas or []:
                area_counts[area] = area_counts.get(area, 0) + 1
        
        stats['focus_areas'] = [
            {'area': area, 'count': count}
            for area, count in sorted(area_counts.items(), 
                                    key=lambda x: x[1], reverse=True)
        ]
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/geographic', methods=['GET'])
def get_geographic_data():
    """Get lab data formatted for geographic visualization"""
    try:
        labs = Lab.query.filter(
            Lab.latitude.isnot(None),
            Lab.longitude.isnot(None)
        ).all()
        
        geographic_data = []
        for lab in labs:
            geographic_data.append({
                'id': lab.id,
                'name': lab.name,
                'latitude': lab.latitude,
                'longitude': lab.longitude,
                'city': lab.city,
                'country': lab.country,
                'institution': lab.institution,
                'focus_areas': lab.focus_areas,
                'paper_count': len(lab.papers) if lab.papers else 0
            })
        
        return jsonify(geographic_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/scrape-papers', methods=['POST'])
def scrape_papers():
    """Trigger paper scraping for specified labs"""
    try:
        data = request.get_json()
        lab_ids = data.get('lab_ids', [])
        sources = data.get('sources', ['arxiv'])  # arxiv, scholar, website
        max_papers = data.get('max_papers', 5)
        
        if not lab_ids:
            return jsonify({'error': 'No lab IDs provided'}), 400
        
        # Get labs
        labs = Lab.query.filter(Lab.id.in_(lab_ids)).all()
        if not labs:
            return jsonify({'error': 'No valid labs found'}), 404
        
        def run_scraping():
            """Run scraping in background thread"""
            async def async_scrape():
                scraper = LabPaperScraper()
                results = []
                for lab in labs:
                    try:
                        lab_results = await scraper.scrape_lab_papers(
                            lab, sources=sources, max_papers=max_papers
                        )
                        results.append({
                            'lab_id': lab.id,
                            'lab_name': lab.name,
                            'papers_found': len(lab_results),
                            'success': True
                        })
                    except Exception as e:
                        results.append({
                            'lab_id': lab.id,
                            'lab_name': lab.name,
                            'error': str(e),
                            'success': False
                        })
                return results
            
            return asyncio.run(async_scrape())
        
        # Run scraping in background thread
        results = []
        
        def background_scrape():
            nonlocal results
            results = run_scraping()
        
        thread = threading.Thread(target=background_scrape)
        thread.start()
        thread.join(timeout=60)  # 60 second timeout
        
        if thread.is_alive():
            return jsonify({
                'message': 'Scraping started in background',
                'status': 'running'
            }), 202
        
        return jsonify({
            'message': 'Paper scraping completed',
            'results': results,
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500