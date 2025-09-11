#!/usr/bin/env python3

from app import create_app
from app.models import Lab

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