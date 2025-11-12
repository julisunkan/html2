from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from models import db, EmailTemplate
from datetime import datetime
import os
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mailcraft.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    templates = EmailTemplate.query.order_by(EmailTemplate.created_at.desc()).all()
    return render_template('index.html', saved_templates=templates)

@app.route('/preview', methods=['POST'])
def preview():
    template_name = request.form.get('template_name', 'template1')
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
    title = request.form.get('title')
    subject = request.form.get('subject')
    header = request.form.get('header')
    body = request.form.get('body')
    button_text = request.form.get('button_text')
    button_link = request.form.get('button_link')
    footer = request.form.get('footer')
    template_name = request.form.get('template_name')
    
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
    
    return redirect(url_for('index'))

@app.route('/export/<int:template_id>')
def export_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    
    html_content = render_template(
        f'email_templates/{template.template_name}.html',
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
    template_name = request.form.get('template_name', 'template1')
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
    
    return redirect(url_for('index'))

@app.route('/view/<int:template_id>')
def view_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    return render_template('view_template.html', template=template)

@app.route('/edit/<int:template_id>')
def edit_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    all_templates = EmailTemplate.query.order_by(EmailTemplate.created_at.desc()).all()
    return render_template('index.html', saved_templates=all_templates, edit_template=template)

@app.route('/update/<int:template_id>', methods=['POST'])
def update_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    
    template.title = request.form.get('title')
    template.subject = request.form.get('subject')
    template.header = request.form.get('header')
    template.body = request.form.get('body')
    template.button_text = request.form.get('button_text')
    template.button_link = request.form.get('button_link')
    template.footer = request.form.get('footer')
    template.template_name = request.form.get('template_name')
    
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
