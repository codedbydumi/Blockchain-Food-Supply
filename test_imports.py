# test_imports.py
try:
    import flask
    print("✅ Flask - OK")
except ImportError as e:
    print("❌ Flask - FAILED:", e)

try:
    import flask_sqlalchemy
    print("✅ Flask-SQLAlchemy - OK")
except ImportError as e:
    print("❌ Flask-SQLAlchemy - FAILED:", e)

try:
    import flask_login
    print("✅ Flask-Login - OK")
except ImportError as e:
    print("❌ Flask-Login - FAILED:", e)

try:
    from Crypto.Hash import SHA256
    print("✅ pycryptodome - OK")
except ImportError as e:
    print("❌ pycryptodome - FAILED:", e)

try:
    import pandas
    print("✅ pandas - OK")
except ImportError as e:
    print("❌ pandas - FAILED:", e)

print("\n🎯 If all show 'OK', you're ready to run the app!")