#!/usr/bin/env python3

from backend.app import create_app
from backend.app.models import Lab
import pytest
from flask import Flask
from flask.testing import FlaskClient
from typing import Generator


@pytest.fixture
def client() -> "Generator[FlaskClient, None, None]":
    app: Flask = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_labs(client: FlaskClient):
    response = client.get('/api/labs/')
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_papers(client: FlaskClient):
    response = client.get('/api/papers/')
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert 'papers' in response.json
    assert isinstance(response.json['papers'], list)


def test_import_papers(client: FlaskClient):
    data = {
        'file': (open('tests/sample_import.csv', 'rb'), 'sample_import.csv')
    }
    response = client.post(
        '/api/papers/import', data=data, content_type='multipart/form-data'
    )
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == 'Papers imported successfully'


def test_get_trends(client: FlaskClient):
    response = client.get('/api/trends/')
    assert response.status_code == 200
    assert isinstance(response.json, dict)


def test_get_statistics(client: FlaskClient):
    response = client.get('/api/statistics/')
    assert response.status_code == 200
    assert isinstance(response.json, dict)


def test_labs():
    app = create_app()
    with app.app_context():
        labs = Lab.query.limit(5).all()
        print("\nFirst 5 labs from API:")
        print("=" * 80)
        for lab in labs:
            print(f"• {lab.name}")
            print(f"  PI: {lab.pi}")
            print(f"  Institution: {lab.institution}")
            print(f"  Location: {lab.city}, {lab.country}")
            print(f"  Focus: {lab.focus_areas}")
            print()

        total = Lab.query.count()
        print(f"Total labs in database: {total}")


if __name__ == "__main__":
    test_labs()