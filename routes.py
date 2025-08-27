from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit
from models import LogManager
from datetime import datetime

# Create blueprint
api = Blueprint('api', __name__)

# Initialize log manager
log_manager = LogManager()

def init_routes(app, socketio):
    """Initialize routes with the Flask app and SocketIO instance"""
    
    @app.route("/")
    def home():
        return render_template('index.html')
    
    @app.route("/log", methods=["POST"])
    def log_card():
        uid = request.form.get("uid")
        user = request.form.get("user", "Unknown")
        
        if not uid:
            return jsonify({"error": "Missing UID"}), 400
        
        try:
            # Add log entry to database
            log_entry = log_manager.add_log(uid, user)
            log_data = log_entry.to_dict()
            
            # Emit real-time update
            socketio.emit("new_log", log_data)
            
            return jsonify({"message": "Log entry created", "log": log_data}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to create log entry: {str(e)}"}), 500
    
    @app.route("/api/logs")
    def get_logs():
        """Get recent logs"""
        try:
            limit = request.args.get('limit', 50, type=int)
            if limit > 1000:  # Prevent excessive queries
                limit = 1000
            
            logs = log_manager.get_recent_logs(limit)
            return jsonify({"logs": logs, "count": len(logs)})
        except Exception as e:
            return jsonify({"error": f"Failed to fetch logs: {str(e)}"}), 500
    
    @app.route("/api/stats")
    def get_stats():
        """Get current statistics"""
        try:
            stats = log_manager.get_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({"error": f"Failed to fetch stats: {str(e)}"}), 500
    
    @app.route("/api/search")
    def search_logs():
        """Search logs by UID or user name"""
        try:
            search_term = request.args.get('q', '')
            limit = request.args.get('limit', 50, type=int)
            
            if not search_term:
                return jsonify({"error": "Search term required"}), 400
            
            if limit > 1000:
                limit = 1000
            
            logs = log_manager.search_logs(search_term, limit)
            return jsonify({"logs": logs, "count": len(logs), "search_term": search_term})
        except Exception as e:
            return jsonify({"error": f"Search failed: {str(e)}"}), 500
    
    @app.route("/api/logs/date/<date>")
    def get_logs_by_date(date):
        """Get logs for a specific date (YYYY-MM-DD format)"""
        try:
            # Validate date format
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            
            limit = request.args.get('limit', 50, type=int)
            if limit > 1000:
                limit = 1000
            
            logs = log_manager.get_logs_by_date(date, limit)
            return jsonify({"logs": logs, "count": len(logs), "date": date})
        except Exception as e:
            return jsonify({"error": f"Failed to fetch logs for date: {str(e)}"}), 500
    
    @app.route("/api/cleanup", methods=["POST"])
    def cleanup_logs():
        """Clean up old logs (admin function)"""
        try:
            days_to_keep = request.json.get('days_to_keep', 90)
            
            if days_to_keep < 1:
                return jsonify({"error": "Days to keep must be at least 1"}), 400
            
            deleted_count = log_manager.cleanup_old_logs(days_to_keep)
            return jsonify({
                "message": f"Cleanup completed",
                "deleted_count": deleted_count,
                "days_to_keep": days_to_keep
            })
        except Exception as e:
            return jsonify({"error": f"Cleanup failed: {str(e)}"}), 500
    
    @app.route("/api/health")
    def health_check():
        """Health check endpoint"""
        try:
            stats = log_manager.get_stats()
            return jsonify({
                "status": "healthy", 
                "timestamp": datetime.now().isoformat(),
                "database": "connected",
                "stats": stats
            })
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500 