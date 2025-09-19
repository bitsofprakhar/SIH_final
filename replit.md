# Jharkhand Document Verification System

## Project Overview
This is a Django-based document verification system designed for the Jharkhand Academic Council (JAC). The application provides a web interface for uploading and verifying certificates/marksheets using AI-powered document authentication.

## Architecture
- **Backend**: Django 5.2.6 with Django REST Framework
- **Frontend**: HTML/CSS/JavaScript with modern UI design
- **Database**: SQLite (for development)
- **File Storage**: Local file system with media uploads

## Key Components
- **Django Backend** (`backened/shaktishield/`): Main application server
- **Certificate Model**: Handles file uploads and verification results
- **REST API**: Provides endpoints for certificate upload and processing
- **Frontend Interface**: Professional government-style portal for document training and verification

## Current Setup
- Python 3.11 with Django and required dependencies installed
- Static files properly configured and served
- CORS enabled for frontend-backend communication
- Database migrations applied
- Workflow configured to run on port 5000

## API Endpoints
- `/`: Main application interface
- `/admin/`: Django admin interface
- `/upload/`: Certificate upload API endpoint
- `/static/`: Static files (CSS, JS)
- `/media/`: Uploaded media files

## Recent Changes (September 19, 2025)
- Configured Django settings for Replit environment (ALLOWED_HOSTS, CORS)
- Set up static files serving for CSS and JavaScript
- Updated frontend to use correct API endpoints
- Fixed JavaScript API base URL to use current domain instead of external ngrok URL
- Resolved JavaScript errors by adding missing setStatus function
- Configured deployment for autoscale hosting with gunicorn
- Added workflow for development server on port 5000
- Successfully imported GitHub project and made it functional in Replit environment

## Portal System Implementation (September 19, 2025)
- **Implemented** 3-portal system as requested:
  - **Single Verification**: Upload and verify individual certificates
  - **Batch Verification**: Process multiple certificates simultaneously
  - **Training Verification**: Training portal for learning verification process
- **Added** complete authentication system with secure login/logout
- **Secured** all portal access with authentication requirements
- **Fixed** CSRF protection and Django template rendering issues
- **Enhanced** upload endpoint security with authentication and session management
- **Implemented** proper Django URL routing with named patterns
- **Added** real-time certificate verification with loading states and result display

## Project Architecture
The system is designed as a document verification portal with:
1. Training portal for uploading authentic documents
2. Verification portal for testing document authenticity
3. AI/ML integration points for document analysis
4. Professional government-style UI design

## User Preferences
- Clean, professional interface following government portal design standards
- Secure file upload handling with proper validation
- Real-time status updates and progress tracking
- Responsive design for various screen sizes