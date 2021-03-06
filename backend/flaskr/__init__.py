import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# function to format the category into key pair values
def clean_category(all_categories):
    clean_categories = [category.format() for category in all_categories]
    if len(clean_categories) == 0:
        return {}
    else:
        categories = {}
        for category in clean_categories:
            categories[category['id']] = category['type']
        return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """

    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authentication, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    """

    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():

        # get all categories and return formatted version
        all_categories = Category.query.all()
        categories = clean_category(all_categories)
        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=["GET"])
    def get_questions():
         # get page from query parameters
        page = request.args.get('page', 1, type=int)

        # get range index of questions return
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # get all questions and return formatted version
        all_questions = Question.query.all()
        questions = [question.format() for question in all_questions]

        # get total number of questions
        total_questions = len(questions)

        # get total number of pages
        total_pages = (total_questions // QUESTIONS_PER_PAGE) + 1

        # get questions for current page
        questions = questions[start:end]

        # get categories and return formatted version
        all_categories = Category.query.all()
        categories = clean_category(all_categories)

        # return questions, total questions, current category, categories
        if len(questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': total_questions,
            'current_category': None,
            'categories': categories,
            'total_pages': total_pages
        })
        

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        else:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=["POST"])
    def create_question():
        body = request.get_json()
        question = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('difficulty')

        if question is None or answer is None or category is None or difficulty is None:
            abort(400)

        new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
        new_question.insert()
        


        return jsonify({
            'success': True,
            'created': new_question.id
        })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')
        if search_term is None:
            abort(400)
        questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
        questions = [question.format() for question in questions]
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions)
        })


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):

        # get questions by category
        all_questions = Question.query.filter(Question.category == category_id).all()
        questions = [question.format() for question in all_questions]
        
        
        # get categories and return formatted version
        all_categories = Category.query.all()
        categories = clean_category(all_categories)

        # return questions, total questions, current category, categories
        if len(questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions),
            'current_category': category_id,
            'categories': categories
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=["POST"])
    def get_quiz_questions():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')
        if category is None:
            abort(400)
        if previous_questions is None:
            previous_questions = []
        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category['id']).all()
        questions = [question.format() for question in questions]
        filtered_questions = [question for question in questions if question['id'] not in previous_questions]
        if len(filtered_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'question': random.choice(filtered_questions)

        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404


    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(406)
    def not_acceptable(error):
        return jsonify({
            'success': False,
            'error': 406,
            'message': 'Not acceptable'
        }), 406

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500


    return app

