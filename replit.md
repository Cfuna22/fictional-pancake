# Overview

This is a CRM Sentiment Data Generator and Dashboard application built with Flask. The application generates realistic customer relationship management (CRM) data combined with sentiment analysis from customer feedback. It's designed to help users create comprehensive datasets for Tableau analysis and business intelligence dashboards.

The application provides functionality to generate synthetic but realistic customer data, sales deals, and customer feedback with sentiment scoring. It also includes AI-powered recommendations based on the generated data and offers integration guides for popular visualization tools like Tableau.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 with dark theme for responsive design
- **Charts and Visualization**: Chart.js for client-side data visualization
- **Styling**: Custom CSS with Font Awesome icons for enhanced user experience

## Backend Architecture
- **Web Framework**: Flask with Python for rapid development and simplicity
- **Data Generation**: Custom `CRMDataGenerator` class using Faker library for realistic synthetic data
- **AI Recommendations**: `AIRecommendations` class for generating business insights and actionable recommendations
- **Session Management**: Flask sessions with configurable secret key for temporary data storage
- **File Handling**: In-memory ZIP file generation for data export

## Data Layer
- **Data Processing**: Pandas DataFrames for data manipulation and analysis
- **Data Generation Strategy**: Seeded random generation for reproducible datasets
- **Export Formats**: CSV files packaged in ZIP archives for easy download

## Key Design Patterns
- **MVC Pattern**: Clear separation between models (data generators), views (templates), and controllers (Flask routes)
- **Factory Pattern**: Data generator classes that create different types of related datasets
- **Service Layer**: Separate classes for data generation and AI recommendations to maintain single responsibility

## API Structure
- RESTful endpoints for data generation and retrieval
- JSON responses for AJAX requests and API interactions
- Form-based POST endpoints for user data generation requests

# External Dependencies

## Core Dependencies
- **Flask**: Web framework for application structure and routing
- **Pandas**: Data manipulation and analysis library
- **NumPy**: Numerical computing for data generation algorithms
- **Faker**: Library for generating realistic fake data

## Frontend Dependencies
- **Bootstrap 5**: CSS framework delivered via CDN
- **Chart.js**: JavaScript charting library delivered via CDN
- **Font Awesome**: Icon library for UI enhancement

## Development Tools
- **Python Logging**: Built-in logging for debugging and monitoring
- **Environment Variables**: Configuration management for deployment flexibility

## Integration Targets
- **Tableau**: Primary target for data visualization and dashboard creation
- **CSV Export**: Standard format for data portability to various BI tools