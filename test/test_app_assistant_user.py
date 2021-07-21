from test.config import *


class AppTestCaseAssistantUser(unittest.TestCase):
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
                "get:students"
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

        self.patcher = patch('app.auth.auth.verify_decode_jwt', return_value=self.mock_payload)
        self.patcher.start()

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()



        # set initial records in database to handel some tests
        # the if statement provides some resource management
        if len(Subject.query.all()) == 0:
            self.client().post('/subjects',
                                 headers=self.header,
                                 json={
                                      "category":"name",
                                      "start": [2022, 11, 11, 1, 3],
                                      "zoom_link": "https://zoom.us.."
                                      })

        if len(Student.query.all()) == 0:
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
    #   test: 403 unauthorized
    # ---------------------------------------------------------


    def test_403_unauthorized_user_for_subject_creation(self):
        res = self.client().post('/subjects',
                                 headers=self.header,
                                 json=self.new_subject)

        self.assertEqual(res.status_code, 403)



    # ---------------------------------------------------------
    #  PATCH /subjects/id
    #   test: 403 unauthorized
    # ---------------------------------------------------------

    def test_403_unauthorized_patch_subjects(self):
        res = self.client().patch('/subjects/{}'.format(self.subject_id),
                                 headers=self.header,
                                 json={"category":"New category"})

        self.assertEqual(res.status_code, 403)


    # ---------------------------------------------------------
    #  DELETE /subjects/id
    #   test: 403 unauthorized
    # ---------------------------------------------------------

    def test_403_unauthorized_for_delation(self):
        res = self.client().delete('/subjects/{}'.format(self.subject_id),
                                 headers=self.header)

        self.assertEqual(res.status_code, 403)

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
    #   test: 403 unauthorized
    # ---------------------------------------------------------

    def test_403_unauthorized_to_enroll_student(self):
        res = self.client().post('students/{}'.format(self.student_id),
                                headers=self.header,
                                json={"subject_id":self.subject_id})

        self.assertEqual(res.status_code, 403)

    # ---------------------------------------------------------
    #  GET /subjects/<subject_id>/students
    #   test: 200
    #         404 not_found
    # ---------------------------------------------------------

    def test_succesful_student_query_by_course(self):
        res = self.client().get(
            '/subjects/{}/students'.format(
                self.subject_id),
                headers=self.header)

        self.assertEqual(res.status_code, 200)


    def test_404_course_not_found_to_query_students_by_course(self):
        res = self.client().get(
            '/subjects/{}/students'.format(
                100000),
                headers=self.header)

        self.assertEqual(res.status_code, 404)


    def tearDown(self):
        self.patcher.stop()


#if __name__ == "__main__":
#    unittest.main()
