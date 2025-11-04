import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flasgger import Swagger

import post_generator
import linkedin_post

app = Flask(__name__, template_folder="templates")
# Enable CORS for all routes
CORS(app)

# Swagger UI Configuration
swagger = Swagger(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gen_topics', methods=['POST'])
def gen_topics():

    data         = request.get_json()  # Parse the JSON from the request
    sess_label   = data.get('sess_label')
    sess_subject = data.get('sess_subject')
    topic_count  = data.get('topic_count')
    status_msg   = ""
    ok_fl        = False
    topicL       = []
    topicN       = 0
    
    
    if not sess_label:
        status_msg += "Invalid session label. "
        
    if not topic_count or not topic_count.isdigit():
        status_msg += "Invalid topic count. "

    if status_msg == "":
        args = post_generator.session_setup(sess_label)
        
        r = post_generator.generate_topic_list(args,sess_subject,int(topic_count))

        sess_subject = r["subject"]
        topicL = r['topicL']
        topicN = len(topicL)
        ok_fl = True

    if not ok_fl and not sess_subject:
        status_msg += "Invalid sess_subject. "        

        
    # Return a JSON response
    return jsonify({
        "sess_label": sess_label,
        'topicL':     topicL,
        'topic_count':  topicN,
        'sess_subject': sess_subject,
        'status_msg':   status_msg if status_msg else "Ok",
        'ok_fl':        ok_fl
    })    
    
@app.route('/gen_facts', methods=['POST'])
def gen_facts():

    r = request.get_json()  # Parse the JSON from the request
    sess_label   = r.get('sess_label')
    sess_subject = r.get('sess_subject')
    status_msg = ""
    factL = []
    ok_fl = False
    
    if status_msg == "":
        args = post_generator.session_setup(sess_label)
        
        factL = post_generator.generate_facts(args,sess_subject)

        ok_fl = True

    return jsonify({
        "sess_label": sess_label,
        'factL':      factL,
        'sess_subject': sess_subject,
        'status_msg':   status_msg if status_msg else "Ok",
        'ok_fl':        ok_fl
    })    

@app.route('/gen_posts', methods=['POST'])
def gen_posts():

    r = request.get_json()  # Parse the JSON from the request
    sess_label   = r.get('sess_label')
    status_msg = ""
    postL = []
    ok_fl = False
    
    if status_msg == "":
        args = post_generator.session_setup(sess_label)
        
        postL = post_generator.generate_posts(args)

        ok_fl = True

    return jsonify({
        "sess_label": sess_label,
        'postL':      postL,
        'status_msg':   status_msg if status_msg else "Ok",
        'ok_fl':        ok_fl
    })    

@app.route('/publish', methods=['POST'])
def publish():

    r = request.get_json()  # Parse the JSON from the request
    sess_label   = r.get('sess_label')
    post_id      = r.get('post_id')
    status_msg = ""
    ok_fl = False
    
    if status_msg == "":
        args = post_generator.session_setup(sess_label)

        post_msg = post_generator.post_id_to_msg( args.cand_db_json_path, post_id )

        print(f"Publishing:{post_id}");
        linkedin_post.post(post_msg)

        ok_fl = True


    return jsonify({
        "sess_label": sess_label,
        'status_msg':   status_msg if status_msg else "Ok",
        'ok_fl':        ok_fl
    })    

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (JS, CSS, etc.)"""
    return send_from_directory(app.static_folder, filename)
       
if __name__ == '__main__':

    if not "OPENAI_API_KEY" in os.environ:
        print("The 'OPENAI_API_KEY' environmental variable has not been set.")
        
    if not "LINKEDIN_ACCESS_TOKEN" in os.environ:
        print("The 'LINKEDIN_ACCESS_TOKEN' environmental variable has not been set.")
        
    app.run(debug=True)
