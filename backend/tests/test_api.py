#!/usr/bin/env python3

import json
import sys
from datetime import date
from pathlib import Path
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app, db  # noqa: E402
from app.models import Lab, Paper  # noqa: E402


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    with app.test_client() as client:
        yield client


@pytest.fixture
def seeded_data(app: Flask) -> None:
    with app.app_context():
        robotics_lab = Lab(
            name="Dexterity Lab",
            pi="Dr. Ada Robot",
            institution="Tech Institute",
            city="Innovation City",
            country="United States",
            lab_type="independent",
        )
        robotics_lab.focus_areas_list = ["Manipulation", "Planning"]

        perception_lab = Lab(
            name="Perception Lab",
            pi="Dr. Vision",
            institution="Vision University",
            city="Optic Town",
            country="France",
            lab_type="group",
        )
        perception_lab.focus_areas_list = ["Perception"]

        db.session.add_all([robotics_lab, perception_lab])
        db.session.flush()

        paper = Paper(
            title="Learning Dexterous Manipulation",
            authors=json.dumps(["Ada Robot"]),
            venue="ICRA",
            publication_date=date.today(),
            research_areas=json.dumps(["Manipulation"]),
            lab_id=robotics_lab.id,
        )
        db.session.add(paper)
        db.session.commit()


def test_get_labs(client: FlaskClient, seeded_data) -> None:
    response = client.get("/api/labs/?per_page=10")
    assert response.status_code == 200

    payload = response.get_json()
    assert isinstance(payload, dict)
    assert "labs" in payload
    assert payload["pagination"]["total"] == 2
    assert {lab["name"] for lab in payload["labs"]} == {
        "Dexterity Lab",
        "Perception Lab",
    }


def test_get_labs_focus_filter(client: FlaskClient, seeded_data) -> None:
    response = client.get("/api/labs/?focus_area=perception")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["pagination"]["total"] == 1
    assert payload["labs"][0]["name"] == "Perception Lab"


def test_get_labs_summary(client: FlaskClient, seeded_data) -> None:
    response = client.get("/api/labs/summary")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["total"] == 2
    assert payload["focus"]["top"]
    assert payload["focus"]["diversity_index"] >= 0.0
    assert payload["recent_activity"]["updated_last_30_days"] >= 1


def test_get_papers(client: FlaskClient, seeded_data) -> None:
    response = client.get('/api/papers/')
    assert response.status_code == 200
    payload = response.get_json()
    assert "papers" in payload
    assert payload["total"] >= 1


def test_import_papers(client: FlaskClient) -> None:
    data = {
        'file': (open('tests/sample_import.csv', 'rb'), 'sample_import.csv')
    }
    response = client.post(
        '/api/papers/import', data=data, content_type='multipart/form-data'
    )
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_get_trends(client: FlaskClient) -> None:
    response = client.get('/api/trends/')
    assert response.status_code == 200
    assert isinstance(response.get_json(), dict)


def test_get_statistics(client: FlaskClient, seeded_data) -> None:
    response = client.get('/api/statistics/')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total_labs"] >= 2


def test_get_analytics_overview(client: FlaskClient, seeded_data) -> None:
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["meta"]["lab_count"] == 2
    assert payload["papers"]["total"] >= 1
    assert payload["focus_areas"]["top"]


def test_get_papers_analytics(client: FlaskClient, seeded_data) -> None:
    response = client.get("/api/analytics/papers")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] >= 1
    assert payload["top_research_areas"]


def test_labs_snapshot(app: Flask, seeded_data) -> None:
    with app.app_context():
        labs = Lab.query.order_by(Lab.name).all()
        assert len(labs) == 2


if __name__ == "__main__":
    pytest.main([__file__])
