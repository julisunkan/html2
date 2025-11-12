# MailCraft - HTML Email Creator

## Overview

MailCraft is a Flask-based web application that enables users to create, preview, and export responsive HTML email templates. The application provides a form-based interface for customizing pre-designed email templates with live preview functionality. Users can save templates to a database, manage them, and export them as standalone HTML files. The application is designed as a Progressive Web App (PWA) for offline functionality and installability.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Template System**: The application uses Jinja2 templating with 10 pre-designed email templates (template1 through template10). Each template is a standalone HTML file with inline CSS for maximum email client compatibility. Templates use table-based layouts following email HTML best practices.

**Real-time Preview**: htmx.js is integrated to provide live preview updates as users modify form fields. The preview updates dynamically without full page reloads by posting to the `/preview` endpoint and updating a target container.

**Progressive Web App**: The application implements PWA features including a manifest.json for installability, service worker for offline caching, and multiple icon sizes (192x192, 512x512) with maskable variants for different platforms.

**Styling Framework**: Bootstrap 5 provides the UI components and responsive layout. Custom CSS in style.css extends Bootstrap with application-specific styling for forms, cards, and navigation.

### Backend Architecture

**Web Framework**: Flask serves as the lightweight web framework handling routing, request processing, and template rendering.

**Database Layer**: Flask-SQLAlchemy provides ORM functionality with SQLite as the database engine. The choice of SQLite allows for a portable, file-based database requiring no separate database server setup.

**Data Model**: Single EmailTemplate model stores all template variations with fields for title, subject, header, body, button text/link, footer, template name, and creation timestamp.

**Security Measures**: 
- CSRF protection using session-based tokens (generate_csrf_token/validate_csrf_token functions)
- Template name validation with an allowed list to prevent arbitrary template injection
- Secret key configuration via environment variable with fallback for development

**Session Management**: Flask sessions store CSRF tokens. The SECRET_KEY can be configured via environment variable for production deployments.

### Application Flow

**Template Creation**: Users select a template design, fill in content fields (header, body, button text/link, footer), and can preview in real-time. The preview endpoint renders the selected template with user-provided content.

**Template Storage**: Completed templates are saved to SQLite database via SQLAlchemy ORM. The EmailTemplate model captures all customization parameters along with metadata.

**Template Management**: The index page lists all saved templates ordered by creation date. Users can view, edit, or export individual templates.

**Export Functionality**: Templates can be exported as standalone HTML files containing all inline styles, making them ready for use in email campaigns.

### Design Patterns

**Template Whitelisting**: The ALLOWED_TEMPLATES list and validate_template_name() function implement a whitelist pattern to ensure only valid template names are processed, preventing path traversal or injection attacks.

**Separation of Concerns**: Models are separated in models.py, templates in dedicated directories, and static assets organized by type (css, js, icons).

**Progressive Enhancement**: The application works without JavaScript but enhances the experience with htmx for live previews when available.

## External Dependencies

### Python Packages
- **Flask**: Core web framework for routing, request handling, and rendering
- **Flask-SQLAlchemy**: ORM layer providing database abstraction and model management

### Frontend Libraries
- **Bootstrap 5** (CDN): UI component framework and responsive grid system
- **htmx.js** (CDN): JavaScript library enabling AJAX-like functionality with HTML attributes for live preview updates

### Database
- **SQLite**: Embedded relational database storing email templates with no external server required

### PWA Assets
- **Service Worker**: Caches application resources for offline functionality
- **Web App Manifest**: Defines installability parameters and app metadata
- **Icon Set**: Multiple sizes and formats for various platforms and contexts

### Session Storage
- **Flask Sessions**: Server-side session management for CSRF token storage using SECRET_KEY for encryption