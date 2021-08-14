from flask import *
import numpy as np
import sqlite3, hashlib, os,re,time
import face_recognition
import imutils
import pickle
import time
import cv2


# from bs4 import BeautifulSoup
# import requests, re,urllib2, os, cookielib,json,shutil,glob

app=Flask(__name__)
app.config["CACHE_TYPE"] = "null"

app.secret_key = 'random string'
# def detectPhishing(url):
#     testUrl=pd.DataFrame(url,columns=['url'])
#     seperation_of_protocol = testUrl['url'].str.split("://",expand = True)
#     seperation_domain_name = seperation_of_protocol[1].str.split("/",1,expand = True)

def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'username' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE matric_number = '" + session['username'] + "'")
            userId, firstName = cur.fetchone()
    conn.close()
    return (loggedIn, firstName)
@app.route('/')
def root():
    loggedIn, firstName = getLoginDetails()
    return render_template('index.html',loggedIn=loggedIn,firstName=firstName)
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('root'))

    return render_template('index.html')

def is_valid(username, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT matric_number, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == username and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False
@app.route("/registration")
def registrationForm():
    return render_template("register.html")
@app.route("/loginForm")
def loginForm():
    if 'username' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_valid(username, password):
            matric=recognise()
            if(matric==username):
                session['username'] = username
                return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)
@app.route("/botnet")
def botnet():
    return render_template('botnet.html')
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName) VALUES (?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)
def recognise():

    #find path of xml file containing haarcascade file 
    cascPathface = os.path.dirname(
    cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())
    
    print("Streaming started")
    video_capture = cv2.VideoCapture(0)
    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,
                                            scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(60, 60),
                                            flags=cv2.CASCADE_SCALE_IMAGE)
    
        # convert the input frame from BGR to RGB 
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []
        # loop over the facial embeddings incase
        # we have multiple embeddings for multiple fcaes
        for encoding in encodings:
        #Compare encodings with encodings in data["encodings"]
        #Matches contain array with boolean values and True for the embeddings it matches closely
        #and False for rest
            matches = face_recognition.compare_faces(data["encodings"],
            encoding)
            #set name =inknown if no encoding matches
            name = "Unknown"
            # check to see if we have found a match
            if True in matches:
                #Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    #Check the names at respective indexes we stored in matchedIdxs
                    name = data["names"][i]
                    #increase count for the name we got
                    counts[name] = counts.get(name, 0) + 1
                #set name which has highest count
                name = max(counts, key=counts.get)
    
    
            # update the list of names
            names.append(name)
            # loop over the recognized faces
            for ((x, y, w, h), name) in zip(faces, names):
                # rescale the face coordinates
                # draw the predicted face name on the image
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()
    return names[0]

if __name__=='__main__':
    app.run(debug=True)
