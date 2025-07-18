import os
from flask import Flask, request, send_file, render_template_string, render_template, redirect, flash
from werkzeug.utils import secure_filename
from credit_dispute_generator import EnhancedCreditDisputeGenerator
from email_utils import send_email_with_attachments

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpg', 'jpeg', 'png'}

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_change_this')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email configuration from environment variables
SMTP_USER = os.environ.get('SMTP_USER', 'movementcredit251@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'hbormbcjsaolnyik')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/comprehensive')
def comprehensive():
    """Route for the new comprehensive AI-powered interface"""
    return render_template('comprehensive.html')

@app.route('/generate_comprehensive_dispute', methods=['POST'])
def generate_comprehensive_dispute():
    """Handle form submission from the comprehensive interface"""
    user_data = {
        'full_name': request.form.get('full_name', ''),
        'street_address': request.form.get('street_address', ''),
        'city': request.form.get('city', ''),
        'state': request.form.get('state', ''),
        'zip_code': request.form.get('zip_code', ''),
        'ssn_last4': request.form.get('ssn_last4', ''),
        'dob': request.form.get('dob', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
    }

    # Handle file uploads
    files_saved = {}
    for file_key in ['credit_report', 'government_id', 'utility_bill', 'ftc_identity_theft_report', 'police_report']:
        uploaded_file = request.files.get(file_key)
        if uploaded_file and uploaded_file.filename and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            files_saved[file_key] = file_path

    # Process credit report if uploaded
    if 'credit_report' in files_saved:
        credit_report_path = files_saved['credit_report']
        
        # Extract text from PDF or TXT
        if credit_report_path.lower().endswith('.pdf'):
            import PyPDF2
            with open(credit_report_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                report_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            with open(credit_report_path, 'r', encoding='utf-8') as f:
                report_text = f.read()

        # Generate dispute letters using your AI parser
        try:
            from advanced_credit_parser import process_3bureau_report
            user_address = f"{user_data['street_address']}, {user_data['city']}, {user_data['state']} {user_data['zip_code']}"
            derogatory_items, dispute_letters = process_3bureau_report(report_text, user_data['full_name'], user_address)
            
            # Also generate using existing generator
            generator = EnhancedCreditDisputeGenerator(user_data)
            generated_files = generator.generate_3bureau_dispute_letters_from_report(report_text)

            # Filter valid files
            valid_files = [f for f in generated_files if os.path.exists(f) and os.path.getsize(f) > 0]

            # Send email
            if user_data['email']:
                try:
                    send_email_with_attachments(
                        smtp_server='smtp.gmail.com',
                        smtp_port=465,
                        smtp_user=SMTP_USER,
                        smtp_password=SMTP_PASSWORD,
                        sender_email=SMTP_USER,
                        recipient_email=user_data['email'],
                        subject='Your AI-Generated Credit Dispute Package',
                        body=f'Your complete dispute package has been generated using our AI analysis. Found {len(derogatory_items)} items to dispute.',
                        attachment_paths=valid_files
                    )
                    flash(f"✅ Success! Found {len(derogatory_items)} items and generated {len(valid_files)} dispute letters. Check your email!", "success")
                except Exception as e:
                    flash(f"❌ Error sending email: {e}", "error")
            
            # Clean up files
            for f in valid_files:
                try:
                    os.remove(f)
                except:
                    pass
                    
        except Exception as e:
            flash(f"❌ Error processing credit report: {e}", "error")
    else:
        flash("❌ Please upload a credit report", "error")

    return redirect('/comprehensive')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_data = {
            'full_name': request.form.get('full_name', ''),
            'street_address': request.form.get('street_address', ''),
            'city': request.form.get('city', ''),
            'state': request.form.get('state', ''),
            'zip_code': request.form.get('zip_code', ''),
            'ssn_last4': request.form.get('ssn_last4', ''),
            'dob': request.form.get('dob', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
        }

        # Save license and proof of address if uploaded
        license_file = request.files.get('license')
        proof_file = request.files.get('proof_of_address')
        if license_file and allowed_file(license_file.filename):
            license_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(license_file.filename))
            license_file.save(license_path)
            user_data['license_path'] =
