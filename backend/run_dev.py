from app import create_app, db
from app.services.lab_importer import import_initial_data
import os

# Use SQLite for development
import tempfile

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///robotics_sota.db'

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")

@app.cli.command()
def import_labs():
    """Import lab data from CSV"""
    result = import_initial_data()
    if result:
        print(f"Successfully imported {result['imported']} labs")
    else:
        print("Failed to import lab data")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized with SQLite!")
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)