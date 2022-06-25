import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgres://tosmel:@Bodmas007@localhost:5432/trivia'
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories']), True

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions']), True
        self.assertTrue(data['total_questions']), True
        self.assertTrue(data['categories']), True

    def test_get_questions_per_page(self):
        response = self.client().get('/questions?page=1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions']), True
        self.assertTrue(data['total_questions']), True
        self.assertTrue(data['categories']), True
        
    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories']), True
        self.assertTrue(data['total_categories']), True
    
    def test_no_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories']), True
        self.assertTrue(data['total_categories']), True
    
    # def test_add_question(self):
    #     response = self.client().post('/questions', json=self.new_question)
    #     data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created'])

    def test_get_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions']), True
        self.assertTrue(data['total_questions']), True
        self.assertTrue(data['categories']), True

    def test_delete_question_not_found(self):
        response = self.client().delete('/questions/1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
    
    def test_delete_question(self):
        response = self.client().delete('/questions/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_get_quizzes(self):
        response = self.client().post('/quizzes',
                                      json={"previous_questions": [5],
                                            "category": "all"
                                            })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("question", data)
        self.assertNotEqual("question", [])

    def test_get_quizzes_missing_parameter(self):
        response = self.client().post('/quizzes', json={"category": "all"})

        self.assertEqual(response.status_code, 406)

    def test_get_quizzes_no_parameter(self):
        response = self.client().post('/quizzes')

        self.assertEqual(response.status_code, 400)
    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()