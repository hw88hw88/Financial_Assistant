# import the chatbot
from chatbot import Chatbot

# import other dependencies
import datetime
import re
import threading
import random

# import flask for the API server
from flask import Flask, request, render_template
app = Flask(__name__)

user_background = {}
user_background_lock = threading.Lock()

jobs = {}
jobs_lock = threading.Lock()

# initialize the chatbot and LLM
bot = Chatbot()
# the bot_lock can prevent the system to run out of memory because of running multiple copies of the LLM
bot_lock = threading.Lock()
with bot_lock:
    # initialize the chatbot before receiving any requests from users to reduce the waiting time
    bot.initialize_chatbot()

# running this function to remove unnecessary elements in jobs{} and user_background{}
# input: (No input variable)
# change (or affected items):
# 1. global variable: jobs{}
# 2. global variable: user_background{}
def clear_job_and_background():
    try:
        def clear_element(dict_elements):
            keys = list(dict_elements.keys())
            for k in keys:
                element = dict_elements.get(k)
                difference = datetime.datetime.now() - element.get('creation_time')
                if difference.days >= 1:
                    dict_elements.pop(k, None)
        with jobs_lock:
            clear_element(jobs)
        with user_background_lock:
            clear_element(user_background)
    except Exception as e:
        print('Error(clear_job_and_background(): ', e)

# picking the system message from a set of pre-written messages to inform the user the chatbot is running
# input: (no input)
# output:
# 1. a message string
def pending_response_generator():
    try:
        pending_reponse = [
            "Just a moment. Thank you...",
            "Processing your request...",
            "Working...",
        ]
        response_choice = random.randint(1, len(pending_reponse)) - 1
        return pending_reponse[response_choice]
    except Exception as e:
        print('Error(pending_response_generator(): ', e)

# call the chatbot to process the requests
# input:
# 1. sender: sender ID or user ID
# 2. message: the user prompt
# 3. job_id: the unique job ID for each prompt request
# output:
# 1. update the global variable: jobs[str(job_id)]. The response from chatbot would be stored in the jobs{} and wait for the web client to retrieve it
def chatbot_generate_response(
    sender,
    message,
    job_id,
):
    try:
        # understanding the prompt
        with bot_lock:
            user_prompt_dict = bot.identify_user_input(
                user_prompt=message
            )
        # the creation time is for removing old responses in jobs{} (some users might get offline before receiving the responses)
        user_prompt_dict['creation_time'] = datetime.datetime.now()

        with user_background_lock:
            # saving or updating user background
            if user_background.get(sender):
                # investment
                ## investment is true if the user expressed investment intent or mentioned risk tolerance
                if user_prompt_dict.get('investment') or user_prompt_dict.get('risk_tolerance') is not None:
                    user_background[sender]['investment'] = True
                # investment explanation
                ## investment explanation is mentioned in the latest prompt, apply the latest request
                if user_prompt_dict.get('investment_explanation') is not None:
                    user_background[sender]['investment_explanation'] = user_prompt_dict.get('investment_explanation')
                # risk_tolerance
                ## if user mentioned risk tolerance, update the user background
                if user_prompt_dict.get('risk_tolerance') is not None:
                    if user_prompt_dict.get('risk_tolerance') != user_background.get(sender).get('risk_tolerance'):
                        user_background[sender]['risk_tolerance'] = user_prompt_dict.get('risk_tolerance')
                # investment_date
                ## if user mentioned investment date, update the user background
                if user_prompt_dict.get('investment_date') is not None:
                    user_background[sender]['investment_date'] = user_prompt_dict.get('investment_date')
            
            elif user_prompt_dict.get('risk_tolerance') is not None:
                # created the user background for new users
                user_background[sender] = user_prompt_dict
                # investment
                ## investment is true if the user expressed investment intent or mentioned risk tolerance
                user_background[sender]['investment'] = True
            else:
                # created the user background for new users
                user_background[sender] = user_prompt_dict

        # classifying the prompt into categories
        with user_background_lock, bot_lock:
            prompt, response_type = bot.classify_response(
                user_prompt_dict=user_background[sender],
            )

        # if response_type == 1:
        #     with bot_lock:
        #         chatbot_response = bot.generate_response(
        #             prompt=prompt
        #         )
        #     chatbot_response = re.sub(r".*Assistant:", "", chatbot_response, flags=re.MULTILINE)
        #     # avoid the system prompt being included in the response
        #     if '```html' in chatbot_response:
        #         chatbot_response = re.sub(r".*```html", "", chatbot_response, flags=re.MULTILINE)
        #     if '<body>' in chatbot_response:
        #         chatbot_response = re.sub(r"<body.?>", "", chatbot_response, flags=re.MULTILINE)
        #     if '</body>' in chatbot_response:
        #         chatbot_response = re.sub(r"<\/body.?>", "", chatbot_response, flags=re.MULTILINE)
        # else:
            # for repsonse type 2, 3 and 4, the prompt was the chatbot response
        chatbot_response = prompt

        with jobs_lock:
            creation_time = jobs.get(str(job_id)).get('creation_time')
            # saving chatbot response to jobs{}
            jobs[str(job_id)] = {
                'status': 'completed',
                'user_message': message,
                'chatbot_response': chatbot_response,
                'sender': sender,
                'creation_time': creation_time
            }
    except Exception as e:
        print('Error(chatbot_generate_response()): ', e)

# the endpoint for the website
# input: (for POST method only)
# 1. POST request with sender: sender ID
# 2. POST request with message: user prompt
# output:
# 1. HTML web page (for GET method)
# 2. JSON object to tell users to wait or raise the error message
# change:
# 1. call the chatbot to process the prompt
@app.route('/', methods=['GET', 'POST'])
def chatbot_new_job_api():
    try:
        if request.method == 'GET':
            return render_template('index.html'), 200

        data = request.get_json()

        if not data:
            # 400 Bad Request
            return {
                'error': 'JSON missing',
                'text': '',
                'sender': None,
                'job_id': '',
                'status': 'failed'
            }, 400

        sender = data.get('sender')
        message = data.get('message')

        # generate new sender id for new or unknown users/ senders
        if not sender:
            sender = str(datetime.datetime.now())
            sender = sender.replace(' ', '_')
            sender = sender.replace(':', '-')
            sender = 'sender' + str(sender)
        # generating job id
        job_id = str(datetime.datetime.now())
        job_id = job_id.replace(' ', '_')
        job_id = job_id.replace(':', '-')
        job_id = 'job_id' + str(job_id)

        with jobs_lock:
            jobs[str(job_id)] = {
                'status': 'pending',
                'user_message': message,
                'chatbot_response': pending_response_generator(),
                'sender': sender,
                'creation_time': datetime.datetime.now()
            }

        # run a new thread to generate response
        threading.Thread(
            target=chatbot_generate_response, 
            args=(
                str(sender),
                str(message),
                str(job_id),
                )
            ).start()

        return{
            'sender':sender,
            'text': pending_response_generator(),
            'job_id': str(job_id),
            'status': 'pending'
        }, 200
        
    except Exception as e:
        print('Error(chatbot_new_job_api()): ', e)
        return {
            'error': str(e),
            'text': '',
            'sender': None,
            'job_id': '',
            'status': 'failed'
        }, 500

# showing the web page about
# input: (no specific input, just a GET request)
# output:
# 1. HTML web page
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html'), 200

# showing the license
# input: (no specific input, just a GET request)
# output:
# 1. the license text file
@app.route('/apache_license', methods=['GET'])
def apache_license():
    return render_template('LICENSE.txt'), 200, {'Content-Type': 'text/plain'}

# reply to users the status or the result of their previous requests
# input:
# 1. GET request with job_id
# output:
# 1. the pending status; or
# 2. the completed response from the chatbot; or
# 3. error message and failed status
@app.route('/status', methods=['GET'])
def chatbot_get_status():
    try:
        job_id = request.args.get('job_id')
        if not job_id:
            return {
                'error': 'job_id missing',
                'text': 'The job is missing.',
                'sender': None,
                'job_id': '',
                'status': 'failed'
            }, 400
        with jobs_lock:
            this_job = jobs.get(str(job_id))

            if this_job.get('status') == 'completed':
                jobs.pop(str(job_id), None)
                return {
                    'sender': this_job.get('sender'),
                    'text': this_job.get('chatbot_response'),
                    'job_id': str(job_id),
                    'status': this_job.get('status')
                }, 200
            return {
                'sender': this_job.get('sender'),
                'text': pending_response_generator(),
                'job_id': str(job_id),
                'status': this_job.get('status')
            }
    except Exception as e:
        print('Error(chatbot_get_status()): ', e)
        return {
            'error': str(e),
            'text': '',
            'sender': None,
            'job_id': '',
            'status': 'failed'
        }, 500
