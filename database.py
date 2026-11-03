import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "hospital.db"

def create_tables():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        cursor = connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL
                )
            """)
        
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    specialty TEXT NOT NULL
                )
            """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY,
                    doctor_id INTEGER NOT NULL,
                    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    UNIQUE (doctor_id, weekday),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                )
            """)
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS appointments (
                            id INTEGER PRIMARY KEY,
                            patient_id INTEGER NOT NULL,
                            doctor_id INTEGER NOT NULL,
                            starts_at TEXT NOT NULL,
                            ends_at TEXT NOT NULL,
                            reason TEXT NOT NULL,
                            status TEXT NOT NULL DEFAULT 'Scheduled'
                                CHECK (status IN ('Scheduled', 'Completed', 'Cancelled')),
                            FOREIGN KEY (patient_id) REFERENCES patients(id),
                            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                        )
                    """)
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS staff (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                            password_hash BLOB NOT NULL,
                            salt BLOB NOT NULL,
                            iterations INTEGER NOT NULL
                        )
                    """)
        connection.commit()
    finally:
        connection.close()

def add_doctor(name,specialty):
    connection = sqlite3.connect(DB_PATH)
    try:
        
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO doctors (name, specialty)
            VALUES (?, ?)
            """,
            (name, specialty))
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        connection.rollback()
    finally:
        connection.close() 
    
        
def add_patient(name,phone):
    connection = sqlite3.connect(DB_PATH)
    
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO patients (name, phone) VALUES (?, ?)",
            (name, phone))
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        connection.rollback()
    finally:
        connection.close()
def get_patients():
    connection = sqlite3.connect(DB_PATH)
    
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT id,name FROM patients ORDER BY id DESC""")
        return cursor.fetchall()
    finally:
        connection.close()
def search_patients(search_text):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT id, name, phone
            FROM patients
            WHERE name LIKE ?
            ORDER BY id DESC
            """,("%"+search_text+"%",))
        return cursor.fetchall()
    finally:
        connection.close()
def update_patient(patient_id,name,phone,):
    
    connection = sqlite3.connect(DB_PATH)
    
    try:
        cursor = connection.cursor()
        cursor.execute( """
            UPDATE patients
            SET name = ?, phone = ?
            WHERE id = ?
            """,
            (name, phone, patient_id))
        connection.commit()
    except sqlite3.Error as e:
        connection.rollback()
    finally:
        connection.close()

def search_doctors(search_text):
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, name, specialty
            FROM doctors
            WHERE name LIKE ?
            ORDER BY id DESC
            """,("%"+search_text+"%",))
        return cursor.fetchall()
    finally:
        connection.close()

def get_doctors():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM doctors ORDER BY name")
        return cursor.fetchall()
    finally:
        connection.close()
def save_update_schedule(doctor_id,weekday,start_time,end_time):
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        cursor = connection.cursor()
        cursor.execute(
                            """
                            INSERT INTO schedules (
                                doctor_id, weekday, start_time, end_time
                            )
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT (doctor_id, weekday)
                            DO UPDATE SET
                                start_time = excluded.start_time,
                                end_time = excluded.end_time
                            """,
                            (doctor_id, weekday, start_time, end_time)
                        )
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        connection.rollback()
    finally:
        connection.close()
def search_schedule(search_id):
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id,doctor_id, weekday, start_time, end_time
            FROM schedules
            WHERE doctor_id LIKE ?
            ORDER BY id DESC
            """,("%"+search_id+"%",))
        return cursor.fetchall()
    finally:
        connection.close()     
def get_doctor_schedule(doctor_id,start):
    connection = sqlite3.connect(DB_PATH)
    
    try:
        cursor = connection.cursor()
        cursor.execute(
                        """
                        SELECT start_time, end_time
                        FROM schedules
                        WHERE doctor_id = ? AND weekday = ?
                        """,
                        (doctor_id, start.weekday())
                                )

        schedule = cursor.fetchone()  
        return schedule
    finally:
        connection.close()
        
from datetime import datetime, timedelta, time


def book_appointment(
    patient_id,
    doctor_id,
    start,
    duration,
    reason
):
    if patient_id is None or doctor_id is None:
        raise ValueError("Please select a patient and doctor.")

    if duration not in (15, 30, 45, 60):
        raise ValueError("Select a valid appointment duration.")

    reason = reason.strip()

    if not reason:
        raise ValueError("Please enter an appointment reason.")

    # Store appointments at minute precision.
    start = start.replace(second=0, microsecond=0)
    end = start + timedelta(minutes=duration)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        # Reserve the write transaction before checking availability.
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        if start <= datetime.now():
            raise ValueError("Appointment must be in the future.")

        # Check patient exists.
        cursor.execute(
            "SELECT id FROM patients WHERE id = ?",
            (patient_id,)
        )

        if cursor.fetchone() is None:
            raise ValueError("The selected patient no longer exists.")

        # Check doctor exists.
        cursor.execute(
            "SELECT id FROM doctors WHERE id = ?",
            (doctor_id,)
        )

        if cursor.fetchone() is None:
            raise ValueError("The selected doctor no longer exists.")

        # Read the doctor's working hours.
        cursor.execute(
            """
            SELECT start_time, end_time
            FROM schedules
            WHERE doctor_id = ? AND weekday = ?
            """,
            (doctor_id, start.weekday())
        )

        schedule = cursor.fetchone()

        if schedule is None:
            raise ValueError(
                "The doctor has no schedule for this weekday."
            )

        opening = datetime.combine(
            start.date(),
            time.fromisoformat(schedule[0])
        )

        closing = datetime.combine(
            start.date(),
            time.fromisoformat(schedule[1])
        )

        if start < opening or end > closing:
            raise ValueError(
                "Appointment is outside the doctor's working hours."
            )

        # Use one consistent format for stored timestamps.
        starts_at = start.strftime("%Y-%m-%d %H:%M:%S")
        ends_at = end.strftime("%Y-%m-%d %H:%M:%S")

        # Check both doctor and patient availability.
        cursor.execute(
            """
            SELECT id
            FROM appointments
            WHERE status != 'Cancelled'
              AND (doctor_id = ? OR patient_id = ?)
              AND starts_at < ?
              AND ends_at > ?
            """,
            (doctor_id, patient_id, ends_at, starts_at)
        )

        if cursor.fetchone() is not None:
            raise ValueError(
                "The doctor or patient already has an "
                "appointment during this time."
            )

        # All checks passed: save the appointment.
        cursor.execute(
            """
            INSERT INTO appointments (
                patient_id,
                doctor_id,
                starts_at,
                ends_at,
                reason
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                doctor_id,
                starts_at,
                ends_at,
                reason
            )
        )

        appointment_id = cursor.lastrowid
        connection.commit()

        return appointment_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
def get_appointments():
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                a.id,
                p.name,
                d.name,
                a.starts_at,
                a.ends_at,
                a.status,
                a.reason
            FROM appointments AS a
            JOIN patients AS p ON a.patient_id = p.id
            JOIN doctors AS d ON a.doctor_id = d.id
            ORDER BY a.starts_at
        """)

        return cursor.fetchall()

    finally:
        connection.close()
def update_appointment_status(appointment_id, new_status):
    if new_status not in ("Cancelled", "Completed"):
        raise ValueError("Invalid appointment status.")

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE appointments
            SET status = ?
            WHERE id = ?
              AND status = 'Scheduled'
            """,
            (new_status, appointment_id)
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "The appointment was not found or is no longer Scheduled."
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()       
    
        
