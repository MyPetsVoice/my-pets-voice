from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/dailycare/health')
def health():
    return render_template('dailycare/health.html')

@app.route('/dailycare/routine')
def routine():
    return render_template('dailycare/routine.html')


if __name__=='__main__':
    app.run(debug=True, port=5001)