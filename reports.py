import sqlite3
import pandas as pd

from database import DB_PATH


def get_appointment_report(start_at, end_before):
    connection = sqlite3.connect(DB_PATH)

    try:
        query = """
            SELECT
                a.id,
                d.id AS doctor_id,
                d.name AS doctor,
                p.name AS patient,
                a.starts_at,
                a.ends_at,
                a.status,
                a.reason
            FROM appointments AS a
            JOIN doctors AS d ON a.doctor_id = d.id
            JOIN patients AS p ON a.patient_id = p.id
            WHERE a.starts_at >= ?
              AND a.starts_at < ?
            ORDER BY a.starts_at
        """

        return pd.read_sql_query(
            query,
            connection,
            params=(start_at, end_before)
        )

    finally:
        connection.close()