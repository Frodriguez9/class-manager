import os
import unittest
from unittest.mock import patch
import json
from flask_sqlalchemy import SQLAlchemy

import app
from app.app import create_app
from app.models import setup_db, subject_student, Subject, Student
from app.functions import query_a_record


class AppTestCaseAdminUser(unittest.TestCase):
    """This class represents the app test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgres://{}@{}/{}".format(
            'postgres','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # mock_payload for the Admin user
        self.mock_payload = {
              "iss": "https://nandodev.us.auth0.com/",
              "sub": "auth0|60e1d9c42a44eb006904a174",
              "aud": "courses",
              "iat": 1625511082,
              "exp": 1625518282,
              "azp": "7HMxHXT4PH7JEoAyhC9nU3kxKCEPz8ln",
              "scope": "",
              "permissions": [
                "delete:subjects",
                "get:students",
                "patch:subjects",
                "post:student-subject",
                "post:subjects"
              ]
            }

        self.header = {'Authorization': 'Bearer           eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im1nYVpwQi1BZjlOR3E0a09QLXh5MSJ9.eyJpc3MiOiJodHRwczovL25hbmRvZGV2LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MGUxZDljNDJhNDRlYjAwNjkwNGExNzQiLCJhdWQiOiJjb3Vyc2VzIiwiaWF0IjoxNjI1NTExMDgyLCJleHAiOjE2MjU1MTgyODIsImF6cCI6IjdITXhIWFQ0UEg3SkVvQXloQzluVTNreEtDRVB6OGxuIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6c3ViamVjdHMiLCJnZXQ6c3R1ZGVudHMiLCJwYXRjaDpzdWJqZWN0cyIsInBvc3Q6c3R1ZGVudC1zdWJqZWN0IiwicG9zdDpzdWJqZWN0cyJdfQ.IsbHxyJ9dgfGOMM0WvJrcvBlHNUC1XA85Y1jDVL0cLRbKKg-3B_ximkWGswqZOSAyh0vSWHjaqEDRzWx3aTe4MIXCE6tBCUZA2bgZONHKMq3dL5BjjwuCEcIrv4bBOdrReWtHLDquF6iVzp8UCKVGwYs0t-FlOD8_M7yLTuAYKPfbAOjljWONl1Yqnw64F76nRqu_hqsxlo9H827KHO24HyDnpCYdgQE_Tzucgwms86TUzd0neEx9LpenYzSrhgOTN00BX8_bwA9HYDN5gO4KOXeQoQerGEzZEglpvVms_-CJHEowGZLOaNJdlVlThCA0rZgkKFT_KJx1UUdjdrPsA'
            }

        self.new_subject = {
             "category":"Some Category",
             "start": [2022, 11, 11, 1, 3],
             "zoom_link": "https://zoom.us/s/110..."
             }

        self.subject_wrong_data = {
             "category":"Some Category",
             "start": [2022, 11, 11, 1, 3]
             }


        """ self.patcher = patch()
                Creates inline mock payload for the admin user.
                It patches the verify_decode_jwt() function
                and returns mock payload """

        self.patcher = patch('auth.auth.verify_decode_jwt', return_value=self.mock_payload)
        self.patcher.start()

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()



        # set initial records in database to handel some tests
        self.client().post('/subjects',
                             headers=self.header,
                             json={
                                  "category":"name",
                                  "start": [2022, 11, 11, 1, 3],
                                  "zoom_link": "https://zoom.us.."
                                  })

        self.client().post('/students',
                                 json={"name":"name",
                                       "last_name": "Last Name"})

        self.subject = query_a_record(Subject)
        self.subject_id = self.subject.id

        self.student = query_a_record(Student)
        self.student_id = self.student.id
    # ---------------------------------------------------------
    #  GET /subjects
    #   test: 200
    # ---------------------------------------------------------


    def test_succesful_query_of_all_subjects(self):
        ''' retrives all available courses '''
        res = self.client().get('/subjects')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # ---------------------------------------------------------
    #  POST /subjects
    #   test: 200
    #         400 lack key parameter
    #         400 wrong key
    #         422 wrong date format
    # ---------------------------------------------------------


    def test_succesful_subject_creation(self):
        res = self.client().post('/subjects',
                                 headers=self.header,
                                 json=self.new_subject)
        data = json.loads(res.data)
        test_insertion = Subject.query.filter_by(
                id=data['new_subject']['id']).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(test_insertion)


    def test_400_error_in_argument_for_subject_creation(self):
        ''' tests wrong or incomplete arguments porvided in json'''
        res = self.client().post('/subjects',
                                 headers=self.header,
                                 json=self.subject_wrong_data)
        self.assertEqual(res.status_code, 400)


    def test_422_invalid_date_for_subject_creation(self):
        res = self.client().post('/subjects',
                                 headers=self.header,
                                 json={"category": "Some Category",
                                       "start": [2021,40,1,0,59],
                                       "zoom_link": "https://zoomlink"})
        self.assertEqual(res.status_code, 422)

    # ---------------------------------------------------------
    #  PATCH /subjects/id
    #   test: 200
    #         404 not_found
    #         400 wrong key
    # ---------------------------------------------------------

    def test_succesful_patch_subjects(self):
        subject_to_patch = query_a_record(Subject)
        id = subject_to_patch.id

        res = self.client().patch('/subjects/{}'.format(id),
                                 headers=self.header,
                                 json={"category":"New category"})

        self.assertEqual(res.status_code, 200)


    def test_404_not_found_patch_subject(self):
        res = self.client().patch('/subjects/10000',
                                 headers=self.header,
                                 json=self.new_subject)

        self.assertEqual(res.status_code, 404)


    def test_400_wrong_key_argument_to_patch_subject(self):
        '''tests validity of keys passed in json request'''
        subject_to_patch = query_a_record(Subject)
        id = subject_to_patch.id

        res = self.client().patch('/subjects/{}'.format(id),
                                 headers=self.header,
                                 json={"wrong_key":"invalid_value"})

        self.assertEqual(res.status_code, 400)

    # ---------------------------------------------------------
    #  DELETE /subjects/id
    #   test: 200
    #         404 not_found
    # ---------------------------------------------------------

    def test_succesful_subject_deletion(self):
        subject_to_delete= query_a_record(Subject)
        id = subject_to_delete.id

        res = self.client().delete('/subjects/{}'.format(id),
                                    headers=self.header)
        data = json.loads(res.data)
        check_delation = Subject.query.filter_by(id=id).one_or_none()

        self.assertTrue(res.status_code, 200)
        self.assertEqual(check_delation, None)

    def test_404_not_found_for_delation(self):
        res = self.client().delete('/subjects/10000',
                                 headers=self.header)

        self.assertEqual(res.status_code, 404)

    # ---------------------------------------------------------
    #  POST /students
    #   test: 200
    #         400 lacks/wrong key
    # ---------------------------------------------------------

    def test_succesful_student_creation(self):
        res = self.client().post('/students',
                                 json={"name":"New Student",
                                       "last_name": "Last Name"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["new_student"])

    def test_400_wrong_key_arg_to_create_student(self):
        "checks that all required arguments are provided in json request"
        res = self.client().post('/students',
                                 json={"name":"No"
                                       })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)

    # ---------------------------------------------------------
    #  POST /students/id --> enroll existent student to a subject
    #   test: 200
    #         400 lacks/wrong key
    #         404 not found
    # ---------------------------------------------------------

    def test_sucessful_student_enrollment(self):
        #subject = query_a_record(Subject)
        #subject_id = subject.id

        #student = query_a_record(Student)
        #student_id = student.id

        res = self.client().post('students/{}'.format(self.student_id),
                                headers=self.header,
                                json={"subject_id":self.subject_id})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['students'])


    # ---------------------------------------------------------
    #  POST /students/id --> enroll existent student to a subject
    #   test: 200
    #         400 lacks/wrong key
    # ---------------------------------------------------------


    def tearDown(self):
        self.patcher.stop()

if __name__ == "__main__":
    unittest.main()

# self.assertTrue(data['questions'])
