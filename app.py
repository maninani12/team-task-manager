from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.secret_key = "teamtasksecret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- USER TABLE ----------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))

    role = db.Column(db.String(20))


# ---------------- PROJECT TABLE ----------------

class Project(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    description = db.Column(db.String(300))


# ---------------- TASK TABLE ----------------

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    description = db.Column(db.String(300))

    priority = db.Column(db.String(20))

    start_date = db.Column(db.String(50))

    due_date = db.Column(db.String(50))

    status = db.Column(db.String(50))

    work_note = db.Column(db.String(500))

    assigned_to = db.Column(db.String(100))

    project_name = db.Column(db.String(100))

    task_active = db.Column(db.String(20))

    admin_review = db.Column(db.String(300))


# ---------------- CREATE DATABASE ----------------

with app.app_context():
    db.create_all()


# ---------------- HOME ----------------

@app.route('/')
def home():
    return redirect('/login')


# ---------------- SIGNUP ----------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        name = request.form['name']

        email = request.form['email']

        password = request.form['password']

        role = request.form['role']

        check_user = User.query.filter_by(email=email).first()

        if check_user:
            return "User already exists"

        new_user = User(
            name=name,
            email=email,
            password=password,
            role=role
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect('/login')

    return render_template('signup.html')


# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session['user'] = user.name

            session['role'] = user.role

            if user.role == 'admin':
                return redirect('/admin_dashboard')

            else:
                return redirect('/member_dashboard')

        else:
            return "Invalid Credentials"

    return render_template('login.html')


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


# ---------------- ADMIN DASHBOARD ----------------

@app.route('/admin_dashboard')
def admin_dashboard():

    if session.get('role') != 'admin':
        return redirect('/login')

    total_tasks = Task.query.count()

    completed_tasks = Task.query.filter_by(status='Completed').count()

    pending_tasks = Task.query.filter_by(status='Pending').count()

    total_users = User.query.count()

    return render_template(
        'admin_dashboard.html',
        total=total_tasks,
        completed=completed_tasks,
        pending=pending_tasks,
        users=total_users
    )


# ---------------- MEMBER DASHBOARD ----------------

@app.route('/member_dashboard')
def member_dashboard():

    if session.get('role') != 'member':
        return redirect('/login')

    my_tasks = Task.query.filter_by(
        assigned_to=session['user']
    ).all()

    return render_template(
        'member_dashboard.html',
        tasks=my_tasks
    )


# ---------------- CREATE PROJECT ----------------

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():

    if session.get('role') != 'admin':
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']

        description = request.form['description']

        new_project = Project(
            title=title,
            description=description
        )

        db.session.add(new_project)

        db.session.commit()

        return redirect('/admin_dashboard')

    return render_template('create_project.html')


# ---------------- CREATE TASK ----------------

@app.route('/create_task', methods=['GET', 'POST'])
def create_task():

    if session.get('role') != 'admin':
        return redirect('/login')

    users = User.query.filter_by(role='member').all()

    projects = Project.query.all()

    if request.method == 'POST':

        title = request.form['title']

        description = request.form['description']

        priority = request.form['priority']

        start_date = request.form['start_date']

        due_date = request.form['due_date']

        assigned_to = request.form.get('assigned_to')

        project_name = request.form.get('project_name')

        if not assigned_to or not project_name:
            return "Please create member account and project first"

        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            start_date=start_date,
            due_date=due_date,
            status='Pending',
            work_note='',
            assigned_to=assigned_to,
            project_name=project_name,
            task_active='Yes',
            admin_review=''
        )

        db.session.add(new_task)

        db.session.commit()

        return redirect('/tasks')

    return render_template(
        'create_task.html',
        users=users,
        projects=projects
    )


# ---------------- VIEW TASKS ----------------

@app.route('/tasks')
def tasks():

    if session.get('role') != 'admin':
        return redirect('/login')

    all_tasks = Task.query.all()

    return render_template(
        'tasks.html',
        tasks=all_tasks
    )


# ---------------- ADMIN UPDATE TASK ----------------

@app.route('/admin_update_task/<int:id>', methods=['POST'])
def admin_update_task(id):

    if session.get('role') != 'admin':
        return redirect('/login')

    task = Task.query.get(id)

    task.title = request.form['title']

    task.description = request.form['description']

    task.assigned_to = request.form['assigned_to']

    task.priority = request.form['priority']

    task.start_date = request.form['start_date']

    task.due_date = request.form['due_date']

    task.admin_review = request.form['admin_review']

    db.session.commit()

    return redirect('/tasks')


# ---------------- DISABLE TASK ----------------

@app.route('/disable_task/<int:id>')
def disable_task(id):

    if session.get('role') != 'admin':
        return redirect('/login')

    task = Task.query.get(id)

    task.task_active = 'No'

    db.session.commit()

    return redirect('/tasks')


# ---------------- UPDATE TASK ----------------

@app.route('/update_task/<int:id>', methods=['GET', 'POST'])
def update_task(id):

    task = Task.query.get(id)

    if task.task_active == 'No':
        return "Task disabled by admin"

    if request.method == 'POST':

        task.status = request.form['status']

        task.work_note = request.form['work_note']

        db.session.commit()

        return redirect('/member_dashboard')

    return render_template(
        'update_task.html',
        task=task
    )


# ---------------- DELETE TASK ----------------

@app.route('/delete_task/<int:id>')
def delete_task(id):

    if session.get('role') != 'admin':
        return redirect('/login')

    task = Task.query.get(id)

    db.session.delete(task)

    db.session.commit()

    return redirect('/tasks')


# ---------------- MANAGE USERS ----------------

@app.route('/manage_users')
def manage_users():

    if session.get('role') != 'admin':
        return redirect('/login')

    users = User.query.all()

    return render_template(
        'manage_users.html',
        users=users
    )


# ---------------- CHANGE ROLE ----------------

@app.route('/change_role/<int:id>')
def change_role(id):

    if session.get('role') != 'admin':
        return redirect('/login')

    user = User.query.get(id)

    if user.role == 'member':
        user.role = 'admin'

    else:
        user.role = 'member'

    db.session.commit()

    return redirect('/manage_users')


# ---------------- DELETE USER ----------------

@app.route('/delete_user/<int:id>')
def delete_user(id):

    if session.get('role') != 'admin':
        return redirect('/login')

    user = User.query.get(id)

    db.session.delete(user)

    db.session.commit()

    return redirect('/manage_users')


# ---------------- RUN APP ----------------

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port)
