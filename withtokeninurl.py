#https://www.youtube.com/watch?v=J5bIPtEbS0Q
from flask import Flask, jsonify, abort, make_response, request
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/tododb'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'apple'

db = SQLAlchemy(app)

class Tasks(db.Model):
    __tablename__ ='tasks'
    id = db.Column('id',db.Integer, primary_key=True)
    title = db.Column('title',db.Text, primary_key=True)
    description = db.Column('description',db.Text, primary_key=True)
    done = db.Column('done',db.Boolean, primary_key=True)
    user_id = db.Column('user_id',db.Integer)
    
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(500))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') #http://127.0.0.1:5000/route?token=asdfghjkdfvgbhnjmertyuiokjhgf

        if not token:
            return jsonify({'Message': 'Token is missing'}),403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            
        except:
            return jsonify({'Message': 'Token is Invalid'}),403

        return f(*args, **kwargs)

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
           

@app.route('/todo/api/tasks', methods=['GET'])
@token_required
def all_tasks():

    tasks = Tasks.query.all()

    output = []
    print(tasks)
    
    for task in tasks:

        tasks_data = {}
        tasks_data['id'] = task.id
        tasks_data['title'] = task.title
        tasks_data['description'] = task.description
        tasks_data['done'] = task.done
        output.append(tasks_data)
    return jsonify({'tasks': output})

@app.route('/todo/api/tasks', methods=['GET'])
@token_required
def get_tasks(user_id):
    tasks = Tasks.query.filter_by(user_id=user_id)
    
    if tasks.count() == 0:
        return jsonify({'message': 'No tasks found the current user'})
    output = []
    for task in tasks:

        tasks_data = {}
        tasks_data['id'] = task.id
        tasks_data['title'] = task.title
        tasks_data['description'] = task.description
        tasks_data['done'] = task.done
        output.append(tasks_data)
    return jsonify({'tasks': output})


@app.route('/todo/api/tasks', methods=['POST'])
@token_required
def create_task(user_id):

    data = request.get_json()
   
    new_task = Tasks(title=data['title'],description=data['description'],done=data['done'],user_id=user_id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'The New Task has been created'})

@app.route('/todo/api/tasks/<int:id>', methods=['PUT'])
@token_required
def update_task(user_id,id):

    task = Tasks.query.filter_by(id=id, user_id=user_id).first()

    if not task:
        return jsonify({'Message': 'No task to update'})
 
    data = request.get_json()
    d =  bool(data['done'])
    task.done = d
    db.session.commit()
    return jsonify({'Message': 'The task has been updated'})

@app.route('/todo/api/tasks/<int:id>', methods=['DELETE'])
@token_required
def delete_task(user_id,id):
    task = Tasks.query.filter_by(id=id, user_id=user_id).first()

    if not task:
        return jsonify({'Message': 'No task to delete'})

    db.session.delete(task)
    db.session.commit()

    return jsonify({'Message': 'Task has been deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
    #user = Users.query.filter_by(email_id="bhaskar@gmail.com", password="xyz")
    #print(user)
    
    # task = Tasks.query.filter_by(id=2, user_id=1).first()

    # task1 = Tasks.query.filter_by(id=1, user_id=1).first()
    # task2 = Tasks.query.filter_by(id=1, user_id=1)
    # # tasks = Tasks.query.filter_by(user_id=3) 
    # # if tasks.count() == 0:
    # #     print 'hi'
    # # else:
    # #     print 'hello'
    # print(task1)
    
    
    