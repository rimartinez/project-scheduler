# Employee-Client Scheduling Service

A modern, minimal scheduling service built with Django, HTMX, and Tailwind CSS.

## Features

- **Role-based Access Control**: Employees, Supervisors, and Clients with distinct permissions
- **Schedule Management**: Create, edit, and manage schedules with approval workflow
- **Modern UI**: Clean, responsive interface with shadcn/ui components
- **Calendar & Table Views**: Multiple ways to view and interact with schedules
- **Reporting**: Comprehensive reporting for all user types
- **Real-time Updates**: HTMX-powered dynamic interactions

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: HTMX + Tailwind CSS
- **Database**: PostgreSQL
- **Sessions**: Database-based (Redis optional)
- **Authentication**: JWT + Session-based

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Tailwind CSS)
npm install
```

### 2. Set Up Environment

```bash
# Copy environment file
cp env.example .env

# Edit .env with your settings
nano .env
```

### 3. Set Up Database

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Build CSS

```bash
# Build Tailwind CSS
npm run build-css-prod
```

### 5. Run Development Server

```bash
# Start Django server
python manage.py runserver
```

## User Roles

### Employees
- Create and manage their own schedules
- Submit schedules for approval
- View personal calendar and reports

### Supervisors
- Review and approve/reject schedules
- View all employee schedules
- Access comprehensive reports

### Clients
- View assigned employee schedules
- Track service hours
- Access client-specific reports

## Project Structure

```
scheduler/
├── apps/
│   ├── accounts/          # User management
│   ├── schedules/         # Schedule CRUD and views
│   ├── clients/           # Client management
│   └── reports/           # Reporting system
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── scheduler/            # Django project settings
└── requirements.txt      # Python dependencies
```

## Development

### Adding New Features

1. Create models in the appropriate app
2. Add views and URL patterns
3. Create templates with Tailwind CSS
4. Add HTMX for interactivity
5. Update tests

### Styling

- Use Tailwind CSS utility classes
- Follow the design system in `static/css/input.css`
- Use shadcn/ui component patterns

### Database Changes

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in environment
2. Configure production database
3. Set up Redis for caching and Celery
4. Configure email settings
5. Set up static file serving

### Docker (Optional)

```bash
# Build and run with Docker
docker-compose up -d
```

## API Endpoints

- `GET /api/schedules/` - List schedules
- `POST /api/schedules/` - Create schedule
- `GET /api/schedules/{id}/` - Get schedule details
- `PUT /api/schedules/{id}/` - Update schedule
- `DELETE /api/schedules/{id}/` - Delete schedule
- `POST /api/schedules/{id}/approve/` - Approve schedule
- `POST /api/schedules/{id}/reject/` - Reject schedule

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
