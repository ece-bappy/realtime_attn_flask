# RFID Access Logs System

A real-time RFID card scanning monitoring system with modern UI, notifications, and SQLite database persistence.

## Project Structure

```
ur_final/
├── server.py          # Main application entry point
├── config.py          # Configuration settings
├── models.py          # Data models and database management
├── routes.py          # Flask routes and API endpoints
├── database_utils.py  # Database maintenance and backup utilities
├── templates/
│   └── index.html     # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css  # Stylesheets
│   └── js/
│       └── app.js     # Client-side JavaScript
├── requirements.txt    # Python dependencies
├── rfid_logs.db       # SQLite database (created automatically)
├── database_backups/  # Database backup directory
└── README.md          # This file
```

## Features

- **Real-time monitoring** of RFID card scans
- **Modern responsive UI** with gradient backgrounds and card layouts
- **Toast notifications** for new scan events
- **Live statistics** (total scans, unique users, today's scans)
- **SQLite database** for persistent data storage
- **RESTful API** endpoints for data access
- **WebSocket support** for real-time updates
- **Database backup and maintenance** utilities
- **Search and filtering** capabilities

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python server.py
   ```

3. Open your browser to `http://localhost:5000`

## Database Features

The system automatically creates a SQLite database (`rfid_logs.db`) with the following features:

- **Automatic table creation** on first run
- **Indexed fields** for optimal performance
- **Automatic backups** (configurable)
- **Data persistence** across application restarts
- **Automatic cleanup** of old logs

## API Endpoints

### Core Endpoints
- `GET /` - Main dashboard
- `POST /log` - Log a new RFID scan

### Data Endpoints
- `GET /api/logs` - Get recent logs
- `GET /api/stats` - Get current statistics
- `GET /api/search?q=<term>` - Search logs by UID or user
- `GET /api/logs/date/<YYYY-MM-DD>` - Get logs for specific date

### Maintenance Endpoints
- `POST /api/cleanup` - Clean up old logs
- `GET /api/health` - Health check with database status

## Configuration

Environment variables:
- `FLASK_DEBUG` - Enable/disable debug mode
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 5000)
- `SECRET_KEY` - Flask secret key
- `DATABASE_PATH` - Database file path
- `DATABASE_BACKUP_ENABLED` - Enable automatic backups
- `DATABASE_CLEANUP_DAYS` - Days to keep logs (default: 90)

## Usage

### Logging RFID Scans

Send POST requests to `/log` with form data:
- `uid` - RFID card UID (required)
- `user` - User name (optional, defaults to "Unknown")

Example:
```bash
curl -X POST http://localhost:5000/log \
  -d "uid=1234567890" \
  -d "user=John Doe"
```

### Searching Logs

Search by UID or user name:
```bash
curl "http://localhost:5000/api/search?q=John&limit=20"
```

### Getting Logs by Date

Get logs for a specific date:
```bash
curl "http://localhost:5000/api/logs/date/2024-01-15"
```

### Database Maintenance

Clean up old logs:
```bash
curl -X POST http://localhost:5000/api/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days_to_keep": 30}'
```

## Database Utilities

The `database_utils.py` module provides:

- **Automatic backups** with timestamped names
- **Database optimization** (VACUUM, REINDEX, ANALYZE)
- **Backup management** (create, restore, cleanup)
- **Database information** and statistics

## Performance Features

- **Database indexing** on timestamp and user fields
- **Query limits** to prevent excessive data retrieval
- **Automatic cleanup** of old log entries
- **Efficient pagination** for large datasets

## Security Features

- **Input validation** for all API endpoints
- **Query limits** to prevent abuse
- **Error handling** with proper HTTP status codes
- **SQL injection protection** using parameterized queries

## Troubleshooting

### Database Issues
- Check file permissions for the database directory
- Ensure sufficient disk space for database growth
- Verify SQLite3 is available in your Python environment

### Performance Issues
- Monitor database size and consider cleanup
- Check if indexes are being used effectively
- Consider increasing cleanup frequency for high-volume systems 