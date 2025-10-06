from flask import Blueprint, current_app, jsonify

from app.models import Lab, Paper
from app.services.analytics import (
    build_dashboard_overview,
    build_lab_summary_payload,
    summarize_papers,
)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/overview", methods=["GET"])
def get_analytics_overview():
    """Return combined lab and paper analytics for dashboards."""

    try:
        labs = Lab.query.all()
        papers = Paper.query.all()
        overview = build_dashboard_overview(labs, papers)
        return jsonify(overview)

    except Exception as exc:
        current_app.logger.exception("Failed to build analytics overview")
        return jsonify({"error": str(exc)}), 500


@analytics_bp.route("/labs", methods=["GET"])
def get_labs_analytics():
    """Return analytics summary focused on labs."""

    try:
        labs = Lab.query.all()
        payload = build_lab_summary_payload(labs)
        return jsonify(payload)

    except Exception as exc:
        current_app.logger.exception("Failed to build labs analytics")
        return jsonify({"error": str(exc)}), 500


@analytics_bp.route("/papers", methods=["GET"])
def get_papers_analytics():
    """Return analytics summary focused on papers."""

    try:
        papers = Paper.query.all()
        summary = summarize_papers(papers)
        return jsonify(summary)

    except Exception as exc:
        current_app.logger.exception("Failed to build papers analytics")
        return jsonify({"error": str(exc)}), 500
