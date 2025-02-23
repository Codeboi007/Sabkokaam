from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db, Job, Users
from elasticsearch import Elasticsearch
from flask_login import current_user, login_required

job_bp = Blueprint('job', __name__)
es = Elasticsearch(hosts=["http://localhost:9200"])

# Function to create the index if it doesn't exist
def create_index(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"Index '{index_name}' created.")
    else:
        print(f"Index '{index_name}' already exists.")

# Ensure the index exists when the app starts
create_index("jobs")

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
        es.index(
            index="jobs",
            id=new_job.id,
            document={
                "title": title,
                "description": description,
                "location": location,
                "salary": salary,
                "employer_id": current_user.id
            }
        )
        flash('Job posted successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('post_job.html')

@job_bp.route('/search_jobs', methods=['GET', 'POST'])
@login_required
def search_jobs():
    query = request.args.get('q', '')
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
    jobs = [hit["_source"] for hit in response["hits"]["hits"]]
    return render_template('search_results.html', jobs=jobs, query=query)

@job_bp.route('/job_details/<int:job_id>')
@login_required
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_details.html', job=job)