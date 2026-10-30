# School Fines & Penalty Management System

Kini nga sistema maoy ledger sa mga **multa** ug **bayad** sa eskuylahan. Ang
balanse gikompyut sa SQL isip `amount - SUM(amount_paid)`, busa tama kini bisan
partial ang bayad. Naa kini aging report, collection report matag bulan ug
matag klase sa multa, top debtors, ug waive nga naay rason.

## Unsa ang kinahanglan

- **Python 3.8 o mas bag-o**
- **XAMPP** (MySQL/MariaDB)
- **mysql-connector-python**

## 1) I-install ang MySQL connector

```powershell
pip install mysql-connector-python
```

## 2) Sugdi ang XAMPP

1. Ablihi ang **XAMPP Control Panel**.
2. Pindota ang **Start** tapad sa **MySQL**.
3. Siguroha nga **green** ang kolor sa MySQL.

## 3) I-import ang database

1. Ablihi ang `http://localhost/phpmyadmin`.
2. Pindota ang **Import** tab.
3. Pilia ang `schema_fines.sql` (naa sa sama nga folder).
4. Pindota ang **Go** o **Import**.
5. Siguroha nga makita ang `school_fines_db` sa lista sa wala.

> Ang schema adunay seed nga mga klase sa multa: ID Replacement, Lost/Damaged
> Property, Late Return of Property, Late Payment, Uniform/Grooming Violation,
> ug Others.

## 4) Koneksyon sa database

| Variable | Default |
| --- | --- |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `3306` |
| `DB_USER` | `root` |
| `DB_PASSWORD` | *(walay password)* |
| `DB_NAME` | `school_fines_db` |

Kung lahi ang setup:

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_USER = "root"
$env:DB_PASSWORD = ""
$env:DB_NAME = "school_fines_db"
```

## 5) Padagana ang sistema

```powershell
cd "C:\Users\suete\Documents\system for sale\lavenia=fines_student_fines_system"
python main_fines.py
```

> Kung ibalhin ang folder sa lain nga computer, ilisi ang `cd` path sa
> aktwal nga lokasyon sa folder.


Dapat makita nimo ang **"Koneksyon sa School Fines database ay OK na."**

## Mga file

| File | Tumong |
| --- | --- |
| `schema_fines.sql` | Naghimo sa `students`, `fine_types`, `fines`, `payments` |
| `fines_db.py` | SQL sa multa, bayad, balanse, aging, ug report |
| `fines_ledger.py` | Flow sa menu ug validation sa bayad |
| `main_fines.py` | Ang CLI menu |
| `test_compile.py` | Pagsusi kung walay syntax error |

## Menu

| Numero | Aksyon |
| --- | --- |
| `1` | Pagdugang og estudyante |
| `2` | Pagdugang og klase sa multa |
| `3` | Pag-issue og multa |
| `4` | Pag-record sa bayad (full o partial) |
| `5` | Tan-awa ang multa ug balanse sa estudyante |
| `6` | Listahan sa tanan nga multa |
| `7` | Unpaid / overdue accounts (aging) |
| `8` | Collection report (matag bulan / matag klase) |
| `9` | I-waive ang multa |
| `10` | Top debtors ug balanse matag grade level |
| `11` | Listahan sa klase sa multa |
| `0` | Gula |

## Unsaon paggamit

1. Pagdugang og estudyante (`1`).
2. Pagdugang o pagpili og klase sa multa (`2` / `11`).
3. Pag-issue og multa (`3`). Mahimo nimong gamiton ang default amount ug ang
   due date nga 30 ka adlaw gikan sa petsa sa multa.
4. Pag-record sa bayad (`4`). Mahimo nga **full** o **partial**.
5. Tan-awa ang balanse sa estudyante (`5`) ug ang aging (`7`).
6. Gamit ang `8` para sa report sa nakolekta, ug `10` para sa top debtors.

## Importante nga lagda sa kwarta

- Ang balanse: `amount - SUM(amount_paid)` — gi-compute sa SQL, dili sa kamot.
- **Dili mahimo ang sobrang bayad.** Mo-error kini kung labaw sa balanse.
- **Dili mahimo bayaran ang PAID o WAIVED** nga multa.
- Ang `receipt_no` unique — dili mahimo madoble ang resibo.
- Ang status: `UNPAID` → `PARTIAL` → `PAID`, ug `WAIVED`.
- Ang waive kinahanglan og rason ug kumpirmasyon.
- Ang waive wala nagapapas sa record; gibutang ra kini sa `WAIVED` ug wala na
  apil sa balanse.

## Giunsa pagtipig ang datos

Ang tanan naa sa MySQL sa `school_fines_db`:

- `students` — estudyante
- `fine_types` — klase sa multa ug default amount
- `fines` — matag multa, due date, status
- `payments` — matag bayad, resibo, petsa, ug kinsa ang nagdawat

## Troubleshooting

| Sayop / Mensahe | Solusyon |
| --- | --- |
| `Can't connect to MySQL server on 'localhost:3306'` | Wala nagdagan ang MySQL. Pindota ang **Start** sa XAMPP. |
| `Unknown database 'school_fines_db'` | Wala pa na-import ang `schema_fines.sql`. |
| `Table 'school_fines_db.fines' doesn't exist` | I-import pag-usab ang schema. |
| `Access denied for user 'root'@'localhost'` | I-set ang `DB_PASSWORD`. |
| `ModuleNotFoundError: No module named 'mysql'` | `pip install mysql-connector-python` |
| `Duplicate entry` sa receipt | Gamit na ang receipt number. Ilisi og laing numero. |
| `Sobra sa balanse` | Ang bayad labaw sa natitirang balanse. |
| `Bayad na ang multang ito` | `PAID` na ang multa; dili na kinahanglan magbayad. |
| `Waived na ang multang ito` | `WAIVED` na ang multa; dili na mahimo bayaran. |

## Backup sa datos

1. Adto sa phpMyAdmin.
2. Pilia ang `school_fines_db`.
3. **Export** → **Go**.
4. Tipigi ang `.sql` file.

## Sulayi ang code

```powershell
python test_compile.py
```

Dapat `OK` ang mogawas.
