# routes/job_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db, Job, Users
from elasticsearch import Elasticsearch
from flask_login import current_user, login_required
import os

job_bp = Blueprint('job', __name__, url_prefix='/job')
es = Elasticsearch(hosts=[os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')])  # Initialize Elasticsearch here

def create_index(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "location": {"type": "text"},
                    "salary": {"type": "float"},
                    "employer_id": {"type": "integer"}
                }
            }
        })
        print(f"Index '{index_name}' created.")
    else:
        print(f"Index '{index_name}' already exists.")

@job_bp.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'employer':
        flash('Only employers can post jobs.', 'error')
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        salary = float(request.form['salary'])

        new_job = Job(
            title=title,
            description=description,
            location=location,
            salary=salary,
            employer_id=current_user.id
        )
        db.session.add(new_job)
        db.session.commit()

        # Index the job in Elasticsearch
        job_data = {
            "title": title,
            "description": description,
            "location": location,
            "salary": salary,
            "employer_id": current_user.id
        }
        print(f"Indexing job: {job_data}")
        es.index(
            index="jobs",
            id=new_job.id,
            body=job_data
        )
        flash('Job posted successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('post_job.html')

@job_bp.route('/search_jobs', methods=['GET'])
@login_required
def search_jobs():
    query = request.args.get('q', '')  # Get the search term from the query string
    print(f"Searching for: {query}")
    if query:
        response = es.search(
            index="jobs",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "description", "location"]
                    }
                }
            }
        )
        job_ids = [hit["_id"] for hit in response["hits"]["hits"]]
        jobs = Job.query.filter(Job.id.in_(job_ids)).all()  # Fetch jobs from the database
        print(f"Found jobs: {jobs}")
    else:
        jobs = []  # No query, return an empty list
    return render_template('search_results.html', jobs=jobs, query=query)

@job_bp.route('/job_details/<int:job_id>')
@login_required
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_details.html', job=job)