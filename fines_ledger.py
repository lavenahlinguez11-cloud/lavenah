# ===== PROBLEMA =====
# Kalat-kalat ang multa sa school (ID replacement, nasirang gamit, huling
# bayad, atbp.). Nasa notebook lang ang record kaya nawawala ang resibo,
# hindi natrack ang partial payment, at walang aging kung sino ang matagal
# nang may utang. Hindi rin malaman ng office kung magkano ang nakolekta.
#
# ===== SOLUSYON =====
# Ang balanse ay (amount - SUM(amount_paid)) mula sa SQL, kaya tama kahit
# partial ang bayad. May aging report (DATEDIFF), collection report per
# buwan at uri, top debtors, at waive na may dahilan.

from datetime import date, timedelta

import mysql.connector

import fines_db


def grab_required(msg):
    while True:
        v = input(msg).strip()
        if v == "":
            print("  * Hindi puwede blangko.")
            continue
        return v


def grab_optional(msg):
    return input(msg).strip()


def grab_integer(msg, minimum=1, default=None):
    while True:
        v = input(msg).strip()
        if v == "":
            if default is not None:
                return default
            print("  * Hindi puwede blangko.")
            continue
        try:
            val = int(v)
        except ValueError:
            print("  * Numero lang dapat.")
            continue
        if val < minimum:
            print(f"  * Dapat {minimum} pataas.")
            continue
        return val


def grab_peso(msg, default=None, minimum=0.01):
    while True:
        v = input(msg).strip()
        if v == "":
            if default is not None:
                return round(float(default), 2)
            print("  * Hindi puwede blangko.")
            continue
        try:
            val = float(v)
        except ValueError:
            print("  * Numero lang dapat.")
            continue
        if val < minimum:
            print(f"  * Dapat {minimum} pataas.")
            continue
        return round(val, 2)


def grab_date(msg, default=None):
    while True:
        v = input(msg).strip()
        if v == "":
            if default:
                return default
            print("  * Hindi puwede blangko.")
            continue
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            print("  * Mali ang petsa. Halimbawa: 2026-10-29")


def render_debtor_card(s):
    print("\n" + "="*44)
    print(f"  STUDENT ID : {s['student_id']}")
    print("="*44)
    print(f"  Buong Pangalan : {s['full_name']}")
    print(f"  Grade Level    : {s['grade_level']}")
    print(f"  Seksyon        : {s['section']}")
    print("="*44)


def render_fine_card(f):
    days = f.get('days_overdue')
    if days is None:
        note = ""
    elif days > 0:
        note = f"  (LATE ng {days} araw)"
    elif days < 0:
        note = f"  ({-days} araw pa bago ang due)"
    else:
        note = "  (Due ngayon)"
    print("\n" + "="*44)
    print(f"  FINE ID : {f['fine_id']}")
    print("="*44)
    print(f"  Estudyante   : [{f['student_id']}] {f['full_name']}")
    print(f"  Grade/Seksyon: {f['grade_level']} - {f['section']}")
    print(f"  Uri ng Multa : {f['type_name']}")
    print(f"  Deskripsyon  : {f['description'] or '---'}")
    print(f"  Halaga       : PHP {float(f['amount']):,.2f}")
    print(f"  Nabayaran    : PHP {float(f['paid']):,.2f}")
    print(f"  BALANSE      : PHP {float(f['balance']):,.2f}")
    print(f"  Petsa        : {f['date_issued']}")
    print(f"  Due Date     : {f['due_date']}{note}")
    print(f"  Kalagayan    : {f['status']}")
    print(f"  Nag-issue    : {f['issued_by']}")
    if f.get('remarks'):
        print(f"  Remarks      : {f['remarks']}")
    print("="*44)


def format_fine_line(r):
    return (
        f"  #{r['fine_id']} | [{r['student_id']}] {r['full_name']} | {r['type_name']} "
        f"| PHP {float(r['amount']):,.2f} | Bayad: {float(r['paid']):,.2f} "
        f"| Balanse: {float(r['balance']):,.2f} | Due: {r['due_date']} | {r['status']}"
    )


# STUDENTS
def enlist_debtor():
    print("\n--- MAGDAGDAG NG ESTUDYANTE ---")
    sid = grab_required("  Student ID: ").upper()
    try:
        exist = fines_db.find_student(sid)
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if exist:
        print("  [PAALALA] Nasa listahan na ang estudyanteng ito.")
        render_debtor_card(exist)
        return
    name = grab_required("  Buong Pangalan (Apelyido, Pangalan): ")
    grade = grab_required("  Grade Level (hal. Grade 10): ")
    section = grab_required("  Seksyon: ")
    try:
        fines_db.add_student(sid, name, grade, section)
        print("\n  [TAPOS NA] Naidagdag na ang estudyante.")
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")


# FINE TYPES
def define_penalty_type():
    print("\n--- MAGDAGDAG NG URI NG MULTA ---")
    name = grab_required("  Pangalan ng Uri (hal. ID Replacement): ")
    amount = grab_peso("  Default na Halaga (0 kung iba-iba): ", minimum=0.0)
    desc = grab_optional("  Deskripsyon (Enter kung wala): ")
    try:
        tid = fines_db.add_fine_type(name, amount, desc or None)
        print(f"\n  [TAPOS NA] Naidagdag na ang uri ng multa. Type ID: {tid}")
    except mysql.connector.Error as e:
        if "Duplicate entry" in str(e):
            print("  [PAALALA] May ganito nang uri ng multa.")
        else:
            print(f"  [MALI] {e}")


def show_penalty_types():
    try:
        charge_rows = fines_db.list_fine_types()
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not charge_rows:
        print("\n  Wala pang uri ng multa. Magdagdag sa [2].")
        return
    print("\n--- MGA URI NG MULTA ---")
    for r in charge_rows:
        print(
            f"  [{r['type_id']}] {r['type_name']} | Default: PHP {float(r['default_amount']):,.2f}"
            f" | {r['description'] or '---'}"
        )


# FINES
def create_charge():
    print("\n--- MAG-ISSUE NG MULTA ---")
    sid = grab_required("  Student ID: ").upper()
    try:
        s = fines_db.find_student(sid)
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not s:
        print("  [WALA] Hindi nasa listahan. Idagdag muna sa [1].")
        return
    render_debtor_card(s)

    try:
        types = fines_db.list_fine_types()
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not types:
        print("  [WALA] Wala pang uri ng multa. Magdagdag muna sa [2].")
        return
    print("\n  Mga Uri ng Multa:")
    for t in types:
        print(
            f"  [{t['type_id']}] {t['type_name']} "
            f"| Default: PHP {float(t['default_amount']):,.2f}"
        )

    tid = grab_integer("\n  Type ID: ")
    chosen = next((t for t in types if t['type_id'] == tid), None)
    if not chosen:
        print("  [WALA] Hindi valid ang Type ID.")
        return

    desc = grab_optional(f"  Deskripsyon (Enter = {chosen['type_name']}): ") or chosen['type_name']
    default_amt = float(chosen['default_amount'])
    amount = grab_peso(
        f"  Halaga (Enter = {default_amt:,.2f}): ",
        default=default_amt if default_amt > 0 else None,
    )
    issued = grab_date(
        "  Petsa ng multa (YYYY-MM-DD, Enter = ngayon): ",
        default=date.today().isoformat(),
    )
    due_default = (date.fromisoformat(issued) + timedelta(days=30)).isoformat()
    due = grab_date(f"  Due date (YYYY-MM-DD, Enter = {due_default}): ", default=due_default)
    issued_by = grab_required("  Sino ang nag-issue: ")
    remarks = grab_optional("  Remarks (Enter kung wala): ")

    try:
        fid = fines_db.issue_fine(
            sid, tid, desc, amount, issued, due, issued_by, remarks or None
        )
        print(f"\n  [TAPOS NA] Na-issue na ang multa. Fine ID: {fid}")
        render_fine_card(fines_db.find_fine(fid))
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")


def post_payment():
    print("\n--- MAG-RECORD NG BAYAD ---")
    fid = grab_integer("  Fine ID: ")
    try:
        f = fines_db.find_fine(fid)
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not f:
        print("  [WALA] Hindi matagpuan ang fine record.")
        return
    render_fine_card(f)

    if f['status'] == 'PAID':
        print("  [PAALALA] Bayad na ang multang ito.")
        return
    if f['status'] == 'WAIVED':
        print("  [PAALALA] Waived na ang multang ito. Hindi na pwedeng bayaran.")
        return

    balance = float(f['balance'])
    amount = grab_peso(f"  Halaga ng bayad (Enter = {balance:,.2f}): ", default=balance)
    pay_date = grab_date(
        "  Petsa ng bayad (YYYY-MM-DD, Enter = ngayon): ",
        default=date.today().isoformat(),
    )
    try:
        auto_receipt = fines_db.next_receipt_no(pay_date)
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    receipt = grab_optional(f"  Receipt No. (Enter = {auto_receipt}): ") or auto_receipt
    received_by = grab_required("  Sino ang tumanggap ng bayad: ")
    remarks = grab_optional("  Remarks (Enter kung wala): ")

    print("\n  --- KUMPIRMASYON NG BAYAD ---")
    print(f"  Fine ID   : #{fid} ({f['type_name']})")
    print(f"  Estudyante: {f['full_name']}")
    print(f"  Bayad     : PHP {amount:,.2f}")
    print(f"  Receipt   : {receipt}")
    confirm = input("  Kumpirmahin ang bayad? (oo/hindi): ").strip().lower()
    if confirm not in ("oo", "o", "yes", "y"):
        print("  Kinansela.")
        return

    try:
        result = fines_db.record_payment(
            fid, amount, pay_date, receipt, received_by, remarks or None
        )
        print(f"\n  [TAPOS NA] Natanggap na ang bayad. Receipt: {receipt}")
        print(f"  Bagong balanse : PHP {result['balance']:,.2f}")
        print(f"  Kalagayan      : {result['status']}")
        if result['status'] == 'PAID':
            print("  Bayad na po ang multa. Salamat!")
    except ValueError as e:
        print(f"  [HINDI PWEDE] {e}")
    except mysql.connector.Error as e:
        if "Duplicate entry" in str(e) or "receipt_no" in str(e):
            print("  [PAALALA] Gamit na ang receipt number na iyon. Iba ang ilagay.")
        else:
            print(f"  [MALI] {e}")


def show_debtor_ledger():
    print("\n--- MULTA AT BALANSE NG ESTUDYANTE ---")
    sid = grab_required("  Student ID: ").upper()
    try:
        s = fines_db.find_student(sid)
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not s:
        print("  [WALA] Hindi nasa listahan ang estudyante.")
        return
    render_debtor_card(s)
    try:
        charge_rows = fines_db.list_fines(sid)
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not charge_rows:
        print("\n  Wala pang multa ang estudyanteng ito.")
        return
    print("\n--- MGA MULTA ---")
    for r in charge_rows:
        print(format_fine_line(r))
    active = [r for r in charge_rows if r['status'] != 'WAIVED']
    waived = len(charge_rows) - len(active)
    total_amount = sum(float(r['amount']) for r in active)
    total_paid = sum(float(r['paid']) for r in active)
    total_balance = sum(float(r['balance']) for r in active)
    overdue = sum(1 for r in active if (r['days_overdue'] or 0) > 0 and float(r['balance']) > 0)
    print("\n" + "="*44)
    print(f"  Kabuuang Multa : PHP {total_amount:,.2f}")
    print(f"  Nabayaran      : PHP {total_paid:,.2f}")
    print(f"  BALANSE        : PHP {total_balance:,.2f}")
    print(f"  Overdue        : {overdue} item")
    if waived:
        print(f"  Waived         : {waived} item (hindi kasama sa balanse)")
    print("="*44)


def show_all_charges():
    try:
        charge_rows = fines_db.list_fines()
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not charge_rows:
        print("\n  Wala pang naitalang multa.")
        return
    print(f"\n--- LISTAHAN NG LAHAT NG MULTA ({len(charge_rows)}) ---")
    for r in charge_rows:
        print(format_fine_line(r))


# REPORTS
def show_aging_report():
    try:
        charge_rows = fines_db.overdue_accounts()
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not charge_rows:
        print("\n  Walang overdue na account. Magaling!")
        return
    print(f"\n--- OVERDUE / UNPAID ACCOUNTS ({len(charge_rows)}) ---")
    total = 0.0
    buckets = {}
    for r in charge_rows:
        balance = float(r['balance'])
        total += balance
        buckets[r['bucket']] = buckets.get(r['bucket'], 0.0) + balance
        print(
            f"  #{r['fine_id']} | [{r['student_id']}] {r['full_name']} "
            f"({r['grade_level']} - {r['section']}) | {r['type_name']} "
            f"| Balanse: PHP {balance:,.2f} | Due: {r['due_date']} "
            f"| Late: {r['days_overdue']} araw [{r['bucket']}]"
        )
    print("-" * 44)
    for bucket in ("1-30 araw", "31-60 araw", "61+ araw"):
        if bucket in buckets:
            print(f"  {bucket:<12}: PHP {buckets[bucket]:,.2f}")
    print(f"  KABUUANG BALANSE: PHP {total:,.2f}")
    print("-" * 44)


def show_collections():
    try:
        monthly = fines_db.collection_by_month()
        by_type = fines_db.collection_by_type()
        summary = fines_db.outstanding_summary()
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return

    print("\n--- COLLECTION REPORT ---")
    print(f"\n  Kabuuang Multa   : PHP {float(summary['total_fines']):,.2f}")
    print(f"  Nakolekta        : PHP {float(summary['total_paid']):,.2f}")
    print(f"  Natitirang Balanse: PHP {float(summary['total_balance']):,.2f}")

    if monthly:
        print("\n  --- Koleksyon per Buwan ---")
        for r in monthly:
            print(
                f"  {r['month']}: PHP {float(r['collected']):,.2f} "
                f"({r['payments']} bayad)"
            )
    else:
        print("\n  Wala pang bayad na naitala.")

    if by_type:
        print("\n  --- Koleksyon per Uri ng Multa ---")
        for r in by_type:
            print(
                f"  {r['type_name']}: PHP {float(r['collected']):,.2f} "
                f"({r['payments']} bayad)"
            )


def waive_charge():
    print("\n--- I-WAIVE ANG MULTA ---")
    fid = grab_integer("  Fine ID: ")
    try:
        f = fines_db.find_fine(fid)
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if not f:
        print("  [WALA] Hindi matagpuan ang fine record.")
        return
    render_fine_card(f)
    if f['status'] == 'PAID':
        print("  [PAALALA] Bayad na ang multang ito. Hindi na kailangang i-waive.")
        return
    if f['status'] == 'WAIVED':
        print("  [PAALALA] Waived na ang multang ito.")
        return
    print("  * Ang waive ay para sa may valid na dahilan (hal. maling issue,")
    print("    nawala ang resibo, o aprubado ng principal).")
    reason = grab_required("  Dahilan ng waive: ")
    confirm = input("  Kumpirmahin ang WAIVE? (oo/hindi): ").strip().lower()
    if confirm not in ("oo", "o", "yes", "y"):
        print("  Kinansela.")
        return
    try:
        fines_db.waive_fine(fid, reason)
        print("\n  [TAPOS NA] Na-waive na ang multa. Hindi na ito kasama sa balanse.")
    except ValueError as e:
        print(f"  [HINDI PWEDE] {e}")
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")


def show_top_balances():
    try:
        charge_rows = fines_db.top_debtors(10)
        grades = fines_db.balance_by_grade()
    except mysql.connector.Error as e:
        print(f"  [MALI] {e}")
        return
    if charge_rows:
        print(f"\n--- TOP DEBTORS ({len(charge_rows)}) ---")
        rank = 0
        for r in charge_rows:
            rank += 1
            print(
                f"  #{rank} [{r['student_id']}] {r['full_name']} "
                f"({r['grade_level']} - {r['section']}) | Multa: {r['total_fines']} "
                f"| Kabuuan: PHP {float(r['total_amount']):,.2f} "
                f"| BALANSE: PHP {float(r['balance']):,.2f}"
            )
    else:
        print("\n  Walang outstanding na balanse. Magaling!")

    if grades:
        print("\n--- BALANSE PER GRADE LEVEL ---")
        for r in grades:
            print(
                f"  {r['grade_level']}: PHP {float(r['balance']):,.2f} "
                f"({r['students']} estudyante, {r['fines']} multa)"
            )
