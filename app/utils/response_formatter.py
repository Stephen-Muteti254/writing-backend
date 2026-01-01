from flask import jsonify

def success_response(payload=None, message=None, status=200):
    resp = {"success": True}
    if payload is not None:
        resp.update(payload if isinstance(payload, dict) else {"data": payload})
    if message:
        resp["message"] = message
    return jsonify(resp), status

def error_response(code, message, details=None, status=400):
    err = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }
    return jsonify(err), status
