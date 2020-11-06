import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    # open the connection to the database
    conn = sqlite3.connect('polar_bear_data.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select * from deployments")
    rows = cur.fetchall()
    conn.close()
    return render_template('index.html', rows=rows)

@app.route('/show/<deploy_id>')
def show(deploy_id):
    conn = sqlite3.connect('polar_bear_data.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # get results from statuses
    cur.execute("select * from statuses WHERE deployment_id =?", (deploy_id),)
    rows = cur.fetchall()
    #get results from deployments
    cur.execute("select * from deployments WHERE deploy_id =?", (deploy_id),)
    bear = cur.fetchall()
    conn.close()
    return render_template('show.html', rows=rows, bear=bear)