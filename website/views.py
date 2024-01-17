from flask import Blueprint, render_template, request, send_file, session, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
import os
import paypalrestsdk
from werkzeug.utils import secure_filename
from docx import Document
import pytz
from . import db
from .wordFileProc_final import fixDocGrammar
views = Blueprint('views', __name__)

# Set the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'docx'}

# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to check if the user can upload based on the last upload time
def can_upload(user):
    last_upload_time = user.last_upload_time
    
    if last_upload_time is None:
        return True
    if user.subscription:
        return True

    last_upload_time = last_upload_time.replace(tzinfo=pytz.FixedOffset(420)) if last_upload_time is not None else None

    current_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    elapsed_time = current_time - last_upload_time if last_upload_time is not None else timedelta(0)
    remaining_time = timedelta(hours=1) - elapsed_time if elapsed_time is not None else timedelta(0)
    
    return remaining_time <= timedelta(0)



 

# Function to modify the content of the DOCX file
def modify_docx_content(file_path):
    doc = Document(file_path)

    # Start fixing grammar in docx file
    if fixDocGrammar(doc):  # successfully
        # Save the modified document
        modified_file_path = file_path.replace('.docx', '_modified.docx')
        doc.save(modified_file_path)
        return modified_file_path
    else:
        print("Error during the doc file processing!!!")
        return None



@views.route('/')
@login_required
def home():
    remaining_time = session.get('remaining_time')
    if not can_upload(current_user):
        last_upload_time = current_user.last_upload_time
        
        last_upload_time = last_upload_time.replace(tzinfo=pytz.FixedOffset(420))     # Convert to the correct timezone
        remaining_time = (last_upload_time + timedelta(hours=1) - datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')))

    return render_template('home.html', remaining_time=remaining_time, user = current_user)

@views.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if not can_upload(current_user):
        last_upload_time = current_user.last_upload_time
        
        last_upload_time = last_upload_time.replace(tzinfo=pytz.FixedOffset(420))
        remaining_time = last_upload_time + timedelta(hours=1) - datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        return render_template('home.html', error='You can only upload one file per hour.', user = current_user, remaining_time=remaining_time )
    # Rest of the code...

    # Check if the post request has the file part
    if 'file' not in request.files:
        return render_template('home.html', error='No file part', user = current_user)

    file = request.files['file']

    # If the user submits an empty form
    if file.filename == '':
        return render_template('home.html', error='No selected file', user = current_user)

    # If the file is valid
    if file and allowed_file(file.filename):
        # Save the file to the upload folder
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Modify the content of the uploaded file
        modified_file_path = modify_docx_content(file_path)

        # Update the last upload time in the session
        current_user.last_upload_time = datetime.now()
        db.session.commit()

        return render_template('home.html', success='File uploaded and modified successfully', filename=filename, modified_filename=os.path.basename(modified_file_path), user=current_user)

    # If the file is not valid
    return render_template('home.html', error='Invalid file type', user = current_user)

@views.route('/download/<filename>')
def download_file(filename):
    # Return the modified file to the user for download
    modified_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.replace('.docx', '_modified.docx'))
    return send_file(modified_file_path, as_attachment=True)

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AZf6k6vTzLcBwrCTwk6-eYfc_C9urIX6Q8jBMe0WoT5-Rrbtj_s-kRrsLg8X1ee_vzk9McT9Tu5EMSFi",
  "client_secret": "EF310QfcEBoV-VsC5bh0CyGO4RB9jQww_CTEgcxSkCW48uS79sdJu6DRTOSFKqLMGYwYxO0u5RWjGTif" 
  })

@views.route('/premium')
@login_required
def index():
    return render_template('premium.html', user = current_user)

@views.route('/payment', methods=['POST'])
def payment():

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "sku": "12345",
                    "price": "10.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "10.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        current_user.subscription = True
        db.session.commit()
        
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})

@views.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    return jsonify({'success' : success})
