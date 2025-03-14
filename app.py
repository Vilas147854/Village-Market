from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'myvillage123'  # Secret key for session management

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Language translations
TRANSLATIONS = {
    'en': {
        'title': 'Kugur Village Market',
        'add_listing': 'Add New Listing',
        'view_requests': 'View Requests',
        'search_placeholder': 'Search for a product...',
        'search_button': 'Search',
        'no_listings': 'No listings found. Add one or check requests!',
        'price': 'Price',
        'seller': 'Seller',
        'contact': 'Contact',
        'add_title': 'Add a New Listing',
        'form_title': 'Title',
        'description': 'Description',
        'form_price': 'Price',
        'form_seller': 'Seller Name',
        'form_contact': 'Contact (Phone/Email)',
        'upload_image': 'Upload Image (optional)',
        'submit': 'Submit',
        'back_to_home': 'Back to Home',
        'requests_title': 'Product Requests',
        'request_product': 'Request a Product',
        'request_placeholder': 'What do you need?',
        'requester': 'Your Name',
        'request_contact': 'Your Contact',
        'submit_request': 'Submit Request',
        'no_requests': 'No requests yet. Add one!',
        'requested_by': 'Requested by',
        'available_from': 'Available from',
        'i_have_this': 'I Have This!',
        'respond_title': 'Respond to Request',
        'back_to_requests': 'Back to Requests'
    },
    'kn': {
        'title': 'ಕುಗೂರ್ ಗ್ರಾಮ ಮಾರುಕಟ್ಟೆ',
        'add_listing': 'ಹೊಸ ಪಟ್ಟಿಯನ್ನು ಸೇರಿಸಿ',
        'view_requests': 'ವಿನಂತಿಗಳನ್ನು ವೀಕ್ಷಿಸಿ',
        'search_placeholder': 'ಉತ್ಪನ್ನವನ್ನು ಹುಡುಕಿ...',
        'search_button': 'ಹುಡುಕಾಟ',
        'no_listings': 'ಯಾವುದೇ ಪಟ್ಟಿಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಒಂದನ್ನು ಸೇರಿಸಿ ಅಥವಾ ವಿನಂತಿಗಳನ್ನು ಪರಿಶೀಲಿಸಿ!',
        'price': 'ಬೆಲೆ',
        'seller': 'ಮಾರಾಟಗಾರ',
        'contact': 'ಸಂಪರ್ಕ',
        'add_title': 'ಹೊಸ ಪಟ್ಟಿಯನ್ನು ಸೇರಿಸಿ',
        'form_title': 'ಶೀರ್ಷಿಕೆ',
        'description': 'ವಿವರಣೆ',
        'form_price': 'ಬೆಲೆ',
        'form_seller': 'ಮಾರಾಟಗಾರನ ಹೆಸರು',
        'form_contact': 'ಸಂಪರ್ಕ (ಫೋನ್/ಇಮೇಲ್)',
        'upload_image': 'ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (ಐಚ್ಛಿಕ)',
        'submit': 'ಸಲ್ಲಿಸಿ',
        'back_to_home': 'ಮುಖಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ',
        'requests_title': 'ಉತ್ಪನ್ನ ವಿನಂತಿಗಳು',
        'request_product': 'ಉತ್ಪನ್ನವನ್ನು ವಿನಂತಿಸಿ',
        'request_placeholder': 'ನಿಮಗೆ ಏನು ಬೇಕು?',
        'requester': 'ನಿಮ್ಮ ಹೆಸರು',
        'request_contact': 'ನಿಮ್ಮ ಸಂಪರ್ಕ',
        'submit_request': 'ವಿನಂತಿಯನ್ನು ಸಲ್ಲಿಸಿ',
        'no_requests': 'ಯಾವುದೇ ವಿನಂತಿಗಳಿಲ್ಲ. ಒಂದನ್ನು ಸೇರಿಸಿ!',
        'requested_by': 'ವಿನಂತಿಸಿದವರು',
        'available_from': 'ಲಭ್ಯವಿದೆ ಇವರಿಂದ',
        'i_have_this': 'ನನ್ನ ಬಳಿ ಇದೆ!',
        'respond_title': 'ವಿನಂತಿಗೆ ಪ್ರತಿಕ್ರಿಯಿಸಿ',
        'back_to_requests': 'ವಿನಂತಿಗಳಿಗೆ ಹಿಂತಿರುಗಿ'
    }
}

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Set up the SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Listings table with image column
    c.execute('''CREATE TABLE IF NOT EXISTS listings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT NOT NULL, 
                  description TEXT NOT NULL, 
                  price TEXT NOT NULL, 
                  seller TEXT NOT NULL, 
                  contact TEXT NOT NULL, 
                  image TEXT)''')
    # Requests table
    c.execute('''CREATE TABLE IF NOT EXISTS requests 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  product TEXT NOT NULL, 
                  requester TEXT NOT NULL, 
                  contact TEXT NOT NULL)''')
    # Responses table
    c.execute('''CREATE TABLE IF NOT EXISTS responses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  request_id INTEGER, 
                  seller TEXT NOT NULL, 
                  contact TEXT NOT NULL, 
                  FOREIGN KEY (request_id) REFERENCES requests(id))''')
    conn.commit()
    conn.close()

# Homepage with search and language selection
@app.route('/', methods=['GET', 'POST'])
def index():
    lang = session.get('language', 'en')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        if 'language' in request.form:
            session['language'] = request.form['language']
            lang = session['language']
        elif 'search' in request.form:
            search_query = request.form['search'].lower()
            c.execute("SELECT * FROM listings WHERE LOWER(title) LIKE ? OR LOWER(description) LIKE ?",
                      (f'%{search_query}%', f'%{search_query}%'))
    else:
        c.execute("SELECT * FROM listings")
    
    listings = c.fetchall()
    conn.close()
    return render_template('index.html', listings=listings, lang=lang, t=TRANSLATIONS[lang])

# Add a new listing
@app.route('/add', methods=['GET', 'POST'])
def add():
    lang = session.get('language', 'en')
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        seller = request.form['seller']
        contact = request.form['contact']
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"

        print("IMage Here",image_path)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO listings (title, description, price, seller, contact, image) VALUES (?, ?, ?, ?, ?, ?)",
                  (title, description, price, seller, contact, image_path))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html', lang=lang, t=TRANSLATIONS[lang])

# Product requests page
@app.route('/requests', methods=['GET', 'POST'])
def requests():
    lang = session.get('language', 'en')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        if 'language' in request.form:
            session['language'] = request.form['language']
            lang = session['language']
        else:
            product = request.form['product']
            requester = request.form['requester']
            contact = request.form['contact']
            c.execute("INSERT INTO requests (product, requester, contact) VALUES (?, ?, ?)",
                      (product, requester, contact))
            conn.commit()
    
    c.execute('''SELECT r.id, r.product, r.requester, r.contact, rs.seller, rs.contact 
                 FROM requests r 
                 LEFT JOIN responses rs ON r.id = rs.request_id''')
    requests_data = c.fetchall()
    conn.close()
    return render_template('requests.html', requests=requests_data, lang=lang, t=TRANSLATIONS[lang])

# Seller response to a request
@app.route('/respond/<int:request_id>', methods=['GET', 'POST'])
def respond(request_id):
    lang = session.get('language', 'en')
    if request.method == 'POST':
        if 'language' in request.form:
            session['language'] = request.form['language']
            lang = session['language']
        else:
            seller = request.form['seller']
            contact = request.form['contact']
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO responses (request_id, seller, contact) VALUES (?, ?, ?)",
                      (request_id, seller, contact))
            conn.commit()
            conn.close()
            return redirect(url_for('requests'))
    return render_template('request_response.html', request_id=request_id, lang=lang, t=TRANSLATIONS[lang])

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    init_db()
    app.run(debug=True)