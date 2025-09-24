from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from app.services.paper_viewer_service import PaperViewerService
from pathlib import Path
import os

paper_viewer_bp = Blueprint('paper_viewer', __name__, template_folder='../templates')

# Initialize service
viewer_service = PaperViewerService()

@paper_viewer_bp.route('/', methods=['GET'])
def index():
    """Main page with search and filters"""
    return render_template('paper_viewer/index.html',
                         categories=viewer_service.parser.categories.keys() if viewer_service.parser else [],
                         tags=sorted(viewer_service.parser.tags) if viewer_service.parser else [],
                         stats=viewer_service.parser.stats if viewer_service.parser else {},
                         total_papers=len(viewer_service.parser.papers) if viewer_service.parser else 0)

@paper_viewer_bp.route('/api/search', methods=['GET'])
def search():
    """API endpoint for searching papers"""
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    tag = request.args.get('tag', '')

    if not viewer_service.parser:
        return jsonify({'error': 'No papers loaded'}), 404

    # Filter papers
    filtered_papers = viewer_service.parser.papers

    if category and category != 'all':
        filtered_papers = [p for p in filtered_papers if p.category == category]

    if tag and tag != 'all':
        filtered_papers = [p for p in filtered_papers if tag in p.tags]

    if query:
        filtered_papers = [
            p for p in filtered_papers
            if (query in p.title.lower() or
                query in p.summary.lower() or
                query in ' '.join(p.authors).lower() or
                any(query in contrib.lower() for contrib in p.contributions))
        ]

    # Convert to JSON-serializable format
    results = []
    for paper in filtered_papers[:50]:  # Limit to 50 results
        results.append({
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'venue': paper.venue,
            'year': paper.year,
            'category': paper.category,
            'summary': paper.summary[:200] + '...' if len(paper.summary) > 200 else paper.summary,
            'tags': paper.tags,
            'url': paper.url
        })

    return jsonify({
        'results': results,
        'total': len(filtered_papers),
        'showing': len(results)
    })

@paper_viewer_bp.route('/paper/<paper_id>', methods=['GET'])
def paper_detail(paper_id):
    """Display detailed paper information"""
    if not viewer_service.parser:
        flash('No papers loaded', 'error')
        return redirect(url_for('paper_viewer.index'))

    paper = next((p for p in viewer_service.parser.papers if p.id == paper_id), None)
    if not paper:
        flash('Paper not found', 'error')
        return redirect(url_for('paper_viewer.index'))

    return render_template('paper_viewer/paper_detail.html', paper=paper)

@paper_viewer_bp.route('/category/<category_name>', methods=['GET'])
def category_view(category_name):
    """View papers in a specific category"""
    if not viewer_service.parser or category_name not in viewer_service.parser.categories:
        flash('Category not found', 'error')
        return redirect(url_for('paper_viewer.index'))

    papers = viewer_service.parser.categories[category_name]
    return render_template('paper_viewer/category_view.html',
                         category=category_name,
                         papers=papers,
                         count=len(papers))

@paper_viewer_bp.route('/export', methods=['GET'])
def export_results():
    """Export filtered results as JSON"""
    from datetime import datetime

    if not viewer_service.parser:
        return jsonify({'error': 'No papers loaded'}), 404

    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    tag = request.args.get('tag', '')

    # Apply same filtering as search
    filtered_papers = viewer_service.parser.papers

    if category and category != 'all':
        filtered_papers = [p for p in filtered_papers if p.category == category]

    if tag and tag != 'all':
        filtered_papers = [p for p in filtered_papers if tag in p.tags]

    if query:
        filtered_papers = [
            p for p in filtered_papers
            if (query in p.title.lower() or
                query in p.summary.lower() or
                query in ' '.join(p.authors).lower())
        ]

    # Create export data
    export_data = {
        'metadata': {
            'total_papers': len(filtered_papers),
            'export_timestamp': str(datetime.now()),
            'filters': {
                'query': query,
                'category': category,
                'tag': tag
            }
        },
        'papers': [
            {
                'title': p.title,
                'authors': p.authors,
                'venue': p.venue,
                'year': p.year,
                'category': p.category,
                'summary': p.summary,
                'abstract': p.abstract,
                'contributions': p.contributions,
                'methods': p.methods,
                'applications': p.applications,
                'tags': p.tags,
                'code': p.code,
                'dataset': p.dataset,
                'url': p.url,
                'doi': p.doi
            }
            for p in filtered_papers
        ]
    }

    return jsonify(export_data)