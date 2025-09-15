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
    """Get all labs with optional filtering and hierarchical support"""
    try:
        # Get query parameters
        country = request.args.get('country')
        focus_area = request.args.get('focus_area')
        search = request.args.get('search')
        include_papers = request.args.get(
            'include_papers', 'false'
        ).lower() == 'true'
        include_sub_groups = request.args.get(
            'include_sub_groups', 'false'
        ).lower() == 'true'
        lab_type = request.args.get('type', None)  # independent/group/department
        
        # Build query
        query = Lab.query
        
        if lab_type:
            query = query.filter(Lab.lab_type == lab_type)
        
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
        return jsonify([
            lab.to_dict(
                include_papers=include_papers,
                include_sub_groups=include_sub_groups
            ) for lab in labs
        ])
        
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
            website=data.get('website'),
            description=data.get('description'),
            established_year=data.get('established_year')
        )
        
        # Set list properties using the property setters
        lab.focus_areas_list = data.get('focus_areas', [])
        lab.funding_sources_list = data.get('funding_sources', [])
        
        db.session.add(lab)
        db.session.commit()
        
        return jsonify(lab.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/<int:lab_id>', methods=['PUT'])
def update_lab(lab_id):
    """Update an existing lab"""
    try:
        lab = Lab.query.get_or_404(lab_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            lab.name = data['name']
        if 'pi' in data:
            lab.pi = data['pi']
        if 'institution' in data:
            lab.institution = data['institution']
        if 'city' in data:
            lab.city = data['city']
        if 'country' in data:
            lab.country = data['country']
        if 'focus_areas' in data:
            lab.focus_areas_list = data['focus_areas']
        if 'website' in data:
            lab.website = data['website']
        if 'latitude' in data:
            lab.latitude = data['latitude']
        if 'longitude' in data:
            lab.longitude = data['longitude']
        if 'established_year' in data:
            lab.established_year = data['established_year']
        if 'funding_sources' in data:
            lab.funding_sources_list = data['funding_sources']
        if 'description' in data:
            lab.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lab updated successfully',
            'lab': lab.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/<int:lab_id>', methods=['DELETE'])
def delete_lab(lab_id):
    """Delete a lab"""
    try:
        lab = Lab.query.get_or_404(lab_id)
        db.session.delete(lab)
        db.session.commit()
        
        return jsonify({'message': 'Lab deleted successfully'}), 200
        
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
                from flask import current_app
                scraper = LabPaperScraper(current_app)
                results = []
                for lab in labs:
                    try:
                        lab_results = await scraper.scrape_lab_papers(
                            lab, sources=sources, max_papers=max_papers
                        )
                        results.append({
                            'lab_id': lab.id,
                            'lab_name': lab.name,
                            'papers_found': lab_results,  # lab_results is already an int
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


@labs_bp.route('/scrape-institutional-papers', methods=['POST'])
def scrape_institutional_papers():
    """Scrape papers from institutions for unknown labs/authors"""
    try:
        data = request.get_json()
        institutions = data.get('institutions', [])
        max_papers = data.get('max_papers', 10)
        
        if not institutions:
            return jsonify({'error': 'No institutions provided'}), 400
        
        def run_institutional_scraping():
            """Run institutional scraping in background thread"""
            async def async_scrape():
                from flask import current_app
                scraper = LabPaperScraper(current_app)
                all_papers = []
                
                for institution in institutions:
                    try:
                        institutional_papers = await scraper.scrape_institutional_papers(
                            institution, max_papers=max_papers
                        )
                        all_papers.extend(institutional_papers)
                    except Exception as e:
                        print(f"Failed to scrape {institution}: {e}")
                        continue
                
                return all_papers
            
            return asyncio.run(async_scrape())
        
        # Run scraping in background thread
        papers = []
        
        def background_scrape():
            nonlocal papers
            papers = run_institutional_scraping()
        
        thread = threading.Thread(target=background_scrape)
        thread.start()
        thread.join(timeout=120)  # 2 minute timeout for institutional search
        
        if thread.is_alive():
            return jsonify({
                'message': 'Institutional scraping started in background',
                'status': 'running'
            }), 202
        
        return jsonify({
            'message': 'Institutional paper scraping completed',
            'papers': papers,
            'total_papers': len(papers),
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/<int:lab_id>/groups', methods=['GET'])
def get_lab_research_groups(lab_id):
    """Get all research groups within a lab"""
    try:
        lab = Lab.query.get_or_404(lab_id)
        groups = lab.sub_groups.all()
        
        return jsonify({
            'parent_lab': lab.to_dict(include_papers=True),
            'research_groups': [
                group.to_dict(include_papers=True) for group in groups
            ],
            'total_groups': len(groups)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/<int:lab_id>/groups', methods=['POST'])
def create_research_group(lab_id):
    """Create a new research group within a lab"""
    try:
        parent_lab = Lab.query.get_or_404(lab_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'pi']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create new research group
        group = Lab(
            name=data['name'],
            pi=data['pi'],
            institution=parent_lab.institution,
            city=parent_lab.city,
            country=parent_lab.country,
            latitude=parent_lab.latitude,
            longitude=parent_lab.longitude,
            website=data.get('website', ''),
            description=data.get('description', ''),
            parent_lab_id=lab_id,
            lab_type='group'
        )
        
        # Set focus areas and funding sources
        if 'focus_areas' in data:
            group.focus_areas_list = data['focus_areas']
        if 'funding_sources' in data:
            group.funding_sources_list = data['funding_sources']
        
        db.session.add(group)
        db.session.commit()
        
        return jsonify({
            'message': 'Research group created successfully',
            'group': group.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@labs_bp.route('/hierarchy', methods=['GET'])
def get_labs_hierarchy():
    """Get labs organized by hierarchy (departments -> groups)"""
    try:
        include_papers = request.args.get(
            'include_papers', 'false'
        ).lower() == 'true'
        
        # Get all independent labs and departments
        top_level_labs = Lab.query.filter(
            (Lab.lab_type == 'independent') | (Lab.lab_type == 'department')
        ).all()
        
        hierarchy = []
        
        for lab in top_level_labs:
            lab_data = lab.to_dict(
                include_papers=include_papers,
                include_sub_groups=True
            )
            
            if lab.lab_type == 'department':
                # Get research groups with their papers
                groups = lab.sub_groups.all()
                lab_data['research_groups'] = [
                    group.to_dict(include_papers=include_papers) 
                    for group in groups
                ]
                lab_data['total_groups'] = len(groups)
                lab_data['total_papers'] = sum(
                    len(group.papers) for group in groups
                )
            
            hierarchy.append(lab_data)
        
        return jsonify({
            'labs': hierarchy,
            'total_institutions': len(hierarchy),
            'total_groups': sum(
                len(lab.get('research_groups', [])) for lab in hierarchy
            )
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500