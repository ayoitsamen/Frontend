from flask import Flask, render_template, request, flash, redirect, url_for, session
from firebase_config import db, auth  # Import Firebase config
from firebase_admin import exceptions, firestore

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey'  # Required for flash messages and session management

# Home Page Route
@app.route('/')
def home():
    return render_template('index.html')

# User Login/Signup Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        action = request.form['action']

        try:
            if action == 'signup':  # Signup Logic
                auth.create_user(email=email, password=password)
                db.collection('users').document(email).set({'email': email})
                flash('Signup successful! You can now log in.', 'success')
                return redirect(url_for('login'))
            elif action == 'login':  # Login Logic
                user = auth.get_user_by_email(email)  # Check user exists
                session['user_logged_in'] = email
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
        except exceptions.FirebaseError as e:
            flash(f"Error: {str(e)}", 'error')

    return render_template('login.html')

# Report Incident Page Route
@app.route('/report')
def report():
    if 'user_logged_in' not in session:
        flash('You must log in to report an incident.', 'error')
        return redirect(url_for('login'))
    return render_template('report.html')

# Handle Incident Submission
@app.route('/submit', methods=['POST'])
def submit():
    if 'user_logged_in' not in session:
        flash('You must log in to submit an incident.', 'error')
        return redirect(url_for('login'))

    description = request.form['incident']
    try:
        # Add incident to Firestore
        db.collection('incidents').add({
            'description': description,
            'user': session['user_logged_in'],
            'status': 'Pending',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        flash('Incident reported successfully!', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
    return redirect(url_for('report'))

# Admin Login Page Route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Authenticate Admin
            user = auth.get_user_by_email(email)
            if email.endswith("@admin.com"):  # Ensure it's an admin email
                session['admin_logged_in'] = email
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('You are not authorized to access the admin dashboard.', 'error')
        except exceptions.FirebaseError:
            flash('Invalid admin credentials. Please try again.', 'error')

    return render_template('admin_login.html')

# Admin Dashboard Route
@app.route('/admin')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        flash('You must log in as admin to access this page.', 'error')
        return redirect(url_for('admin_login'))

    try:
        # Fetch data from Firestore
        newsletter_data = [doc.to_dict() for doc in db.collection('newsletter').stream()]
        incident_data = [doc.to_dict() for doc in db.collection('incidents').stream()]
        contact_data = [doc.to_dict() for doc in db.collection('contact').stream()]
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('home'))

    return render_template('admin.html', newsletter=newsletter_data, incidents=incident_data, contacts=contact_data)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
