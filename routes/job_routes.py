from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from database import db, Job
from flask import current_app as app
import logging
from elasticsearch import Elasticsearch

# Configure logging
logging.basicConfig(level=logging.DEBUG)

job_bp = Blueprint('job', __name__)
es = Elasticsearch(hosts=[os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')])  # Initialize Elasticsearch here

# Job Posting Page Route
@job_bp.route('/post-job', methods=['GET'])
@login_required
def post_job():
    return render_template('post-job.html')  # Render the job posting page

@job_bp.route('/post-job', methods=['POST'])
@login_required
def create_job():
    try:
        # Extract form data
        job_name = request.form['job-name']
        job_description = request.form['job-description']
        people_needed = request.form['people-needed']
        working_hours = request.form['working-hours']
        earnings = request.form['earnings']

        # Save uploaded job image
        job_image = request.files['job-image']
        if job_image:
            job_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(job_image.filename))
            job_image.save(job_image_path)
        else:
            job_image_path = None

        # Create job record
        new_job = Job(
            job_name=job_name,
            job_description=job_description,
            people_needed=people_needed,
            working_hours=working_hours,
            earnings=earnings,
            job_image=job_image_path,
            employer_name=current_user.full_name , # Store the employer's name
            employer_email=current_user.email,  # Store the employer's email
            employer_contact=current_user.contact_number 
            
        )
        db.session.add(new_job)
        db.session.commit()

        # Index the job in Elasticsearch
        es.index(index='jobs', id=new_job.id, body={
            'job_name': job_name,
            'job_description': job_description,
            'people_needed': people_needed,
            'working_hours': working_hours,
            'earnings': earnings,
            'employer_name': current_user.full_name,
            'employer_email': current_user.email,
            'employer_contact': current_user.contact_number,
            'created_at': new_job.created_at
        })

        # Redirect to a success page or job listing page
        return redirect(url_for('job.post_job'))
    except Exception as e:
        logging.error(f"Error during job posting: {e}")
        return jsonify({'success': False, 'error': 'An error occurred during job posting'}), 500

@job_bp.route('/search-job', methods=['GET'])
def search_job_page():
    return render_template('search-job.html') 


# Job Search Route
@job_bp.route('/search-jobs', methods=['GET'])
def search_jobs():
    query = request.args.get('q')
    if not query:
        return jsonify({'success': False, 'error': 'No search query provided'}), 400

    try:
        search_results = es.search(index='jobs', body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['job_name', 'job_description', 'employer_name']
                }
            }
        })

        jobs = [{'id': hit['_id'], **hit['_source']} for hit in search_results['hits']['hits']]
        return jsonify({'success': True, 'jobs': jobs})
    except Exception as e:
        logging.error(f"Error during job search: {e}")
        return jsonify({'success': False, 'error': 'An error occurred during job search'}), 500
    


    # Placeholder route for job application
@job_bp.route('/apply/<int:job_id>', methods=['GET'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('apply-job.html', job=job)