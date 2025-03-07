
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import logging
from mysql.connector import Error
import mysql.connector.pooling
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

# Database configuration with connection pooling
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sanjay@123.',
    'database': 'bookings'
}

# Connection pool setup
cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

# Function to establish a database connection
def get_db_connection():
    try:
        return cnxpool.get_connection()
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

# Register Route
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile_number = request.form['mobile_number']
        
        logging.debug(f"Registering user: {name}, {email}, {mobile_number}")

        connection = get_db_connection()
        if connection:
            logging.info("Database connection established.")
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email, password, mobile_number) VALUES (%s, %s, %s, %s)",
                               (name, email, password, mobile_number))
                connection.commit()
                flash("Thanks for registering!", "success")
                return redirect(url_for('login'))
            except mysql.connector.Error as err:
                logging.error(f"Error: {err}")
                flash(f"Error: {err}", "danger")
            finally:
                cursor.close()
                connection.close()
        else:
            logging.error("Database connection failed!")
            flash("Database connection failed!", "danger")
    
    return render_template('registration.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
                user = cursor.fetchone()

                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['name']
                    flash("Login successful!", "success")
                    return redirect(url_for('rooms'))
                else:
                    print("Invalid login. Please try again.", "danger")
            except mysql.connector.Error as err:
                flash(f"Error: {err}", "danger")
            finally:
                cursor.close()
                connection.close()
        else:
            flash("Database connection failed!", "danger")

    return render_template('login.html')

# Check Rooms Route
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if request.method == 'POST':
        room_type = request.form['room_type']
        return redirect(url_for('rooms'))
    
    return render_template('rooms.html')

# Thank You Route
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')
# Booking page
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        checkin_date = request.form['checkin_date']
        checkout_date = request.form['checkout_date']
        adults = request.form['adults']
        children = request.form['children']
        message = request.form['message']

        connection = get_db_connection()
        if not connection:
            return "Database connection failed", 500

        cursor = connection.cursor()
        query = """
            INSERT INTO booking (guest_name, phone_number, email, checkin_date, checkout_date, adults, children, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (name, phone, email, checkin_date, checkout_date, adults, children, message)

        try:
            cursor.execute(query, values)
            connection.commit()
            flash("Booking successful")
        except mysql.connector.Error as e:
            logging.error(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('thank_you'))
    
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)