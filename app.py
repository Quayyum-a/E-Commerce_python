from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app, origins=["http://127.0.0.1:5500/index.html", "http://localhost:5500"], supports_credentials=True)

if __name__ == '__main__':
    app.run(debug=True)
