#import necessary libraries
from ast import Str
import os
from platform import java_ver
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add(
      'Access-Control-Allow-Headers', 'Content-Type,Authorization,True'
      )
    response.headers.add(
      'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS'
      )
    return response

  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    current_categories = [category.format() for category in categories]

    if len(categories) == 0:
        abort(404)

    return jsonify({
      'success': True,
      'categories': {cat.id: cat.type for cat in categories},
      'total_categories': len(Category.query.all())
    })

  '''
  Create an endpoint to handle GET requests for questions.
  '''

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)

    categories = Category.query.order_by(Category.type).all()

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': {category.id: category.type for category in categories},
      'current_category': []
    })
  '''
  Create an endpoint to DELETE question using a question ID. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def deleteor_get_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      questions =  Question.query.order_by(Question.question_id).all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(questions)
      })
    except:
      abort(422)

  @app.route('/questions/<int:question_id>', methods=['GET'])
  def get_single_question(question_id):
    question = Question.query.order_by(Question.id).filter(Question.id == question_id).one_or_none()
    if question is None:
      abort(404)
    
    question = question.format()
    return jsonify({
      'success': True,
      'question': question,
      'question_id': question_id
    })

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question.
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    searchTerm = body.get('searchTerm', None)

    try:
      if searchTerm:
          questions = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{searchTerm}%')).all()
          current_questions = paginate_questions(request, questions)


          return jsonify({
              'success': True,
              'questions': current_questions,
              'total_questions': len(questions)
          })
      else:
          question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
          question.insert()

          questions = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, questions)

          return jsonify({
              'success': True,
              'created': question.id,
              'questions': current_questions,
              'total_questions': len(Question.query.all())
          })
    except:
      abort(422)

  

  '''
  Create a GET endpoint to get questions based on category. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    # body = request.get_json()
    # curr_category = body.get('category', None)
    category = Category.query.filter(Category.id == category_id).first()
    categories = Category.query.order_by(Category.type).all()
    category_ids = [cat.id for cat in categories]

    if category_id in category_ids:
      questions = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
      current_questions = paginate_questions(request, questions)
    else:
      abort(400)

    if len(current_questions) == 0:
        abort(404)
    

    return jsonify({
        'success': True,
        'category': category_id,
        'questions': current_questions,
        'current_category': category.format(),
        'total_questions_in_category': len(Question.query.filter(Question.category == category_id).all())
    })

  '''
  Create a POST endpoint to get questions to play the quiz. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    try:
        body = request.get_json()

        # Get the quiz category as passed in from the request
        category = body.get('quiz_category', None)
        cat_id = category['id']

        # Get the previous questions as passed in from the request
        previous_questions = body.get('previous_questions', None)

        # Put the required parameters in a list
        # variables = ['quiz_category', 'previous_questions']

        # Ensure that the request body contains the two required params. otherwise return a 422 - uprocessable error
        # if not (variable in body for variable in variables):
        #     abort(422)

        # Check if the category passed in is 0 and return random question from all categories
        if cat_id == 0 :
            available_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            question = random.choice(available_questions)
            question = question.format()

        # Check if the category passed in is included in the categories present and return random question from that category
        else :
            available_questions = Question.query.filter(Question.category==cat_id).filter(Question.id.notin_(previous_questions)).all()
            question = random.choice(available_questions)
            question = question.format()

        # An even more complex way to do it.
        # new_question = available_questions[random.randraeeenge(0, len(available_questions))].format() if len(available_questions) > 0 else None

        return jsonify({
            'success': True,
            'question': question,
            'question_id': question.id,
            'total_available_questions': len(available_questions)
        })
    except:
        abort(422)


  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable"
        }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

  @app.errorhandler(405)
  def bad_request(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405
  
  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500
  
  return app

