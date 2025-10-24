from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Simple token for authentication
API_TOKEN = "secret123"  # in real projects, use env variables

def to_float(x):
    try:
        return float(x)
    except:
        return None

# Helper for invalid numeric input
def invalid_numeric_response():
    return jsonify({"detail": "Invalid numeric input"}), 400

# Decorator to require token for endpoints
def require_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"detail": "Unauthorized"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # preserve function name
    return wrapper

@app.route("/add", methods=["GET"])
@require_token
def add():
    a = request.args.get("a")
    b = request.args.get("b")
    a_f = to_float(a)
    b_f = to_float(b)
    if a_f is None or b_f is None:
        return invalid_numeric_response()
    return jsonify({"result": a_f + b_f})

@app.route("/subtract", methods=["GET"])
@require_token
def subtract():
    a = request.args.get("a")
    b = request.args.get("b")
    a_f = to_float(a)
    b_f = to_float(b)
    if a_f is None or b_f is None:
        return invalid_numeric_response()
    return jsonify({"result": a_f - b_f})

@app.route("/multiply", methods=["GET"])
@require_token
def multiply():
    a = request.args.get("a")
    b = request.args.get("b")
    a_f = to_float(a)
    b_f = to_float(b)
    if a_f is None or b_f is None:
        return invalid_numeric_response()
    return jsonify({"result": a_f * b_f})

@app.route("/divide", methods=["GET"])
@require_token
def divide():
    a = request.args.get("a")
    b = request.args.get("b")
    a_f = to_float(a)
    b_f = to_float(b)
    if a_f is None or b_f is None:
        return invalid_numeric_response()
    if b_f == 0:
        return jsonify({"detail": "Division by zero"}), 400
    return jsonify({"result": a_f / b_f})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

