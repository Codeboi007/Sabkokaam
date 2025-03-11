from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from database import db, Job, UserCategory, Application,Users
from flask import current_app as app
import logging
from elasticsearch import Elasticsearch
import json, requests


logging.basicConfig(level=logging.DEBUG)

job_bp = Blueprint('job', __name__)
es = Elasticsearch(hosts=[os.getenv('ELASTICSEARCH_HOST')]) 


@job_bp.route('/post-job', methods=['GET'])
def post_job():
    return render_template('post-job.html')  

@job_bp.route('/post-job', methods=['POST'])
def create_job():
    try:
        job_name = request.form['job-name']
        job_description = request.form['job-description']
        people_needed = request.form['people-needed']
        working_hours = request.form['working-hours']
        earnings = request.form['earnings']
        job_categories = request.form['job-categories']
        address = request.form['address']

        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=YOUR_API_KEY"
        response = requests.get(geocode_url)
        geocode_data = response.json()

        if geocode_data['status'] == 'OK':
            latitude = geocode_data['results'][0]['geometry']['location']['lat']
            longitude = geocode_data['results'][0]['geometry']['location']['lng']
        else:
            latitude = None
            longitude = None

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
            employer_name=current_user.full_name, 
            employer_email=current_user.email, 
            employer_contact=current_user.contact_number,
            job_categories=job_categories,
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(new_job)
        db.session.commit()

        # Index the job in Elasticsearch
        es.index(index='jobs', id=new_job.id, body=new_job.serialize())

        return redirect(url_for('job.search_job_page'))
    except Exception as e:
        logging.error(f"Error during job posting: {e}")
        return jsonify({'success': False, 'error': 'An error occurred during job posting'}), 500

@job_bp.route('/search-job', methods=['GET'])
def search_job_page():
    return render_template('search-job.html')

@job_bp.route('/search-jobs', methods=['GET'])
def search_jobs():
    query = request.args.get('q')


    try:
    
        user_categories = UserCategory.query.filter_by(user_id=current_user.id).all()
        categories = [uc.category.lower() for uc in user_categories]

        
        category_jobs = Job.query.all()
        matching_jobs = []
        for job in category_jobs:
            job_categories = json.loads(job.job_categories)
            if any(category.lower() in categories for category in job_categories):
                matching_jobs.append(job.serialize())

        if not query:
            return jsonify({'success': True, 'jobs': matching_jobs})


        search_results = es.search(index='jobs', body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['job_name', 'job_description', 'employer_name']
                }
            }
        })

        search_jobs = [{'id': hit['_id'], **hit['_source']} for hit in search_results['hits']['hits']]
        
    
        combined_jobs = {job['id']: job for job in matching_jobs + search_jobs}.values()

        return jsonify({'success': True, 'jobs': list(combined_jobs)})
    except Exception as e:
        logging.error(f"Error during job search: {e}")
        return jsonify({'success': False, 'error': 'An error occurred during job search'}), 500

@job_bp.route('/map', methods=['GET'])
def map_page():
    return render_template('map.html')

@job_bp.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        try:

            existing_application = Application.query.filter_by(job_id=job_id, worker_id=current_user.id).first()
            if existing_application:
                flash('You have already applied for this job.', 'warning')
                return redirect(url_for('auth.option_page'))

            new_application = Application(
                job_id=job_id,
                worker_id=current_user.id,
                status='pending'
            )
            db.session.add(new_application)
            db.session.commit()

            flash('You have successfully applied for this job!', 'success')
            return redirect(url_for('auth.option_page'))
        except Exception as e:
            logging.error(f"Error during job application: {e}")
            flash('An error occurred during job application. Please try again.', 'danger')
            return redirect(url_for('job.apply_job', job_id=job_id))

    return render_template('apply-job.html', job=job)

@job_bp.route('/user-category-jobs', methods=['GET'])
def user_category_jobs():
    try:

        user_categories = UserCategory.query.filter_by(user_id=current_user.id).all()
        categories = [uc.category for uc in user_categories]

        
        jobs = Job.query.filter(Job.job_categories.in_(categories)).all()
        job_list = [job.serialize() for job in jobs]

        return jsonify({'success': True, 'jobs': job_list})
    except Exception as e:
        logging.error(f"Error fetching user category jobs: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while fetching jobs'}), 500
    


@job_bp.route('/employer/<int:worker_id>', methods=['GET'])

def view_worker(worker_id):
    worker = Users.query.get(worker_id)
    if not worker:
        flash('Worker not found', 'error')
        return redirect(url_for('job.search_job_page'))
    
    return render_template('employer.html', worker=worker)