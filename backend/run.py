from app import create_app, db
from app.services.lab_importer import import_initial_data
import os

app = create_app()

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
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)