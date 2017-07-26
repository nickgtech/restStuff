from flask import Flask, jsonify, abort, make_response, request, url_for

# this is the python centric way of instantiating an instance of the class
app = Flask(__name__)

# List of tasks to be used as a temp databse for the example application
tasks = [
    {
        'id': 1,
        'title': u'Buy Groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Find a tutorial',
        'done': False
    }
]

# builds the uri for the task in question (_external = true builds an absolute path)

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id = task['id'], _external = True)
        else:
            new_task[field] = task[field]
    return new_task

# app.route defines the URL after the IP/Domain name that is being used.
# When being ran locally it defaults to 127.0.0.1:5000.
# the get_task function simply generates a JSON response to GET all tasks in the DB
# following rest principles all tasks are returned under the URI of tasks

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})
# the last line is a bit confusing. Its short hand for a for loop.
# you declare a new task variable dynamically which contains the json object
# from the tasks list at the current index of the list you're at

# this is another get method that allows for individual tasks to be returned.
# keeping in line with rest principles we are using the same URI for tasks
# and adding an id so that we can return a specific task

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            return jsonify({'task': [make_public_task(task)]})
    abort(404)

# the not_found function is called whenever we do an abort
# it receives the error and returns a json response (to keep
# in line with our api) with the error and a description

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

# again using the same URI we use our POST verb to create a new
# task. if the request that is sent is not a json request or
# if there is no title in the request we abort with a
# "Bad request response" While I didnt include it the appropriate way
# to handle this would be to create a bad_request function that returns
# a json response with the details

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('descripton'),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': [make_public_task(task)]}), 201

# Using our URI we ad the task ID to make sure we are updating the right
# task. We use the PUT verb to send the HTTP data. We do some validation
# first and if we pass we then update the task with the apropriate data
# from the request and return the json response.

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) != unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': make_public_task(task[0])})

# Again, keeping in principle with REST we hand over a URI of tasks + id
# and use it to delete the task we'd like out using the correct HTTP
# verb. we return a json response of true to show successful deletion.

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})

# entry point of the app
if __name__ == '__main__':
    app.run(debug=True)
