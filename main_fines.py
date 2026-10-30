# ===== PROBLEMA =====
# Kalat-kalat ang multa sa school (ID replacement, nasirang gamit, huling
# bayad, atbp.). Nasa notebook lang ang record kaya nawawala ang resibo,
# hindi natrack ang partial payment, at walang aging kung sino ang matagal
# nang may utang. Hindi rin malaman ng office kung magkano ang nakolekta.
#
# ===== SOLUSYON =====
# CLI system na may fines at payments ledger, live balance, aging report,
# collection report, top debtors, at waive. Bawal ang sobrang bayad, at may
# resibo ang bawat transaksyon.
import fines_db
import fines_ledger


def fines_menu():
    print("\n" + "="*56)
    print("        SCHOOL FINES & PENALTY MANAGEMENT SYSTEM")
    print("="*56)
    print("  [1] Magdagdag ng Estudyante")
    print("  [2] Magdagdag ng Uri ng Multa")
    print("  [3] Mag-issue ng Multa")
    print("  [4] Mag-record ng Bayad (Full o Partial)")
    print("  [5] Tingnan ang Multa/Balanse ng Estudyante")
    print("  [6] Listahan ng Lahat ng Multa")
    print("  [7] Unpaid / Overdue Accounts (Aging)")
    print("  [8] Collection Report (per Buwan / per Uri)")
    print("  [9] I-waive ang Multa")
    print("  [10] Top Debtors at Balanse per Grade Level")
    print("  [11] Listahan ng Uri ng Multa")
    print("  [0] Lumabas")
    print("="*56)


def fines_cli():
    ok, msg = fines_db.test_connection()
    print(f"\n  {msg}")
    if not ok:
        print("  Paki-import muna ang 'schema_fines.sql' sa XAMPP/MySQL.")
        return
    while True:
        fines_menu()
        ch = input("\n  Ano'ng aksyon ang gagawin? : ").strip()
        if ch == "1":
            fines_ledger.enlist_debtor()
        elif ch == "2":
            fines_ledger.define_penalty_type()
        elif ch == "3":
            fines_ledger.create_charge()
        elif ch == "4":
            fines_ledger.post_payment()
        elif ch == "5":
            fines_ledger.show_debtor_ledger()
        elif ch == "6":
            fines_ledger.show_all_charges()
        elif ch == "7":
            fines_ledger.show_aging_report()
        elif ch == "8":
            fines_ledger.show_collections()
        elif ch == "9":
            fines_ledger.waive_charge()
        elif ch == "10":
            fines_ledger.show_top_balances()
        elif ch == "11":
            fines_ledger.show_penalty_types()
        elif ch == "0":
            print("\n  Sige, paalam! Bayaran ang tamang multa.")
            break
        else:
            print("\n  * Hindi tamang pagpili.")


if __name__ == "__main__":
    fines_cli()
