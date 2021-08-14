from flask import *
import sqlite3, hashlib, os
app=Flask(__name__)
UPLOAD_FOLDER = 'static/database'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/')
def root():
    return render_template('index.html')
@app.route('/home',methods=["GET", "POST"])
def home():
    data=[]
    if request.method == "POST":
        name = request.form['name']
        keyword = request.form['keyword']
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("select * from apparatus where name like ?", ('%'+keyword+'%',))
            data = cur.fetchall()
        conn.close()
    return render_template('home.html',data=data)
if __name__=='__main__':
    app.run(debug=True)