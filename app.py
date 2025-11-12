from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session, abort
from models import db, EmailTemplate
from datetime import datetime
import os
from io import BytesIO
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mailcraft.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db.init_app(app)

ALLOWED_TEMPLATES = [
    'template1', 'template2', 'template3', 'template4', 'template5',
    'template6', 'template7', 'template8', 'template9', 'template10'
]

def validate_template_name(template_name):
    if template_name not in ALLOWED_TEMPLATES:
        abort(400, description="Invalid template name")
    return template_name

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']

def validate_csrf_token():
    token = session.get('csrf_token')
    form_token = request.form.get('csrf_token')
    if not token or token != form_token:
        abort(403, description="Invalid CSRF token")

app.jinja_env.globals['csrf_token'] = generate_csrf_token

with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    templates = EmailTemplate.query.order_by(EmailTemplate.created_at.desc()).all()
    
    # Get list of uploaded images
    uploaded_images = []
    upload_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_folder):
        uploaded_images = sorted([f for f in os.listdir(upload_folder) if allowed_file(f)], reverse=True)
    
    return render_template('index.html', saved_templates=templates, uploaded_images=uploaded_images)

@app.route('/preview', methods=['POST'])
def preview():
    template_name = validate_template_name(request.form.get('template_name', 'template1'))
    header = request.form.get('header', '')
    body = request.form.get('body', '')
    button_text = request.form.get('button_text', '')
    button_link = request.form.get('button_link', '')
    footer = request.form.get('footer', '')

    return render_template(
        f'email_templates/{template_name}.html',
        header=header,
        body=body,
        button_text=button_text,
        button_link=button_link,
        footer=footer
    )

@app.route('/save', methods=['POST'])
def save_template():
    validate_csrf_token()

    title = request.form.get('title')
    subject = request.form.get('subject')
    header = request.form.get('header')
    body = request.form.get('body')
    button_text = request.form.get('button_text')
    button_link = request.form.get('button_link')
    footer = request.form.get('footer')
    template_name = validate_template_name(request.form.get('template_name'))

    template = EmailTemplate(
        title=title,
        subject=subject,
        header=header,
        body=body,
        button_text=button_text,
        button_link=button_link,
        footer=footer,
        template_name=template_name
    )

    db.session.add(template)
    db.session.commit()

    return redirect(url_for('index', success='saved'))

@app.route('/export/<int:template_id>')
def export_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    validated_template_name = validate_template_name(template.template_name)

    html_content = render_template(
        f'email_templates/{validated_template_name}.html',
        header=template.header,
        body=template.body,
        button_text=template.button_text,
        button_link=template.button_link,
        footer=template.footer
    )

    buffer = BytesIO()
    buffer.write(html_content.encode('utf-8'))
    buffer.seek(0)

    filename = f"{template.title.replace(' ', '_')}.html"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='text/html'
    )

@app.route('/export_current', methods=['POST'])
def export_current():
    validate_csrf_token()

    template_name = validate_template_name(request.form.get('template_name', 'template1'))
    title = request.form.get('title', 'email_template')
    header = request.form.get('header', '')
    body = request.form.get('body', '')
    button_text = request.form.get('button_text', '')
    button_link = request.form.get('button_link', '')
    footer = request.form.get('footer', '')

    html_content = render_template(
        f'email_templates/{template_name}.html',
        header=header,
        body=body,
        button_text=button_text,
        button_link=button_link,
        footer=footer
    )

    buffer = BytesIO()
    buffer.write(html_content.encode('utf-8'))
    buffer.seek(0)

    filename = f"{title.replace(' ', '_')}.html"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='text/html'
    )

@app.route('/import_html', methods=['POST'])
def import_html():
    validate_csrf_token()

    if 'html_file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['html_file']
    if file.filename == '':
        return redirect(url_for('index'))

    html_content = file.read().decode('utf-8')
    title = request.form.get('import_title', file.filename.replace('.html', ''))

    template = EmailTemplate(
        title=title,
        subject=f"Imported: {title}",
        header="Imported Template",
        body=html_content,
        button_text="",
        button_link="",
        footer="",
        template_name="template1"
    )

    db.session.add(template)
    db.session.commit()

    return redirect(url_for('index', success='imported'))

@app.route('/view/<int:template_id>')
def view_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    validate_template_name(template.template_name)
    return render_template('view_template.html', template=template)

@app.route('/edit/<int:template_id>')
def edit_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    all_templates = EmailTemplate.query.order_by(EmailTemplate.created_at.desc()).all()
    
    # Get list of uploaded images
    uploaded_images = []
    upload_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_folder):
        uploaded_images = sorted([f for f in os.listdir(upload_folder) if allowed_file(f)], reverse=True)
    
    return render_template('index.html', saved_templates=all_templates, edit_template=template, uploaded_images=uploaded_images)

@app.route('/update/<int:template_id>', methods=['POST'])
def update_template(template_id):
    validate_csrf_token()

    template = EmailTemplate.query.get_or_404(template_id)

    template.title = request.form.get('title')
    template.subject = request.form.get('subject')
    template.header = request.form.get('header')
    template.body = request.form.get('body')
    template.button_text = request.form.get('button_text')
    template.button_link = request.form.get('button_link')
    template.footer = request.form.get('footer')
    template.template_name = validate_template_name(request.form.get('template_name'))

    db.session.commit()

    return redirect(url_for('index', success='updated'))

@app.route('/delete/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    validate_csrf_token()

    template = EmailTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return redirect(url_for('index', success='deleted'))

@app.route('/upload_image', methods=['POST'])
def upload_image():
    validate_csrf_token()
    
    if 'image' not in request.files:
        return redirect(url_for('index', error='No image file provided'))
    
    file = request.files['image']
    
    if file.filename == '':
        return redirect(url_for('index', error='No image selected'))
    
    if file and allowed_file(file.filename):
        filename = secrets.token_hex(8) + '_' + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_url = url_for('static', filename=f'uploads/{filename}', _external=True)
        return redirect(url_for('index', success='image_uploaded', image_url=image_url, filename=filename))
    
    return redirect(url_for('index', error='Invalid file type. Only images allowed.'))

@app.route('/delete_image/<filename>', methods=['POST'])
def delete_image(filename):
    validate_csrf_token()
    
    # Security: Ensure filename doesn't contain path traversal attempts
    if '/' in filename or '\\' in filename or '..' in filename:
        return redirect(url_for('index', error='Invalid filename'))
    
    # Verify file exists and is an allowed image type
    if not allowed_file(filename):
        return redirect(url_for('index', error='Invalid file type'))
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return redirect(url_for('index', success='image_deleted'))
        except Exception as e:
            return redirect(url_for('index', error=f'Failed to delete image: {str(e)}'))
    else:
        return redirect(url_for('index', error='Image not found'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)