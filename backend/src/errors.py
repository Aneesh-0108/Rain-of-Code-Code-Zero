from flask import jsonify

class APIError(Exception):
    def __init__(self, message, status=400, code="bad_request"):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api(err):
        return jsonify({"error": err.code, "message": err.message}), err.status

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not_found"}), 404

    @app.errorhandler(500)
    def server_error(err):
        return jsonify({"error": "server_error", "message": "Internal error"}), 500