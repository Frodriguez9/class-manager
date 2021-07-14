import os
import unittest
from unittest.mock import patch
import json
from flask_sqlalchemy import SQLAlchemy

import app
from app.app import create_app
from app.models import setup_db, subject_student, Subject, Student

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

        # mock_payload for the assistant user
        self.mock_payload = {
              "iss": "https://nandodev.us.auth0.com/",
              "sub": "auth0|60e8b100a8522a00691290ad",
              "aud": "courses",
              "iat": 1625862632,
              "exp": 1625869832,
              "azp": "7HMxHXT4PH7JEoAyhC9nU3kxKCEPz8ln",
              "scope": "",
              "permissions": [
                "get:students"
              ]
            }

        self.header = {'Authorization': 'Bearer           eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im1nYVpwQi1BZjlOR3E0a09QLXh5MSJ9.eyJpc3MiOiJodHRwczovL25hbmRvZGV2LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MGUxZDljNDJhNDRlYjAwNjkwNGExNzQiLCJhdWQiOiJjb3Vyc2VzIiwiaWF0IjoxNjI1NTExMDgyLCJleHAiOjE2MjU1MTgyODIsImF6cCI6IjdITXhIWFQ0UEg3SkVvQXloQzluVTNreEtDRVB6OGxuIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6c3ViamVjdHMiLCJnZXQ6c3R1ZGVudHMiLCJwYXRjaDpzdWJqZWN0cyIsInBvc3Q6c3R1ZGVudC1zdWJqZWN0IiwicG9zdDpzdWJqZWN0cyJdfQ.IsbHxyJ9dgfGOMM0WvJrcvBlHNUC1XA85Y1jDVL0cLRbKKg-3B_ximkWGswqZOSAyh0vSWHjaqEDRzWx3aTe4MIXCE6tBCUZA2bgZONHKMq3dL5BjjwuCEcIrv4bBOdrReWtHLDquF6iVzp8UCKVGwYs0t-FlOD8_M7yLTuAYKPfbAOjljWONl1Yqnw64F76nRqu_hqsxlo9H827KHO24HyDnpCYdgQE_Tzucgwms86TUzd0neEx9LpenYzSrhgOTN00BX8_bwA9HYDN5gO4KOXeQoQerGEzZEglpvVms_-CJHEowGZLOaNJdlVlThCA0rZgkKFT_KJx1UUdjdrPsA'
            }

        self.new_subject = {
             "category":"Some Category",
             "start": [2022, 11, 11, 1, 3],
             "zoom_link": "https://zoom.us/s/1100000?iIifQ.wfY2ldlb82SWo3TsR77lBiJjR53TNeFUiKbLyCvZZjw"
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


    def test_succesful_query_of_all_subjects(self):
        ''' retrives all available courses '''
        res = self.client().get('/subjects')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_403_unauthorized_subject_creation(self):
        res = self.client().post('/subjects',
                                 headers=self.header,
                                 json=self.subject_wrong_data)
        self.assertEqual(res.status_code, 403)


    def tearDown(self):
        self.patcher.stop()

if __name__ == "__main__":
    unittest.main()
