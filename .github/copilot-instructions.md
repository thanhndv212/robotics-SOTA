<!-- Workspace-specific instructions for robotics-SOTA project -->

This is a comprehensive robotics research trends mapping system with the following components:

## Project Overview
- **Purpose**: Interactive mapping and analysis of global robotics research trends
- **Data**: 50+ robotics labs worldwide with automated paper tracking
- **Tech Stack**: React + TypeScript frontend, Python Flask/FastAPI backend, PostgreSQL database
- **Features**: Geographic visualization, trend analysis, paper classification, real-time updates

## Development Guidelines
- Use Python for backend APIs and data processing
- Use React with TypeScript for frontend components
- Implement D3.js for data visualizations
- Use Mapbox for geographic mapping
- Follow RESTful API design patterns
- Include comprehensive error handling and logging
- Write unit tests for critical components
- Use Docker for containerization

## Architecture Components
- **Frontend**: Interactive map, search/filter interface, trend dashboards
- **Backend**: API endpoints, data processing, paper tracking, trend analysis
- **Database**: Lab data, papers, researchers, citations, trends
- **Services**: ArXiv integration, Google Scholar scraping, NLP classification

## Code Organization
- `/frontend/` - React application
- `/backend/` - Python API and services
- `/data/` - CSV imports and processed datasets
- `/scripts/` - Data processing and automation
- `/docs/` - Documentation and API specs
- `/tests/` - Unit and integration tests