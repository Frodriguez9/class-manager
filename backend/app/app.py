import sys, os

from flask import (
    Flask,
    request,
    jsonify,
    abort,
    redirect,
    url_for,
    session
    )

from backend.app.models import (
    db,
    setup_db,
    Subject,
    Student,
    subject_student
    )
from flask_cors import CORS
from six.moves.urllib.parse import urlencode
from backend.app.functions import (
    format_date,
    build_login_link,
    validate_json_keys,
    check_required_data
    )

from backend.auth.auth import AuthError, requires_auth
import http.client


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = os.environ['APP_SECRET_KEY']
    setup_db(app)
    CORS(app)


    # ---------------------------------------------------------
    # Public routes
    # ---------------------------------------------------------

    @app.route('/subjects')
    def query_courses():
        try:
            subjects_list = Subject.query.all()
            courses = [subject.info() for subject in subjects_list]
        except:
            abort(500)

        return jsonify({
            "success": True,
            "subjects": courses
        })


    # ---------------------------------------------------------
    # Subject CREATE, PATCH, DELETE
    # ---------------------------------------------------------

    '''
    POST /subjects
        create a new online class.
        Permission: for users with admin role
    '''

    @app.route("/subjects", methods=['POST'])
    @requires_auth('post:subjects')
    def create_subject(payload):
        data = request.get_json()
        '''
        required data structure:

            {
             'category':'Some Category',
             'start': [yyyy, mm, dd, hh, mm],
             'zoom_link': "https://zoom.us/s/1100000?iIifQ.wfY2ldlb82SWo3TsR77lBiJjR53TNeFUiKbLyCvZZjw"
             }

             where dd == [1-31]
                   mm == [1-12]
                   hh == [00-23]
                   mm == [00-59]
        '''
        required_keys = ["category", "start", "zoom_link"]
        # return error 400 if does not validate
        check_required_data(required_keys, data)

        # error in date format is handled in the function definition
        start = format_date(data['start'])

        subject = Subject(category=data['category'],
                          start=start,
                          zoom_link=data['zoom_link'])

        subject.insert()

        return jsonify({
            'success': True,
            'new_subject': subject.info()

        })


    '''
    PATCH /subjects/id
        modify an existing online class.
        Permission: for users with admin role
    '''

    @app.route('/subjects/<int:subject_id>', methods=['PATCH'])
    @requires_auth('patch:subjects')
    def edit_subject(payload, subject_id):

        data = request.get_json()
        #       error. What happens if wrong keys are submited
        '''
        required data structure:

            {
             opt_"category": "new_category",
             opt_"start": [yyyy, mm, dd, hh, mm],
             opt_"zoom_link": "https://zoom.us/s/1100000?iIifQ.wfY2ldlb82SWo3TsR77lBiJjR53TNeFUiKbLyCvZZjw",
             opt_"withdraw_students": [X, Y]
             }

             where dd == [1-31]
        '''
        acceptable_keys = ["category", "start", "zoom_link", "withdraw_students"]
        # return error 400 if does not validate
        validate_json_keys(acceptable_keys, data)

        subject = Subject.query.filter_by(id=subject_id).one_or_none()
        if not subject:
            abort(404)


        if "category" in data:
            subject.category = data["category"]
        if "start" in data:
            start = format_date(data["start"])
            subject.start = start
        if "zoom_link" in data:
            subject.zoom_link = data["zoom_link"]
        if "withdraw_students" in data:
            for id in data["withdraw_students"]:
                for student in subject.students:
                    if id == student.id:
                        subject.students.remove(student)

        subject.update()

        return jsonify({
            "success": True,
            "updated_info": subject.info()
        })


    '''
    DELETE /subjects/<id>
    '''

    @app.route('/subjects/<int:subject_id>', methods=['DELETE'])
    @requires_auth('delete:subjects')
    def delete_subject(payload, subject_id):
        subject = Subject.query.filter_by(id=subject_id).one_or_none()

        if not subject:
            abort(404)

        subject.delete()

        return jsonify({
            "success": True
        })

    # ---------------------------------------------------------
    # Student CREATE, ENROLL IN CLASS
    # ---------------------------------------------------------

    @app.route('/students', methods=['POST'])
    def create_new_student():
        data = request.get_json()
        '''
        required data structure:

            {
             "name": "some name",
             "last_name": "some last name"
             }
        '''

        required_keys = ["name", "last_name"]

        check_required_data(required_keys, data)

        try:
            new_student = Student(name=data["name"], last_name=data["last_name"])
            new_student.insert()

        except:
            abort(500)

        return jsonify({
            "success": True,
            "new_student": new_student.info()

        })


    @app.route('/students/<int:student_id>', methods=["POST"])
    @requires_auth('post:student-subject')
    def enroll_student(payload, student_id):
        data = request.get_json()
        '''
        required data structure:

            {
             "subject_id": some integer
             }
        '''
        # error 400 handled in check_required_data()
        check_required_data(['subject_id'], data)

        student = Student.query.filter_by(id=student_id).one_or_none()
        subject = Subject.query.filter_by(id=data["subject_id"]).one_or_none()

        if not subject or not student:
            abort(404)

        try:

            subject.students.append(student)
            subject.update()

            enrolled_students = [student.info() for student in subject.students]

        except:
            abort(500)

        return jsonify({
            "success": True,
            "subject_id": subject.id,
            "students": enrolled_students
        })


    # ---------------------------------------------------------
    # Student QUERY
    # ---------------------------------------------------------


    @app.route('/subjects/<int:subject_id>/students')
    @requires_auth('get:students')
    def query_students_in_course(payload, subject_id):
        subject = Subject.query.filter_by(id=subject_id).one_or_none()
        if not subject:
            abort(404)

        info = subject.info()

        return jsonify({
            "success": True,
            "subject_id": subject_id,
            "category": info["category"],
            "students": info["students"]
        })



    # ---------------------------------------------------------
    # Login, callback handler, logout
    # ---------------------------------------------------------

    @app.route('/login')
    def test_auth0():

        auth_link = build_login_link()

        return redirect(auth_link)

        '''return jsonify({
            "status": "Auth0 working properly",
            "link": link
        })'''

    @app.route('/callback')
    def callback_handling():
        # TODO: Check how to obtain to save the token info in the flask
        # session so that you can unse in the ''/logout' route
        '''code = request.args.get('code')
        conn = http.client.HTTPSConnection("")

        payload = f"grant_type=authorization_code&client_id=7HMxHXT4PH7JEoAyhC9nU3kxKCEPz8ln&client_secret=pN1qArB6GIPgB1N_EBrCBzrgtZHsa1bI0CPPGQlgQArS7nztazgJUxnov6Gg7PRD&code={code}&redirect_uri=http://127.0.0.1:5000/callback"

        headers = { 'content-type': "application/x-www-form-urlencoded" }

        conn.request("POST", "/nandodev.us.auth0.com/oauth/token", payload, headers)

        res = conn.getresponse()
        data = res.read()

        print(data.decode("utf-8"))'''

        return redirect('/subjects')


    @app.route('/logout')
    def user_logout():
        session.clear()
        params = {'returnTo': url_for('query_courses', _external=True), 'client_id': os.environ['AUTH_CLIENT_ID']}
        a = os.environ['AUTH_URL'] + '/v2/logout?' + urlencode(params)
        return redirect(os.environ['AUTH_URL'] + '.auth0.com' + '/v2/logout?' + urlencode(params))


    # ---------------------------------------------------------
    # error handlers
    # ---------------------------------------------------------

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404


    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Failure"
        }), 500


    '''
    error handler for AuthError
        error handler should conform to general task above
    '''

    @app.errorhandler(AuthError)
    def authentication_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "code": error.error['code'],
            "message": error.error['description']
        }), error.status_code

    return app
