import py_compile

py_compile.compile('fines_db.py', doraise=True)
py_compile.compile('fines_ledger.py', doraise=True)
py_compile.compile('main_fines.py', doraise=True)
print('OK')
