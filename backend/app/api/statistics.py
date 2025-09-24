from flask import Blueprint, jsonify
from app.models import Paper, Lab

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/", methods=["GET"])
def get_statistics():
    """Get general statistics about the database"""
    try:
        total_papers = Paper.query.count()
        total_labs = Lab.query.count()

        return jsonify(
            {"total_papers": total_papers, "total_labs": total_labs}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
