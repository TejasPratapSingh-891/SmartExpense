import os
from app import create_app

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f" SmartExpense Platform is running at:")
    print(f" http://127.0.0.1:{port}")
    print(f" Demo credentials: tejas@smartexpense.com / admin123")
    print(f"=======================================================\n")
    app.run(host='127.0.0.1', port=port, debug=True)
