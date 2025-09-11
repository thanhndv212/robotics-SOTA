# Robotics SOTA - Interactive Research Trends Mapping System

A comprehensive full-stack system for mapping and analyzing global robotics research trends with interactive geographic visualization, automated paper tracking, and AI-powered trend analysis.

## 🚀 Features

- **Interactive Geographic Map**: Visualize 47+ robotics labs worldwide with Mapbox integration
- **Real-time Database**: SQLite/PostgreSQL with comprehensive lab, paper, and researcher data
- **REST API**: Complete backend API for labs, papers, trends, and statistics
- **Advanced Search**: Multi-dimensional filtering by location, research focus, and institution
- **Research Analytics**: Track research areas including robot learning, manipulation, perception
- **Citation Networks**: Analyze collaboration patterns and geographic research clusters

## 🏗️ Architecture

```
robotics-SOTA/
├── backend/          # Python Flask backend (✅ Complete)
│   ├── app/
│   │   ├── models/   # SQLAlchemy database models
│   │   ├── api/      # REST API endpoints
│   │   ├── services/ # Lab data import, paper tracking
│   │   └── __init__.py # Flask app factory
│   ├── run_dev.py    # Development server
│   └── requirements.txt
├── frontend/         # React + TypeScript frontend (✅ Structure Ready)
│   ├── src/
│   │   ├── components/ # Interactive map, lab details
│   │   ├── services/   # API integration
│   │   └── App.tsx     # Main application
│   └── package.json
├── data/            # Lab directory CSV (47 labs imported)
├── scripts/         # Database setup and import tools
├── docs/           # API documentation
└── tests/          # Unit tests
```

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Ant Design, Mapbox GL JS, D3.js
- **Backend**: Python 3.12, Flask, SQLAlchemy, SQLite (dev) / PostgreSQL (prod)
- **Data Processing**: pandas, JSON storage, geocoding APIs
- **Development**: VS Code, conda environment, GitHub
- **Deployment**: Docker ready, Railway/Heroku compatible

## 📊 Current Database

**47 Leading Robotics Research Labs** including:
- **US West**: UC Berkeley (3 labs), Stanford IRIS, Caltech
- **US East**: MIT (2 labs), CMU Robotics Institute, Harvard  
- **Europe**: Oxford, Cambridge, Imperial College, EPFL, ETH Zurich, Max Planck
- **Asia**: University of Tokyo (3 labs), Tsinghua, KAIST, NTU Singapore
- **Global Coverage**: 12+ countries across North America, Europe, and Asia

**Research Focus Areas**: Deep RL, manipulation, perception, sim2real, human-robot interaction, legged locomotion, autonomous systems, industrial robotics

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (conda recommended)
- **Node.js 16+** and npm
- **Git**

### Option 1: One-Command Setup 🎯
```bash
git clone <repository-url>
cd robotics-SOTA
./start-dev.sh  # Starts both backend and frontend
```

### Option 2: Manual Setup

1. **Clone and Setup Backend**
```bash
git clone <repository-url>
cd robotics-SOTA

# Backend setup
cd backend
pip install -r requirements.txt
python ../scripts/setup_database.py  # Imports 47 labs
```

2. **Start Backend Server**
```bash
cd backend
python -c "
import sys, os
sys.path.insert(0, '.')
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
app.run(host='127.0.0.1', port=8080, debug=True)
"
```

3. **Setup Frontend** (requires Node.js)
```bash
cd frontend
npm install          # Install React dependencies
npm start           # Start development server
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8080
- **Lab Data**: http://127.0.0.1:8080/api/labs

## 📡 API Endpoints

### Labs
- `GET /api/labs` - List all robotics labs
- `GET /api/labs?limit=10&country=USA` - Filtered labs
- `GET /api/labs/{id}` - Specific lab details

### Papers (Coming Soon)
- `GET /api/papers` - Research papers
- `GET /api/papers?lab_id=1&year=2024` - Filtered papers

### Trends (Coming Soon)  
- `GET /api/trends` - Research trend analysis
- `GET /api/trends?timeframe=2024` - Temporal trends

### Statistics
- `GET /api/labs/stats` - Lab distribution statistics
- `GET /api/papers/stats` - Publication metrics

## 🗺️ Map Features

- **Geographic Visualization**: Interactive world map with lab locations
- **Lab Markers**: Click markers to view lab details, PI, research focus
- **Country Clustering**: Visual grouping by research density
- **Search & Filter**: Real-time filtering by name, country, research area
- **Statistics Panel**: Live counts of labs, countries, research areas

## 🧪 Development Status

| Component | Status | Description |
|-----------|--------|-------------|
| **Backend API** | ✅ Complete | Flask server with SQLite, 47 labs imported |
| **Database Models** | ✅ Complete | Lab, Paper, Researcher, Citation entities |
| **Frontend Structure** | ✅ Ready | React components, API integration setup |
| **Interactive Map** | 🔄 In Progress | Mapbox integration (needs API key) |
| **Paper Tracking** | 📋 Planned | arXiv, Google Scholar automation |
| **Trend Analysis** | 📋 Planned | NLP-powered research trend detection |

## 🛠️ Configuration

### Environment Variables
Create `.env` files:

**Backend (.env)**:
```
DATABASE_URL=sqlite:///robotics_sota.db
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

**Frontend (.env)**:
```
REACT_APP_API_URL=http://127.0.0.1:8080/api
REACT_APP_MAPBOX_TOKEN=your-mapbox-token  # Required for maps
```

### Mapbox Setup
1. Sign up at [Mapbox](https://mapbox.com)
2. Get your access token
3. Add to frontend `.env` file
4. Restart frontend: `npm start`

## 📁 Project Structure Details

```
├── backend/
│   ├── app/
│   │   ├── __init__.py      # Flask app factory, SQLite config
│   │   ├── models/
│   │   │   └── __init__.py  # Lab, Paper, Researcher models
│   │   ├── api/
│   │   │   ├── labs.py      # Lab endpoints with filtering
│   │   │   ├── papers.py    # Paper endpoints (ready)
│   │   │   └── trends.py    # Trend analysis endpoints
│   │   └── services/
│   │       ├── lab_importer.py     # CSV import with geocoding
│   │       ├── paper_tracker.py   # arXiv integration (planned)
│   │       └── nlp_processor.py   # Trend analysis (planned)
│   ├── run_dev.py           # Development server launcher
│   └── robotics_sota.db    # SQLite database (47 labs)
├── frontend/src/
│   ├── components/
│   │   └── InteractiveMap.tsx  # Mapbox map component
│   ├── services/
│   │   └── api.ts           # Backend API integration
│   └── App.tsx              # Main application UI
├── data/
│   └── robot_learning_labs_directory.csv  # Source data (50 labs)
├── scripts/
│   └── setup_database.py   # Database initialization
└── start-dev.sh            # One-command development launcher
```

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Docker (optional)

### Development Setup

1. **Clone and setup backend**:
```bash
cd backend
pip install -r requirements.txt
python run.py
```

2. **Setup frontend**:
```bash
cd frontend
npm install
npm start
```

3. **Import initial data**:
```bash
python scripts/import_labs.py data/robot_learning_labs_directory.csv
```

## 📈 Usage

1. **Browse Labs**: Interactive map with lab information and research focus
2. **Search Papers**: Real-time search across tracked publications
3. **Analyze Trends**: View emerging research directions and hot topics
4. **Track Citations**: Monitor paper impact and citation networks
5. **Export Data**: Download filtered results in various formats

## 🧪 Development

### Running Tests
```bash
pytest tests/
npm test  # Frontend tests
```

### API Documentation
- Backend API: `http://localhost:5000/docs`
- Frontend: `http://localhost:3000`

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- Robotics research community for open data sharing
- arXiv for providing open access to research papers
- Mapbox for geographic visualization capabilities

---

**Status**: 🚧 Under Development | **Version**: 1.0.0-alpha