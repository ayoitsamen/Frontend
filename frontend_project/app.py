import requests
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from firebase_admin import auth, firestore, storage
from firebase_config import db  # Ensure Firebase Admin SDK initializes correctly

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey'  # Needed for session handling

# Initialize Firebase Storage
bucket = storage.bucket("your-firebase-storage-bucket-name")  # Replace with your Firebase Storage bucket name

# 🚀 Fetch Live Transport News from NewsData.io (Now with images)
def fetch_transport_news():
    api_key = "YOUR_API_KEY_HERE"  # 🔹 Replace with your real API key
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q=transport&country=gb"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get("results", [])

            # Ensure each article has an image; if not, use a default placeholder
            for article in articles:
                if "image_url" not in article or not article["image_url"]:
                    article["image_url"] = "/static/images/default_news.jpg"  # Default image placeholder

            return articles  # Return modified articles with images
        else:
            return []
    except Exception as e:
        return []

# 🚀 Landing Page (Auto-Redirects to Login)
@app.route('/')
def landing():
    return render_template('landing.html')

# 🚀 Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.get_user_by_email(email)
            user_doc = db.collection("users").document(user.uid).get()

            if not user_doc.exists:
                flash("❌ User does not exist!", "error")
                return redirect(url_for('login'))

            session['user_id'] = user.uid
            session['user_email'] = email
            flash("✅ Login Successful!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"❌ Login Failed: {str(e)}", "error")

    return render_template('login.html')

# 🚀 Sign Up Page (Now with Email Verification)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            # Create user in Firebase Authentication
            user = auth.create_user(email=email, password=password, display_name=name)

            # Store user data in Firestore
            db.collection("Sign up").document(user.uid).set({
                "Name": name,
                "Email": email,
                "CreatedAt": firestore.SERVER_TIMESTAMP
            })

            # Send Email Verification
            link = auth.generate_email_verification_link(email)
            send_verification_email(email, link)

            flash("✅ We have sent an email. Please verify before logging in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"❌ Sign Up Failed: {str(e)}", "error")

    return render_template('signup.html')

# 🚀 Function to Send Email Verification
def send_verification_email(email, link):
    try:
        # You can use an email-sending service like SendGrid, SMTP, etc.
        print(f"📩 Email Sent to {email}, Verification Link: {link}")
        # TODO: Replace this with an actual email service
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

# 🚀 Home Page
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# 🚀 Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        incidents = [doc.to_dict() for doc in db.collection('incidents').stream()]
        return render_template('admin_dashboard.html', incidents=incidents)
    except Exception as e:
        flash(f"Error fetching reports: {str(e)}", 'error')
        return redirect(url_for('home'))

# 🚀 Live Updates Page (TfL API + Transport News)
@app.route('/updates')
def updates():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tfl_updates = fetch_tfl_updates()  # Fetch TfL service updates
    transport_news = fetch_transport_news()  # Fetch live transport news

    return render_template('updates.html', tfl_updates=tfl_updates, transport_news=transport_news)

# 🚀 Fetch TfL Live Updates
def fetch_tfl_updates():
    url = "https://api.tfl.gov.uk/Line/Mode/tube,overground,dlr,tram/Status"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

# 🚀 API Route for Fetching TfL Updates
@app.route('/get_tfl_updates')
def get_tfl_updates():
    return jsonify(fetch_tfl_updates())

# 🚀 API Route for Fetching Transport News (AJAX Calls)
@app.route('/get_transport_news')
def get_transport_news():
    return jsonify(fetch_transport_news())

# 🚀 Report Incident Page
@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('report.html')

# 🚀 Handle Incident Submission
@app.route('/submit_incident', methods=['POST'])
def submit_incident():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Get form data
        user = session.get('user_email')  # Use the logged-in user's email
        description = request.form.get("description")
        location = request.form.get("location")
        ai_result = request.form.get("ai_result")
        confidence = request.form.get("confidence")
        image = request.files.get("image")

        # Save image to Firebase Storage
        if image:
            blob = bucket.blob(f"incidents/{image.filename}")
            blob.upload_from_file(image)
            image_url = blob.public_url
        else:
            image_url = None

        # Save incident to Firestore
        incident = {
            "user": user,
            "description": description,
            "location": location,
            "ai_result": ai_result,
            "confidence": confidence,
            "image_url": image_url,
            "status": "Pending"  # Default status
        }
        db.collection('incidents').add(incident)

        return jsonify({"message": "Incident submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Contact Us Page
@app.route('/contact')
def contact():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('contact.html')

# 🚀 User Dashboard Page
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

# 🚀 Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('✅ You have been logged out.', 'info')
    return redirect(url_for('landing'))

# 🚀 Map API: Fetch Stations & Bus Stops for Postcode
@app.route('/get_stations', methods=['POST'])
def get_stations():
    data = request.json
    postcode = data.get('postcode')

    if not postcode:
        return jsonify({'error': 'No postcode provided'}), 400

    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={postcode}, London, UK"
        geo_data = requests.get(geo_url).json()

        if not geo_data:
            return jsonify({'error': 'Invalid postcode'}), 400

        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']

        train_url = f"https://nominatim.openstreetmap.org/search?format=json&q=train+station+near+{lat},{lon}&limit=3"
        train_stations = requests.get(train_url).json()

        bus_url = f"https://nominatim.openstreetmap.org/search?format=json&q=bus+stop+near+{lat},{lon}&limit=3"
        bus_stops = requests.get(bus_url).json()

        return jsonify({'stations': train_stations, 'bus_stops': bus_stops, 'lat': lat, 'lon': lon})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🚀 Contact Us - Handle Form Submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        data = request.json  # Get form data from frontend
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        if not name or not email or not message:
            return jsonify({"error": "All fields are required"}), 400

        # Save to Firestore under 'contact_messages'
        db.collection("contact_messages").add({
            "Name": name,
            "Email": email,
            "Message": message
        })

        return jsonify({"success": "Thank you for contacting us! We will get back to you soon."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Run Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)