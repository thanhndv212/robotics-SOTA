# Robotics SOTA - Interactive Research Trends Mapping System

A comprehensive full-stack system for mapping and analyzing global robotics research trends with real-time data visualization, automated paper tracking, and research analytics.

## 🚀 Features

- **Modern Web Dashboard**: Next.js 14 + Tailwind CSS with server-side rendering
- **171 Global Labs**: Comprehensive directory of robotics research labs worldwide
- **Real-time Database**: SQLite with 171 labs across 24 countries, ready for paper tracking
- **REST API**: Complete Flask backend API for labs, papers, trends, and statistics
- **Advanced Search & Filtering**: Multi-dimensional filtering by location, research focus, and institution
- **Research Analytics**: Track research areas including robot learning, manipulation, perception, sim2real
- **Responsive UI**: Clean, modern interface with lab cards, metrics, and detailed views
- **Geographic Coverage**: Labs from USA (60), South Korea (26), Canada (10), China, Japan, UK, and 18+ more countries

## 🏗️ Architecture

```
robotics-SOTA/
├── backend/          # Python Flask backend (✅ Complete & Running)
│   ├── app/
│   │   ├── models/   # SQLAlchemy database models (Lab, Paper, Researcher)
│   │   ├── api/      # REST API endpoints (labs, papers, trends, statistics)
│   │   ├── services/ # Lab importer, paper scraper, analytics
│   │   └── __init__.py # Flask app factory with CORS
│   ├── instance/
│   │   └── robotics_sota.db # SQLite database (171 labs)
│   ├── run_dev.py    # Development server with auto-import
│   └── requirements.txt
├── frontend/         # Next.js 14 + Tailwind CSS (✅ Complete & Production Ready)
│   ├── app/
│   │   ├── layout.tsx    # Root layout with metadata
│   │   ├── page.tsx      # Home page
│   │   └── globals.css   # Global Tailwind styles
│   ├── components/
│   │   └── dashboard/    # Lab dashboard components
│   │       ├── LabsDashboard.tsx  # Main orchestrator
│   │       ├── MetricsSummary.tsx # Statistics cards
│   │       ├── LabFilters.tsx     # Search & filters
│   │       ├── LabList.tsx        # Grid container
│   │       └── LabCard.tsx        # Individual lab display
│   ├── lib/
│   │   └── api.ts        # Backend API client
│   ├── types/
│   │   └── lab.ts        # TypeScript interfaces
│   ├── next.config.mjs   # Next.js configuration
│   ├── tailwind.config.ts # Tailwind configuration
│   └── package.json
├── data/            # Lab directory CSV (178 labs source data)
│   └── robot_learning_labs_directory.csv
├── scripts/         # Database setup tools
├── docs/           # API documentation
├── start-dev.sh    # One-command development launcher
└── tests/          # Unit tests
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14.2.33 (App Router, React 18.2)
- **Language**: TypeScript 5.4.5
- **Styling**: Tailwind CSS 3.4.4 (utility-first CSS)
- **HTTP Client**: Axios 1.7.9
- **Build**: SWC compiler, automatic code splitting
- **Rendering**: SSR/SSG/ISR support, edge deployment ready

### Backend
- **Language**: Python 3.12+
- **Framework**: Flask with CORS support
- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod ready)
- **Data Processing**: pandas for CSV import, JSON serialization
- **API**: RESTful endpoints with query parameter filtering

### Development
- **Environment**: conda/venv for Python, npm for Node.js
- **Tools**: VS Code, ESLint, Git
- **Scripts**: Automated development launcher (`start-dev.sh`)
- **Deployment**: Docker ready, Railway/Vercel/Heroku compatible

## 📊 Current Database

**171 Leading Robotics Research Labs** including:

### Geographic Distribution (24 Countries)
- **USA**: 60 labs (35%) - UC Berkeley, Stanford, MIT, CMU, and more
- **South Korea**: 26 labs (15%) - KAIST, Seoul National University, GIST
- **Canada**: 10 labs (6%) - University of Toronto, McGill, UBC, Vector Institute
- **China**: 8 labs - Tsinghua, Peking University, Shanghai Jiao Tong
- **Japan**: 8 labs - University of Tokyo, RIKEN, Waseda, Osaka University
- **UK**: 8 labs - Oxford, Cambridge, Imperial College, Edinburgh
- **Germany**: 7 labs - TUM, RWTH Aachen, Max Planck, Karlsruhe
- **India**: 6 labs - IIT Bombay, IIT Delhi, IIT Madras, IISc
- **France**: 5 labs - INRIA, LAAS-CNRS, Sorbonne
- **Switzerland**: 5 labs - EPFL, ETH Zurich, University of Zurich
- **Plus 14 more countries**: Australia, Singapore, Israel, Netherlands, Italy, and more

### Top Research Focus Areas
1. **Perception** - 10 labs
2. **Manipulation** - 8 labs  
3. **Sim2real** - 7 labs
4. **Human-Robot Interaction** - 5 labs
5. **Embodied AI** - 4 labs
6. **Robot Learning, Grasping, Autonomous Systems** - Multiple labs each

### Notable Labs Include
- **Berkeley Robot Learning Lab (RLL)** - Pieter Abbeel
- **Levine Lab / Robot Learning** - Sergey Levine, UC Berkeley
- **Stanford IRIS** - Chelsea Finn, Stanford
- **MIT Robot Locomotion & Learning** - Russ Tedrake
- **RobIn Lab** - Roberto Martín-Martín, UT Austin
- **CMU Robotics Institute** - Multiple research groups
- **And 165+ more world-leading robotics labs**

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** (conda recommended for environment management)
- **Node.js 18+** and npm
- **Git**

### Option 1: One-Command Setup 🎯 (Recommended)
```bash
git clone https://github.com/thanhndv212/robotics-SOTA.git
cd robotics-SOTA
bash start-dev.sh  # Starts both backend and frontend automatically
```

This script will:
1. ✅ Check Python and Node.js prerequisites
2. 🐍 Start Flask backend on port 8080
3. 📥 Auto-import 171 labs from CSV (first run only)
4. ⚛️ Start Next.js frontend on port 3000
5. 🎉 Open your browser to http://localhost:3000

### Option 2: Manual Setup

**1. Clone Repository**
```bash
git clone https://github.com/thanhndv212/robotics-SOTA.git
cd robotics-SOTA
```

**2. Setup and Start Backend**
```bash
cd backend
pip install -r requirements.txt
python run_dev.py  # Starts on http://127.0.0.1:8080
```

**3. Setup and Start Frontend** (new terminal)
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

### Access the Application
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8080
- **Labs API Endpoint**: http://127.0.0.1:8080/api/labs
- **Statistics**: http://127.0.0.1:8080/api/labs/stats

### Production Build
```bash
# Frontend production build
cd frontend
npm run build
npm start

# Backend production (use gunicorn)
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 'app:create_app()'
```

## 🎛️ User Interface Features

### Dashboard Overview
- **Metrics Summary**: Live statistics showing total labs, countries, papers, and active labs
- **Search & Filters**: Real-time filtering by search term, country, and research focus area
- **Lab Cards**: Responsive grid layout with lab information, PI, location, and focus areas
- **Recent Papers**: Display of latest publications with PDF/ArXiv/DOI links (when available)
- **Responsive Design**: Optimized for desktop, tablet, and mobile viewing

### Features
- **Smart Search**: Filter labs by name, PI, institution, or city
- **Country Filter**: Dropdown with 24 countries to choose from
- **Focus Area Filter**: Filter by specific research areas (manipulation, perception, etc.)
- **Reset Filters**: Quick reset button to clear all filters
- **Real-time Updates**: Instant filtering as you type or select options
- **Paper Tracking**: Ready for integration with ArXiv and Google Scholar APIs

### Coming Soon
- Paper scraping from ArXiv and lab websites
- Research trend analysis and visualization
- Citation network graphs
- Collaboration pattern analysis

## 📡 API Endpoints

### Labs
- `GET /api/labs` - List all robotics labs (171 total)
  - Query params: `?include_papers=true&include_sub_groups=true`
  - Returns: Array of lab objects with full details
- `GET /api/labs?country=USA` - Filter labs by country
- `GET /api/labs?focus_area=manipulation` - Filter by research focus
- `GET /api/labs/{id}` - Get specific lab details by ID
- `GET /api/labs/stats` - Get lab distribution statistics
  - Total labs, countries, focus areas distribution

### Papers (Database Ready)
- `GET /api/papers` - List all research papers (ready for scraping)
- `GET /api/papers?lab_id=1` - Papers from specific lab
- `POST /api/papers` - Add new paper manually
- `PUT /api/papers/{id}` - Update paper information
- `DELETE /api/papers/{id}` - Remove paper

### Statistics
- `GET /api/labs/stats` - Lab statistics
  - Total labs: 171
  - Countries: 24
  - Geographic distribution
  - Focus areas breakdown

### Data Import
- `POST /api/labs/import` - Import labs from CSV
  - Body: `{"csv_path": "path/to/file.csv"}`
  - Auto-geocoding and data normalization

### Response Format
```json
{
  "labs": [
    {
      "id": 1,
      "name": "Berkeley Robot Learning Lab (RLL)",
      "pi": "Pieter Abbeel",
      "institution": "UC Berkeley",
      "city": "Berkeley",
      "country": "USA",
      "latitude": 37.8719,
      "longitude": -122.2585,
      "focus_areas": ["Deep RL", "imitation learning", "sim2real"],
      "website": "https://rll.berkeley.edu/",
      "papers": []
    }
  ]
}
```

## 🧪 Development Status

| Component | Status | Description |
|-----------|--------|-------------|
| **Backend API** | ✅ Complete | Flask server with CORS, SQLite database |
| **Database** | ✅ Populated | 171 labs across 24 countries imported |
| **Lab Models** | ✅ Complete | SQLAlchemy models with relationships |
| **Paper Models** | ✅ Ready | Database schema ready for paper tracking |
| **API Endpoints** | ✅ Complete | Labs CRUD, filtering, statistics |
| **Data Import** | ✅ Complete | CSV import with 171 labs |
| **Frontend Stack** | ✅ Complete | Next.js 14 + Tailwind CSS |
| **Dashboard UI** | ✅ Complete | Lab cards, filters, metrics, search |
| **Responsive Design** | ✅ Complete | Mobile-friendly layout |
| **Production Build** | ✅ Validated | Successful build with 91.5 kB first load JS |
| **Paper Scraping** | 📋 Planned | ArXiv, Google Scholar integration |
| **Trend Analysis** | 📋 Planned | NLP-powered research trend detection |
| **Citation Network** | 📋 Planned | Collaboration pattern visualization |
| **Map Visualization** | 📋 Optional | Geographic lab distribution (optional feature) |

### Recent Updates
- ✅ Migrated from Create React App to Next.js 14
- ✅ Replaced Ant Design with Tailwind CSS
- ✅ Simplified component architecture
- ✅ Improved build performance (1189ms compile time)
- ✅ Removed unused CRA files and dependencies
- ✅ Database populated with 171 labs from CSV

## 🛠️ Configuration

### Backend Configuration

Create `backend/.env`:
```bash
DATABASE_URL=sqlite:///instance/robotics_sota.db
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Frontend Configuration

Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8080/api
```

### Environment Variables

**Backend**:
- `DATABASE_URL` - Database connection string (default: SQLite)
- `FLASK_ENV` - Environment mode (development/production)
- `FLASK_DEBUG` - Debug mode (True/False)
- `SECRET_KEY` - Flask secret key for sessions

**Frontend**:
- `NEXT_PUBLIC_API_URL` - Backend API base URL

### Database Configuration

The system uses SQLite by default for development:
- **Location**: `backend/instance/robotics_sota.db`
- **Auto-created**: Database and tables created on first run
- **Auto-import**: Labs imported from CSV on first run if database is empty

For production, configure PostgreSQL:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/robotics_sota
```

## 📁 Project Structure Details

```
robotics-SOTA/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory with CORS
│   │   ├── models/
│   │   │   └── __init__.py          # Lab, Paper, Researcher models
│   │   ├── api/
│   │   │   ├── labs.py              # Lab endpoints with filtering
│   │   │   ├── papers.py            # Paper CRUD endpoints
│   │   │   ├── trends.py            # Trend analysis (planned)
│   │   │   └── statistics.py        # Statistics endpoints
│   │   └── services/
│   │       ├── lab_importer.py      # CSV import with validation
│   │       ├── lab_paper_scraper.py # Paper scraping service
│   │       └── analytics.py         # Analytics service
│   ├── instance/
│   │   └── robotics_sota.db         # SQLite database (171 labs)
│   ├── run_dev.py                   # Development server launcher
│   ├── requirements.txt             # Python dependencies
│   └── tests/                       # Backend tests
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout with metadata
│   │   ├── page.tsx                 # Home page
│   │   └── globals.css              # Tailwind CSS imports
│   ├── components/
│   │   └── dashboard/
│   │       ├── LabsDashboard.tsx    # Main dashboard component
│   │       ├── MetricsSummary.tsx   # Statistics cards
│   │       ├── LabFilters.tsx       # Search and filter controls
│   │       ├── LabList.tsx          # Lab grid container
│   │       └── LabCard.tsx          # Individual lab card
│   ├── lib/
│   │   └── api.ts                   # API client with axios
│   ├── types/
│   │   └── lab.ts                   # TypeScript interfaces
│   ├── .next/                       # Next.js build output
│   ├── next.config.mjs              # Next.js configuration
│   ├── tailwind.config.ts           # Tailwind configuration
│   ├── tsconfig.json                # TypeScript configuration
│   └── package.json                 # Node.js dependencies
│
├── data/
│   └── robot_learning_labs_directory.csv  # Source data (178 labs)
│
├── scripts/
│   └── setup_database.py            # Database initialization
│
├── start-dev.sh                     # Development environment launcher
├── README.md                        # This file
└── LICENSE                          # MIT License
```

## 🧪 Development

### Running the Application

**Development Mode** (with hot reload):
```bash
bash start-dev.sh  # Both backend and frontend
```

**Backend Only**:
```bash
cd backend
python run_dev.py
```

**Frontend Only**:
```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend Production Build**:
```bash
cd frontend
npm run build     # Creates optimized production build
npm run start     # Serves production build
```

**Backend Production**:
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 'app:create_app()'
```

### Running Tests

**Backend Tests**:
```bash
cd backend
pytest tests/
```

**Frontend Tests** (coming soon):
```bash
cd frontend
npm test
```

### Code Quality

**Linting**:
```bash
cd frontend
npm run lint      # ESLint for TypeScript/React
```

**Type Checking**:
```bash
cd frontend
npm run type-check
```

### Database Management

**View Database**:
```bash
cd backend
python -c "
from app import create_app, db
from app.models import Lab
app = create_app()
with app.app_context():
    labs = Lab.query.all()
    print(f'Total labs: {len(labs)}')
    for lab in labs[:5]:
        print(f'- {lab.name} ({lab.country})')
"
```

**Reset Database**:
```bash
cd backend
rm instance/robotics_sota.db
python run_dev.py  # Will recreate and import
```

## 📈 Usage

1. **Browse Labs**: 
   - View all 171 labs in responsive card layout
   - See lab name, PI, institution, location, and research focus
   
2. **Search & Filter**:
   - Search by name, PI, institution, or city
   - Filter by country (24 countries available)
   - Filter by research focus area (manipulation, perception, etc.)
   - Real-time results as you type

3. **View Details**:
   - Each lab card shows key information
   - Focus areas displayed as tags
   - Website links when available
   - Ready for paper listings (coming soon)

4. **Statistics Dashboard**:
   - Live metrics: total labs, countries represented
   - Geographic distribution visualization
   - Research focus breakdown
   - Updated timestamp

5. **API Integration**:
   - Use REST API for custom applications
   - Filter and query labs programmatically
   - Export data in JSON format
   - Ready for paper tracking integration

### Next Steps
- Integrate ArXiv paper scraping
- Add Google Scholar citation tracking
- Implement research trend analysis
- Add collaboration network visualization
- Enable paper search and filtering

## 🧪 Development

### Running the Application

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.