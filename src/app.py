from flask import request, Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('main_page.html')

port = int(os.getenv("PORT", 5000))
if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port = port)