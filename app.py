from flask import * 
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import os
app = Flask(__name__, static_folder='images') 
app.secret_key='asdsdfsdfs13sdf_df%&'
model = tf.keras.models.load_model('model/model.h5')
users = {
    "pulakkumarghosh2001@gmail.com": "Pulak@2001",
    "admin@infomaticae.com": "admin",
}

@app.route('/login', methods=['POST', 'GET'])
def login():
    if "username" in session:
        return redirect(url_for('main'))
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')
        print(username)
        print(users)
        print(username in users)
        if username in users:
            pass_org = users[username]
            print(pass_org)
            if pass_org == password:
                session['username'] = username
                return redirect(url_for('main'))
            else:
                return render_template('login.html', msg="Wrong Credentials !")
        else:
            return render_template('login.html', msg="Wrong Credentials !")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')  
def main():  
    print(session)
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", modelType=0) 

@app.route('/batch')
def batch(): 
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("batch.html")
  
@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        folder = 'images'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        f = request.files['file']
        f.save('images/'+f.filename)
        img_path = 'images/'+f.filename
        img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128, 3))
        img = tf.keras.preprocessing.image.img_to_array(img)
        img = img/255.
        img = np.expand_dims(img, axis=0)
        pred_value = model.predict(img)
        prediction = pred_value[0][0]
        print(pred_value)
        print(prediction)
        if prediction > 0.5:
            result = 'No Corrosion'
        else:
            result = 'Corrosion'
        return render_template("result2.html", name = f.filename, link=f.filename, severity=result, severite_score=float("{:.3f}".format(1-prediction)))  

@app.route('/folder', methods=['POST'])
def folder_upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        folder = 'images'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        files = request.files.getlist('folderfile')
        data = []
        for f in files:
            f.save('images/'+f.filename)
            img_path = 'images/'+f.filename
            img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128, 3))
            img = tf.keras.preprocessing.image.img_to_array(img)
            img = img/255.
            img = np.expand_dims(img, axis=0)
            pred_value = model.predict(img)
            prediction = pred_value[0][0]
            if prediction < 0.5:
                status = 'Corrosion'
            else:
                status = 'No Corrosion'
            temp = {
                'filename': f.filename,
                'prediction_value': float("{:.3f}".format(1-prediction)),
                'status': status
            } 
            data.append(temp)
        return render_template('folder.html', data=data)


if __name__ == '__main__':  
    app.run(host="0.0.0.0", port=5000,debug=True)