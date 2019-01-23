from flask import Flask, jsonify, abort, make_response, request
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
from flask_jwt_extended import JWTManager

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/todo'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'apple'

db = SQLAlchemy(app)

class Tasks(db.Model):
    __tablename__ ='tasks'
    id = db.Column('id',db.Integer, primary_key=True)
    task = db.Column('task',db.String(1000),  nullable=False)
    status = db.Column('status',db.Boolean)
    user_id = db.Column('user_id',db.Integer,nullable=False)
    
class Users(db.Model):
    __tablename__ ='users'
    id = db.Column('id',db.Integer, primary_key=True)
    email_id = db.Column('email_id', db.String(500), unique=True)
    password = db.Column('password',db.String(1000))



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'Message': 'Token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = Users.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            print(e)
            return jsonify({'Message': 'Token is Invalid'})

        return f(user, *args, **kwargs)

    return decorated


def get_token(user_id,email_id,password):
    d = {
        'user_id':user_id,
        'email_id':email_id,
        'password': password,
        'exp': datetime .datetime.utcnow()+datetime.timedelta(minutes=15)
        }
    token = jwt.encode(d, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    return token

@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()
   
    user = Users.query.filter_by(email_id=data['email_id'])
    
    if user.count() == 0:
        pw_hash = bcrypt.generate_password_hash(data['password'])
        new_user = Users(email_id=data['email_id'],password=pw_hash)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Successfully registered'})
    else:
        return jsonify({'message': 'You are already registered or Please login using /login'})


@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    
    user = Users.query.filter_by(email_id=data['email_id']).first()

    if user:
        flag = bcrypt.check_password_hash(user.password, data['password'])
        if flag:
            token = get_token(user.id,user.email_id,user.password)
            return jsonify({'token': token, 'message':'Successfully logged in'})
    
    return jsonify({'message': 'Invalid User...Please register using /register'})
           

@app.route('/todo/api/all_tasks', methods=['GET'])
@token_required
def all_tasks(user):

    tasks = Tasks.query.all()

    output = []
    print(tasks)
    
    for task in tasks:

        tasks_data = {}
        tasks_data['id'] = task.id
        tasks_data['task'] = task.task
        tasks_data['status'] = task.status
        output.append(tasks_data)
    return jsonify({'tasks': output})

@app.route('/todo/api/get_tasks', methods=['GET'])
@token_required
def get_tasks(user):
    tasks = Tasks.query.filter_by(user_id=user.id)
    
    if tasks.count() == 0:
        return jsonify({'message': 'No tasks found the current user'})
    output = []
    for task in tasks:

        tasks_data = {}
        tasks_data['id'] = task.id
        tasks_data['task'] = task.task
        tasks_data['status'] = task.status
        output.append(tasks_data)
    return jsonify(output)



@app.route('/todo/api/create_tasks', methods=['POST'])
@token_required
def create_task(user):

    data = request.get_json()
   
    new_task = Tasks(task=data['task'],status=data['status'],user_id=user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'The New Task has been created'})

@app.route('/todo/api/update_tasks/<int:id>', methods=['PUT'])
@token_required
def update_task(user,id):

    task = Tasks.query.filter_by(user_id=user.id).first()

    if not task:
        return jsonify({'Message': 'No task to update'})
 
    data = request.get_json()
    task.status = bool(data['status'])
    db.session.commit()
    return jsonify({'Message': 'The task has been updated'})

@app.route('/todo/api/delete_tasks/<int:id>', methods=['DELETE'])
@token_required
def delete_task(user,id):
    task = Tasks.query.filter_by(user_id=user.id).first()

    if not task:
        return jsonify({'Message': 'No task to delete'})

    db.session.delete(task)
    db.session.commit()

    return jsonify({'Message': 'Task has been deleted successfully'})

if __name__ == '__main__':
    app.run(debug=False)