from flask import Flask, request, url_for, session, redirect, render_template
from flaskext.mysql import MySQL
from flask_oauth import OAuth
import logging
import time
from logging.handlers import RotatingFileHandler

oauth = OAuth()
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'tst'
app.config['MYSQL_DATABASE_HOST'] = '172.24.0.2'
app.config['MYSQL_DATABASE_PORT'] = 3306

app.secret_key = 'secretkey'

mysql.init_app(app)
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key='915492308190-t6vq51h87c5lf0kkdgrv130ijk7dhk1j.apps.googleusercontent.com',
                          consumer_secret='vli5knwxYjMFSeF0KPO9BefE')

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route('/authorized')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('landing'))

@app.route('/')
def landing():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S') + ' akses landing page')
    return render_template('index.html')

@app.route('/addresource')
def add_resource():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S') + ' akses add resource page')
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    return render_template('new.html')

@app.route('/deleteresource')
def del_resource():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S') + ' akses delete resource page')
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    return render_template('delete.html')

@app.route('/editresource')
def editresource():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S') + ' akses edit resource page')
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    return render_template('edit.html')

# get all resources
@app.route('/resources', methods=['GET'])
def get_resources():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM resources'
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    result_baru = []
    for resource in result:
        the_resource = {
            'id': resource[0],
            'name': resource[1],
            'category': resource[2],
            'desc': resource[3],
            'location': resource[4]
        }
        result_baru.append(the_resource)

    return {'resources': result_baru}

# get specific resource
@app.route('/resources/<string:id>', methods=['GET'])
def get_spec_resources(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM resources WHERE id = %s'
    cursor.execute(query,id)
    result = cursor.fetchall()
    conn.close()

    result_baru = []
    for resource in result:
        the_resource = {
            'id': resource[0],
            'name': resource[1],
            'category': resource[2],
            'desc': resource[3],
            'location': resource[4]
        }
        result_baru.append(the_resource)

    return {'resource': result_baru}

# create new resource
@app.route('/new-resource', methods=['POST'])
def insert_resource():
    conn = mysql.connect()
    cursor = conn.cursor()
    
    name = request.form['name']
    category = request.form['category']
    desc = request.form['description']
    location = request.form['location']

    query = 'INSERT INTO resources (name, category, description, location) VALUES (%s, %s, %s, %s)'
    data = (name, category, desc, location)

    cursor.execute(query,data)
    conn.commit()
    conn.close()

    result = {
        'name': name,
        'category': category,
        'desc': desc,
        'location': location
    }

    return {'added': result}

# delete resource
@app.route('/delete-resource/<string:id>', methods=['DELETE'])
def delete_resource(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = 'SELECT * FROM resources WHERE id = %s'
    cursor.execute(query,id)
    result = cursor.fetchall()

    query = 'DELETE FROM resources WHERE id = %s'
    cursor.execute(query,id)
    conn.commit()
    conn.close()

    result_baru = []
    for resource in result:
        the_resource = {
            'id': resource[0],
            'name': resource[1],
            'category': resource[2],
            'desc': resource[3],
            'location': resource[4]
        }
        result_baru.append(the_resource)

    return {'deleted': result_baru}

# edit existing resource
@app.route('/edit-resource/<string:id>', methods=['PUT'])
def edit_resource(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    
    name = request.form['name']
    category = request.form['category']
    desc = request.form['description']
    location = request.form['location']

    query = 'UPDATE resources SET name = %s, category = %s, description = %s, location = %s WHERE id = %s'
    data = (name, category, desc, location, id)

    cursor.execute(query,data)
    conn.commit()
    conn.close()

    result = {
        'name': name,
        'category': category,
        'desc': desc,
        'location': location
    }

    return {'edited': result}

if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')
