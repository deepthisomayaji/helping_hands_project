from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Create tables if not exists
def create_tables():
    conn = sqlite3.connect('helping_hands.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT,
            skills TEXT,
            preferences TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assistance (
            assistance_id INTEGER PRIMARY KEY,
            task_description TEXT,
            date TEXT,
            time TEXT,
            status TEXT,
            assigned_employee_id INTEGER,
            FOREIGN KEY (assigned_employee_id) REFERENCES employees(employee_id)
        )
    ''')

    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def index():
    conn = sqlite3.connect('helping_hands.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM assistance')
    assistance_data = cursor.fetchall()
    
    cursor.execute('SELECT * FROM employees')
    employee_data = cursor.fetchall()

    conn.close()

    return render_template('index.html', assistance_data=assistance_data, employee_data=employee_data)

@app.route('/offer_assistance', methods=['POST'])
def offer_assistance():
    if request.method == 'POST':
        task_description = request.form['task_description']
        date = request.form['date']
        time = request.form['time']

        conn = sqlite3.connect('helping_hands.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO assistance (task_description, date, time, status)
            VALUES (?, ?, ?, ?)
        ''', (task_description, date, time, 'pending'))

        conn.commit()
        conn.close()
    return redirect(url_for('offer_assistance'))
    # return redirect(url_for('index'))
      
           

if __name__ == '__main__':
    app.run(debug=True)
