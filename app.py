from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
from eth_account.messages import encode_defunct
from eth_account import Account

app = Flask(__name__)


def getDatabase():
    conn = sqlite3.connect("TesteDB.db")
    conn.row_factory = sqlite3.Row
    try:
        volunteers = conn.execute("SELECT * FROM volunteers").fetchall()
        voters = conn.execute("SELECT * FROM voters").fetchall()
    except Exception as e:
        print(e)
        createTable(conn)
        # getDatabase()
    finally:
        return conn


def createTable(conn):
    print("Calling createTable")
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS volunteers (
                    id integer PRIMARY KEY, 
                    name text NOT NULL, 
                    votes integer )''')

        c.execute('''CREATE TABLE IF NOT EXISTS voters ( 
                    id integer PRIMARY KEY, 
                    wallet text NOT NULL, 
                    date text NOT NULL, 
                    volunteer_id integer NOT NULL,
                    signature text NOT NULL,
                    FOREIGN KEY (volunteer_id) REFERENCES volunteers (id) )''')

    except Exception as e:
        print(e)


def verify_signature(message, signature, address):
    message = "Votes: "+message
    enc_message = encode_defunct(text=message)
    msg_address = Account.recover_message(enc_message, signature=signature)
    if msg_address.lower() == address.lower():
        print("Message Validated")
        return True
    else:
        print("Message NOT Validated")
        return False

@app.route("/", methods=['POST', 'GET'])
def vote():
    if request.method == 'GET':
        conn = getDatabase()
        volunteers = conn.execute(
            'SELECT * FROM volunteers ORDER BY name').fetchall()
        conn.close()
        msg = "Please choose the best volunteers"
        return render_template('vote.html', volunteers=volunteers, msg=msg)

    if request.method == 'POST':
        if request.form['button'] == "Vote":
            print("Calling Vote")
            try:
                ids = request.form.getlist('checkbox')
                walletAddress = request.form['wallet_Address']
                signature = request.form['signature'] 
                with sqlite3.connect("TesteDB.db") as con:
                    if verify_signature(",".join([str(item) for item in ids]), signature, walletAddress) is True:
                        cur = con.cursor()
                        idw = cur.execute(
                            "SELECT id from voters WHERE wallet=(?)", (walletAddress,)).fetchone()
                        if idw is None:
                            for id in ids:
                                cur.execute(
                                    "UPDATE volunteers SET votes=votes+1 WHERE name=(?)", (id,))
                            list = ",".join([str(item) for item in ids])
                            cur.execute("INSERT INTO voters (wallet, date, volunteer_id, signature) VALUES (?,?,?,?)", (
                                walletAddress, datetime.now(), list, signature))
                            con.commit()
                            msg = "Votes successfully computed " + '\U00002705' 
                        else:
                            msg = "User already voted " + '\U0000274c' 
                    else:
                        msg = "Unable to validate signature" + '\U0000274c' 
            except sqlite3.Error as er:
                print('SQLite error: %s' % (' '.join(er.args)))
                con.rollback()
                msg = "error in vote operation " + '\U0000274c' 
            finally:
                con.row_factory = sqlite3.Row
                volunteers = con.execute(
                    'SELECT * FROM volunteers ORDER BY name').fetchall()
                con.close()
                return render_template('vote.html', volunteers=volunteers, msg=msg)


@app.route("/adm/", methods=['POST', 'GET'])
def adm():
    if request.method == 'GET':
        conn = getDatabase()
        volunteers = conn.execute(
            'SELECT * FROM volunteers ORDER BY name').fetchall()
        conn.close()
        msg = "This should be accessed by admins only"
        return render_template('adm.html', volunteers=volunteers, msg=msg)

    if request.method == 'POST':
        if request.form['submit'] == "Insert":
            try:
                name = request.form['name']
                walletAddress = request.form['wallet_Address']
                print(name + " " + walletAddress)
                with sqlite3.connect("TesteDB.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO volunteers (name, votes) VALUES (?,?)", (name, 0))
                    con.commit()
                    msg = "Record successfully added"
            except sqlite3.Error as er:
                print('SQLite error: %s' % (' '.join(er.args)))
                con.rollback()
                msg = "Error in insert operation"
            finally:
                con.row_factory = sqlite3.Row
                volunteers = con.execute(
                    'SELECT * FROM volunteers ORDER BY name').fetchall()
                con.close()
                return render_template("adm.html", volunteers=volunteers, msg=msg)

        elif request.form['submit'] == "Delete":
            print("Callind delete")
            try:
                names = request.form.getlist('checkbox')
                with sqlite3.connect("TesteDB.db") as con:
                    cur = con.cursor()
                    for name in names:
                        cur.execute(
                            "DELETE FROM volunteers WHERE name=(?)", (name,))
                        con.commit()
                    msg = "Record successfully deleted"
            except sqlite3.Error as er:
                print('SQLite error: %s' % (' '.join(er.args)))
                con.rollback()
                msg = "Error in delete operation"
            finally:
                con.row_factory = sqlite3.Row
                volunteers = con.execute(
                    'SELECT * FROM volunteers ORDER BY name').fetchall()
                con.close()
                print(volunteers)
                return render_template("adm.html", volunteers=volunteers, msg=msg)

@app.route("/list/", methods=['POST', 'GET'])
def listvote():
    if request.method == 'GET':
        conn = getDatabase()
        voters = conn.execute('SELECT * FROM voters').fetchall()
        conn.close()
        return render_template("list.html", voters=voters)
