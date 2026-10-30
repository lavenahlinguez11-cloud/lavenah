# ===== PROBLEMA =====
# Kalat-kalat ang multa sa school (ID replacement, nasirang gamit, huling
# bayad, atbp.). Nasa notebook lang ang record kaya nawawala ang resibo,
# hindi natrack ang partial payment, at walang aging kung sino ang matagal
# nang may utang. Hindi rin malaman ng office kung magkano ang nakolekta.
#
# ===== SOLUSYON =====
# Ang balanse ay (amount - SUM(amount_paid)) mula sa SQL, kaya tama kahit
# partial ang bayad. May DATEDIFF() aging report, collection report per
# buwan/uri, top debtors, at waive na may dahilan.

import os

import mysql.connector
from mysql.connector import Error


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "school_fines_db")


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
    )


def test_connection():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM fines LIMIT 1")
            cursor.fetchone()
            return True, "Koneksyon sa School Fines database ay OK na."
        return False, "Hindi makakonekta sa database."
    except Error as error:
        return False, str(error)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# STUDENTS
def add_student(student_id, full_name, grade_level, section):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO students (student_id, full_name, grade_level, section)
            VALUES (%s,%s,%s,%s)
            """,
            (student_id, full_name, grade_level, section),
        )
        connection.commit()
        return cursor.lastrowid
    except Error:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def find_student(student_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def list_students():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students ORDER BY grade_level, section, full_name")
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# FINE TYPES
def add_fine_type(type_name, default_amount, description):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO fine_types (type_name, default_amount, description)
            VALUES (%s,%s,%s)
            """,
            (type_name, default_amount, description),
        )
        connection.commit()
        return cursor.lastrowid
    except Error:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def find_fine_type(type_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM fine_types WHERE type_id = %s", (type_id,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def list_fine_types():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM fine_types ORDER BY type_name")
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# FINES
def issue_fine(student_id, type_id, description, amount, date_issued,
               due_date, issued_by, remarks):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO fines (student_id, type_id, description, amount,
                               date_issued, due_date, issued_by, remarks)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (student_id, type_id, description, amount, date_issued,
             due_date, issued_by, remarks),
        )
        connection.commit()
        return cursor.lastrowid
    except Error:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def find_fine(fine_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT f.fine_id, f.student_id, s.full_name, s.grade_level, s.section,
                   f.type_id, t.type_name, f.description, f.amount,
                   f.date_issued, f.due_date, f.status, f.issued_by, f.remarks,
                   COALESCE(p.paid, 0) AS paid,
                   f.amount - COALESCE(p.paid, 0) AS balance,
                   DATEDIFF(CURDATE(), f.due_date) AS days_overdue
            FROM fines f
            JOIN students s ON s.student_id = f.student_id
            JOIN fine_types t ON t.type_id = f.type_id
            LEFT JOIN (
                SELECT fine_id, SUM(amount_paid) AS paid
                FROM payments
                GROUP BY fine_id
            ) p ON p.fine_id = f.fine_id
            WHERE f.fine_id = %s
            """,
            (fine_id,),
        )
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def list_fines(student_id=None):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        base = """
            SELECT f.fine_id, f.student_id, s.full_name, s.grade_level, s.section,
                   f.type_id, t.type_name, f.description, f.amount,
                   f.date_issued, f.due_date, f.status, f.issued_by, f.remarks,
                   COALESCE(p.paid, 0) AS paid,
                   f.amount - COALESCE(p.paid, 0) AS balance,
                   DATEDIFF(CURDATE(), f.due_date) AS days_overdue
            FROM fines f
            JOIN students s ON s.student_id = f.student_id
            JOIN fine_types t ON t.type_id = f.type_id
            LEFT JOIN (
                SELECT fine_id, SUM(amount_paid) AS paid
                FROM payments
                GROUP BY fine_id
            ) p ON p.fine_id = f.fine_id
        """
        if student_id:
            cursor.execute(
                base + " WHERE f.student_id = %s ORDER BY f.status, f.date_issued DESC, f.fine_id DESC",
                (student_id,),
            )
        else:
            cursor.execute(
                base + " ORDER BY f.status, f.date_issued DESC, f.fine_id DESC"
            )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def next_receipt_no(payment_date):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) + 1 AS seq FROM payments WHERE payment_date = %s",
            (payment_date,),
        )
        seq = cursor.fetchone()["seq"]
        return f"R{payment_date.replace('-', '')}-{seq:04d}"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def record_payment(fine_id, amount, payment_date, receipt_no, received_by, remarks):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT fine_id, amount, status FROM fines WHERE fine_id = %s FOR UPDATE",
            (fine_id,),
        )
        fine = cursor.fetchone()
        if not fine:
            raise ValueError("Wala ang fine record na ito.")
        if fine["status"] == "PAID":
            raise ValueError("Bayad na ang multang ito.")
        if fine["status"] == "WAIVED":
            raise ValueError("Waived na ang multang ito. Hindi na pwedeng bayaran.")

        cursor.execute(
            "SELECT COALESCE(SUM(amount_paid), 0) AS paid FROM payments WHERE fine_id = %s",
            (fine_id,),
        )
        paid = float(cursor.fetchone()["paid"] or 0)
        total = float(fine["amount"])
        balance = round(total - paid, 2)
        amount = round(float(amount), 2)
        if amount <= 0:
            raise ValueError("Dapat mas malaki sa 0 ang bayad.")
        if amount > balance:
            raise ValueError(f"Sobra sa balanse. Balanse: PHP {balance:,.2f}")

        new_paid = round(paid + amount, 2)
        new_status = "PAID" if new_paid >= total else "PARTIAL"

        cursor.execute(
            """
            INSERT INTO payments (fine_id, amount_paid, payment_date,
                                  receipt_no, received_by, remarks)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (fine_id, amount, payment_date, receipt_no, received_by, remarks),
        )
        payment_id = cursor.lastrowid
        cursor.execute(
            "UPDATE fines SET status = %s WHERE fine_id = %s",
            (new_status, fine_id),
        )
        connection.commit()
        return {
            "payment_id": payment_id,
            "status": new_status,
            "balance": round(total - new_paid, 2),
        }
    except Exception:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def waive_fine(fine_id, reason):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT fine_id, status FROM fines WHERE fine_id = %s FOR UPDATE",
            (fine_id,),
        )
        fine = cursor.fetchone()
        if not fine:
            raise ValueError("Wala ang fine record na ito.")
        if fine["status"] == "PAID":
            raise ValueError("Bayad na ang multang ito. Hindi na kailangang i-waive.")
        if fine["status"] == "WAIVED":
            raise ValueError("Waived na ang multang ito.")
        cursor.execute(
            """
            UPDATE fines
            SET status = 'WAIVED',
                remarks = CONCAT(COALESCE(remarks, ''), ' | WAIVED: ', %s)
            WHERE fine_id = %s
            """,
            (reason, fine_id),
        )
        connection.commit()
        return True
    except Exception:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# REPORTS
def overdue_accounts():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT f.fine_id, f.student_id, s.full_name, s.grade_level, s.section,
                   t.type_name, f.amount, f.date_issued, f.due_date, f.status,
                   COALESCE(p.paid, 0) AS paid,
                   f.amount - COALESCE(p.paid, 0) AS balance,
                   DATEDIFF(CURDATE(), f.due_date) AS days_overdue,
                   CASE
                       WHEN DATEDIFF(CURDATE(), f.due_date) <= 30 THEN '1-30 araw'
                       WHEN DATEDIFF(CURDATE(), f.due_date) <= 60 THEN '31-60 araw'
                       ELSE '61+ araw'
                   END AS bucket
            FROM fines f
            JOIN students s ON s.student_id = f.student_id
            JOIN fine_types t ON t.type_id = f.type_id
            LEFT JOIN (
                SELECT fine_id, SUM(amount_paid) AS paid
                FROM payments
                GROUP BY fine_id
            ) p ON p.fine_id = f.fine_id
            WHERE f.status IN ('UNPAID', 'PARTIAL')
              AND f.amount - COALESCE(p.paid, 0) > 0
              AND f.due_date < CURDATE()
            ORDER BY days_overdue DESC, balance DESC
            """
        )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def collection_by_month():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT DATE_FORMAT(payment_date, '%Y-%m') AS month,
                   COUNT(*) AS payments,
                   SUM(amount_paid) AS collected
            FROM payments
            GROUP BY month
            ORDER BY month DESC
            """
        )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def collection_by_type():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT t.type_name,
                   COUNT(p.payment_id) AS payments,
                   SUM(p.amount_paid) AS collected
            FROM payments p
            JOIN fines f ON f.fine_id = p.fine_id
            JOIN fine_types t ON t.type_id = f.type_id
            GROUP BY t.type_name
            ORDER BY collected DESC
            """
        )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def outstanding_summary():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT COALESCE(SUM(f.amount), 0) AS total_fines,
                   COALESCE(SUM(COALESCE(p.paid, 0)), 0) AS total_paid,
                   COALESCE(SUM(f.amount - COALESCE(p.paid, 0)), 0) AS total_balance
            FROM fines f
            LEFT JOIN (
                SELECT fine_id, SUM(amount_paid) AS paid
                FROM payments
                GROUP BY fine_id
            ) p ON p.fine_id = f.fine_id
            WHERE f.status <> 'WAIVED'
            """
        )
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def top_debtors(limit=10):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.student_id, s.full_name, s.grade_level, s.section,
                   COUNT(DISTINCT f.fine_id) AS total_fines,
                   SUM(f.amount) AS total_amount,
                   SUM(f.amount) - COALESCE(SUM(p.paid), 0) AS balance
            FROM students s
            JOIN fines f ON f.student_id = s.student_id
            LEFT JOIN (
                SELECT fine_id, SUM(amount_paid) AS paid
                FROM payments
                GROUP BY fine_id
            ) p ON p.fine_id = f.fine_id
            WHERE f.status <> 'WAIVED'
            GROUP BY s.student_id, s.full_name, s.grade_level, s.section
            HAVING balance > 0
            ORDER BY balance DESC, s.full_name
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def balance_by_grade():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.grade_level,
                   COUNT(DISTINCT s.student_id) AS students,
                   COUNT(DISTINCT f.fine_id) AS fines,
                   SUM(f.amount) - COALESCE(SUM(p.paid), 0) AS balance
            FROM students s
            JOIN fines f ON f.student_id = s.student_id
            LEFT JOIN (
                SELECT fine_id, SUM(amount_paid) AS paid
                FROM payments
                GROUP BY fine_id
            ) p ON p.fine_id = f.fine_id
            WHERE f.status <> 'WAIVED'
            GROUP BY s.grade_level
            HAVING balance > 0
            ORDER BY balance DESC
            """
        )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
