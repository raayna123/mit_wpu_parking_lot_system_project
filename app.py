from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from database import get_db_connection
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
# Enable CORS so your separate HTML/JS frontend can communicate with this API
CORS(app)

# ==========================================
# PARKING FACILITIES ENDPOINTS
# ==========================================

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Parking Lot Management API!"}), 200

@app.route('/api/parkings', methods=['GET'])
def get_parkings():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Removed 'location' from the SELECT query
        cur.execute("SELECT id, name FROM parking ORDER BY id")
        parkings = cur.fetchall()
        return jsonify(parkings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass

@app.route('/api/parkings', methods=['POST'])
def add_parking():
    data = request.json or {}
    name = str(data.get("name", "")).strip()

    if not name:
        return jsonify({"error": "Parking name is required."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO parking (name) VALUES (%s)", (name,))
        conn.commit()
        return jsonify({"message": "Parking facility added successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass

# ==========================================
# INDIVIDUAL PARKING SPOTS (P_LOTS) ENDPOINTS
# ==========================================

from psycopg2.extras import RealDictCursor

@app.route('/api/plots', methods=['GET'])
def get_plots():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, parking_id, plot_number, status, user_id FROM reservations") 
        plots = cur.fetchall()
        return jsonify(plots), 200
    except Exception as e:
        return jsonify([]), 200
    finally:
        try: cur.close(); conn.close()
        except: pass

@app.route('/api/plots', methods=['POST'])
def add_plot():
    data = request.json or {}
    try:
        parking_id = int(data.get("parking_id"))
    except (ValueError, TypeError):
        return jsonify({"error": "Valid parking ID is required."}), 400

    plot_number = str(data.get("plot_number", "")).strip()
    if not plot_number:
        return jsonify({"error": "Plot number is required."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO p_lots (parking_id, plot_number) VALUES (%s, %s)", (parking_id, plot_number))
        conn.commit()
        return jsonify({"message": "Parking spot added successfully."}), 201
    except psycopg2.IntegrityError:
        return jsonify({"error": "Invalid parking facility ID."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass

# ==========================================
# USERS ENDPOINTS
# ==========================================

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, username FROM users ORDER BY id")
        users = cur.fetchall()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.json or {}
    username = str(data.get("username", "")).strip()
    password_hash = str(data.get("password_hash", "")).strip()

    if not (username and password_hash):
        return jsonify({"error": "Username and password hash are required."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        return jsonify({"message": "User registered successfully."}), 201
    except psycopg2.IntegrityError:
        return jsonify({"error": "Username already exists."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass

# ==========================================
# RESERVATIONS ENDPOINTS
# ==========================================

@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT r.id, r.user_id, u.username, r.parking_id, pk.name AS parking_name, r.status
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            JOIN parking pk ON r.parking_id = pk.id
            ORDER BY r.id
        """)
        reservations = cur.fetchall()
        return jsonify(reservations), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass



@app.route('/api/reservations', methods=['POST'])
def add_reservation():
    data = request.json or {}
    user_id = data.get("user_id")
    parking_id = data.get("parking_id")
    plot_number = data.get("plot_number")
    status = data.get("status", "Reserved") # 'Reserved' (green) or 'Occupied' (red)

    if not (user_id and parking_id and plot_number):
        return jsonify({"error": "Missing required reservation details."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if this student ID already has an active spot booked anywhere
        cur.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
        if cur.fetchone():
            return jsonify({"error": "You already have an active parking spot booked! Each user can only book one spot."}), 400

        # Automatically insert user if not exists
        default_username = f"Student_{user_id}"
        default_password = "dummy_hash"
        cur.execute(
            """
            INSERT INTO users (id, username, password_hash) VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (user_id, default_username, default_password)
        )
        
        # Insert reservation/occupancy
        cur.execute(
            "INSERT INTO reservations (user_id, parking_id, plot_number, status) VALUES (%s, %s, %s, %s)",
            (user_id, parking_id, plot_number, status)
        )
        conn.commit()
        return jsonify({"message": "Spot updated successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass

@app.route('/api/reservations/occupy', methods=['PUT'])
def occupy_reserved_spot():
    data = request.json or {}
    user_id = data.get("user_id")
    parking_id = data.get("parking_id")
    plot_number = data.get("plot_number")

    if not (user_id and parking_id and plot_number):
        return jsonify({"error": "Missing required details."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Find the reservation for this plot
        cur.execute(
            "SELECT * FROM reservations WHERE parking_id = %s AND plot_number = %s",
            (parking_id, plot_number)
        )
        reservation = cur.fetchone()
        
        if not reservation:
            return jsonify({"error": "Spot not found."}), 404
            
        # Verify if current user matches the reservation owner
        if str(reservation['user_id']) != str(user_id):
            return jsonify({"error": "Reserved by someone else"}), 403
            
        # Update status to Occupied (red)
        cur.execute(
            "UPDATE reservations SET status = 'Occupied' WHERE parking_id = %s AND plot_number = %s",
            (parking_id, plot_number)
        )
        conn.commit()
        return jsonify({"message": "Spot marked as occupied successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)