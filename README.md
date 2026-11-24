# Parking Lot Management System

A web-based campus parking management system built with **Flask**, **PostgreSQL (`psycopg2`)**, and **Vanilla HTML/CSS/JavaScript**. Users log in using a 10-digit PRN, choose a parking facility, view a 10×10 parking spot grid (`P1`–`P100`), reserve open slots (`Reserved`), and transition their reserved slots to occupied (`Occupied`).

---

## Architecture & Tech Stack

- **Backend API (`app.py`):** Python Flask REST API with `flask-cors` enabled for cross-origin requests from the frontend on port `5000`.
- **Database Layer (`database.py` & PostgreSQL):** Connects to PostgreSQL via `psycopg2` and loads environment variables using `python-dotenv`.
- **Frontend (`index.html`, `campus.png`):** Single-page/multi-view Vanilla JS client using the `fetch` API and DOM manipulation to render parking facilities and the 10×10 spot matrix.

### Key Libraries & Modules

| Component | Libraries / Modules | Role |
| :--- | :--- | :--- |
| `app.py` | `Flask`, `request`, `jsonify`, `flask_cors.CORS`, `psycopg2.extras.RealDictCursor` | REST endpoints, JSON parsing/serialization, CORS, dict cursors |
| `database.py` | `psycopg2`, `os`, `dotenv.load_dotenv` | PostgreSQL connection management via `.env` |
| `index.html` | HTML5, CSS3, Vanilla JS (`fetch`, DOM APIs) | PRN login, lot selection, 10×10 grid (`P1`–`P100`), status updates |

---

## Database Schema Overview

- **`parking`**: Stores parking facilities (`id`, `name`).
- **`p_lots`**: Stores individual parking plot definitions (`id`, `parking_id`, `plot_number`).
- **`users`**: Stores student/user records (`id`, `username`, `password_hash`). During PRN-based reservation, new PRNs are auto-provisioned with `Student_<PRN>` and a placeholder hash if not already present.
- **`reservations`**: Tracks active slot bookings and occupancy (`id`, `user_id`, `parking_id`, `plot_number`, `status`), enforcing a single active spot per user (`user_id`) in the booking flow.

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health/welcome message for the API |
| `GET` | `/api/parkings` | Returns all parking facilities ordered by `id` |
| `POST` | `/api/parkings` | Adds a new parking facility (`{"name": "..."}`) |
| `GET` | `/api/plots` | Returns plot status records (`id`, `parking_id`, `plot_number`, `status`, `user_id`) from `reservations` |
| `POST` | `/api/plots` | Inserts a new spot into `p_lots` (`{"parking_id": 1, "plot_number": "P1"}`) |
| `GET` | `/api/users` | Returns user `id` and `username` records ordered by `id` |
| `POST` | `/api/users` | Registers a user (`{"username": "...", "password_hash": "..."}`) |
| `GET` | `/api/reservations` | Joins `reservations`, `users`, and `parking` to list reservations |
| `POST` | `/api/reservations` | Books a spot (`Reserved` or `Occupied`) if the user has no active spot; auto-creates user if needed |
| `PUT` | `/api/reservations/occupy` | Verifies `user_id` ownership for `(parking_id, plot_number)` and updates `status` to `Occupied` |

---

## Project Structure

```text
parking-lot-management-system/
├── app.py           # Flask application and REST API route handlers
├── database.py      # PostgreSQL connection helper using psycopg2 and .env
├── index.html       # Frontend UI, PRN flow, and 10x10 parking grid logic
├── campus.png       # Campus background image used by the frontend
├── .env             # Local database credentials (do not commit to version control)
└── README.md        # Project documentation
