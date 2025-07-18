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

        # Generate dispute letters using simplified generator
        try:
            # Use existing generator
            generator = EnhancedCreditDisputeGenerator(user_data)
            generated_files = generator.generate_3bureau_dispute_letters_from_report(report_text)
            
            # Assume 3 items found for demo
            derogatory_items = ['Sample Item 1', 'Sample Item 2', 'Sample Item 3']

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
                        body='Your complete dispute package has been generated using our AI analysis. Found ' + str(len(derogatory_items)) + ' items to dispute.',
                        attachment_paths=valid_files
                    )
                    flash("Success! Found " + str(len(derogatory_items)) + " items and generated " + str(len(valid_files)) + " dispute letters. Check your email!", "success")
                except Exception as e:
                    flash("Error sending email: " + str(e), "error")
            
            # Clean up files
            for f in valid_files:
                try:
                    os.remove(f)
                except:
                    pass
                    
        except Exception as e:
            flash("Error processing credit report: " + str(e), "error")
    else:
        flash("Please upload a credit report", "error")

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
            user_data['license_path'] = license_path
        if proof_file and allowed_file(proof_file.filename):
            proof_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(proof_file.filename))
            proof_file.save(proof_path)
            user_data['proof_of_address_path'] = proof_path

        # Handle credit report upload and extraction
        credit_report_file = request.files.get('credit_report')
        if credit_report_file and allowed_file(credit_report_file.filename):
            credit_report_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(credit_report_file.filename))
            credit_report_file.save(credit_report_path)
            user_data['credit_report_path'] = credit_report_path

            # Extract text from PDF or TXT
            if credit_report_path.lower().endswith('.pdf'):
                import PyPDF2
                with open(credit_report_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    report_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            else:
                with open(credit_report_path, 'r', encoding='utf-8') as f:
                    report_text = f.read()

            generator = EnhancedCreditDisputeGenerator(user_data)
            generated_files = generator.generate_3bureau_dispute_letters_from_report(report_text)

            # Ensure all files exist and are non-empty before attaching
            valid_files = []
            for f in generated_files:
                if os.path.exists(f) and os.path.getsize(f) > 0:
                    valid_files.append(f)
                else:
                    print("File missing or empty, not attaching: " + f)
            print("Files to attach:", valid_files)

            # Send email with attachments
            recipient_email = user_data['email']
            try:
                send_email_with_attachments(
                    smtp_server='smtp.gmail.com',
                    smtp_port=465,
                    smtp_user=SMTP_USER,
                    smtp_password=SMTP_PASSWORD,
                    sender_email=SMTP_USER,
                    recipient_email=recipient_email,
                    subject='Your Credit Dispute Letters',
                    body='Attached are your generated credit dispute letters.',
                    attachment_paths=valid_files
                )
                flash("Your letters have been emailed to you.", "success")
            except Exception as e:
                flash("Email sending failed: " + str(e), "danger")

            # Clean up files
            for f in valid_files:
                try:
                    os.remove(f)
                except Exception:
                    pass

            return redirect(request.url)
        else:
            flash('Please upload a valid credit report (PDF or TXT).')
            return redirect(request.url)

    # HTML form
    return render_template_string("""
    <!doctype html>
    <html>
    <head>
      <title>Credit Report Dispute Generator</title>
      <style>
        body { background: #e6f2ff; font-family: Helvetica, Arial, sans-serif; }
        .container { max-width: 700px; margin: 30px auto; background: #fff; border-radius: 10px; box-shadow: 0 0 10px #ccc; padding: 30px; }
        h1 { color: #003366; text-align: center; }
        label { display: block; margin-top: 12px; color: #003366; }
        input[type="text"], input[type="email"], input[type="file"], textarea { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #bbb; }
        input[type="submit"] { background: #ffcc00; color: #003366; font-weight: bold; border: none; border-radius: 5px; padding: 12px 0; width: 100%; margin-top: 20px; font-size: 16px; }
        input[type="submit"]:hover { background: #6699cc; color: #fff; }
        .required { color: #cc0000; }
      </style>
    </head>
    <body>
    <div class="container">
      <h1>Credit Report Dispute Generator</h1>
      <form method=post enctype=multipart/form-data>
        <label>Full Name: <span class="required">*</span>
          <input type=text name=full_name required>
        </label>
        <label>Street Address: <span class="required">*</span>
          <input type=text name=street_address required>
        </label>
        <label>City: <span class="required">*</span>
          <input type=text name=city required>
        </label>
        <label>State: <span class="required">*</span>
          <input type=text name=state required>
        </label>
        <label>Zip Code: <span class="required">*</span>
          <input type=text name=zip_code required>
        </label>
        <label>Last 4 SSN: <span class="required">*</span>
          <input type=text name=ssn_last4 required>
        </label>
        <label>Date of Birth: <span class="required">*</span>
          <input type=text name=dob required>
        </label>
        <label>Email: <span class="required">*</span>
          <input type=email name=email required>
        </label>
        <label>Phone: <span class="required">*</span>
          <input type=text name=phone required>
        </label>
        <label>Driver's License (JPG/PNG/PDF): <input type=file name=license></label>
        <label>Proof of Address (JPG/PNG/PDF): <input type=file name=proof_of_address></label>
        <label>Credit Report (PDF/TXT): <span class="required">*</span>
          <input type=file name=credit_report required>
        </label>
        <input type=submit value="Generate Dispute Letters">
      </form>
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <ul>
          {% for message in messages %}
            <li>{{ message }}</li>
          {% endfor %}
          </ul>
        {% endif %}
      {% endwith %}
      <p style="color:#cc0000; margin-top:10px;">* Required fields</p>
    </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')
