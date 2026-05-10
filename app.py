from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# DATABASE CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# DATABASE OBJECT
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

    description = db.Column(db.String(200))


# ---------------- TASK TABLE ----------------

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    status = db.Column(db.String(50))

    assigned_to = db.Column(db.String(100))


# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return redirect('/login')


# ---------------- SIGNUP PAGE ----------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

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


# ---------------- LOGIN PAGE ----------------

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
            return redirect('/dashboard')

        else:
            return "Invalid Credentials"

    return render_template('login.html')


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    total_tasks = Task.query.count()

    completed_tasks = Task.query.filter_by(status='Completed').count()

    pending_tasks = Task.query.filter_by(status='Pending').count()

    return render_template(
        'dashboard.html',
        total=total_tasks,
        completed=completed_tasks,
        pending=pending_tasks
    )


# ---------------- CREATE PROJECT ----------------

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']

        new_project = Project(
            title=title,
            description=description
        )

        db.session.add(new_project)
        db.session.commit()

        return redirect('/dashboard')

    return render_template('create_project.html')


# ---------------- CREATE TASK ----------------

@app.route('/create_task', methods=['GET', 'POST'])
def create_task():

    if request.method == 'POST':

        title = request.form['title']
        status = request.form['status']
        assigned_to = request.form['assigned_to']

        new_task = Task(
            title=title,
            status=status,
            assigned_to=assigned_to
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect('/tasks')

    return render_template('create_task.html')


# ---------------- VIEW TASKS ----------------

@app.route('/tasks')
def tasks():

    all_tasks = Task.query.all()

    return render_template('tasks.html', tasks=all_tasks)


# ---------------- RUN APPLICATION ----------------

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)