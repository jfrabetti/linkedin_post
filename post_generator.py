import os
import json
import time
import types
import pprint
import pickle
from string import Template
from openai import OpenAI

def title_to_folder_name( title ):
    return title.replace(':',' ').replace('  ',' ').replace(' ','_')

def session_setup( session_label ):
    # Create the program context and set program constants

    sessionArgsD = dict(
        session_label = session_label,
        openai = None,
        out_dir = "data",
        topic_fname = "topic.json",
        facts_fname = "facts.json",
        cand_db_fname = "candidates_db.json",
        cand_db_json_path = None,
        facts_folder = "facts",
        posts_folder = "posts",
        html_template_fname = "html_template.html",
        facts_dir = None,
        asstL = [ ("sm_post_writer","asst_WomMsa2aYXsJiGvx9sTMn1kV"),
                  ("sm_linkedin_writer", "asst_wu1fdguNKMViz29dOdWY25bO"),
                  ("sm_pirate_writer", "asst_tZTX9AlLMDWlDhGAf1DNPv85") ],
    )

    # Turn dict into class for key.value
    args = types.SimpleNamespace(**sessionArgsD)
    
    # Open OpenAI store openai in args
    args.openai = OpenAI()

    # if the output path does not already exist then create it
    args.out_dir = os.path.join(args.out_dir,args.session_label)
    if not os.path.isdir(args.out_dir):
        os.makedirs(args.out_dir,exist_ok=True)

    # create the base 'facts' directory
    args.facts_dir = os.path.join(args.out_dir,args.facts_folder)
    if not os.path.isdir(args.facts_dir):
        os.makedirs(args.facts_dir,exist_ok=True)

    args.cand_db_json_path = os.path.join(args.out_dir,args.cand_db_fname)
        
    return args

def generate_topic_list( args, subject, topic_count ):

    dev_prompt = """
    You are an assistant who is able to to generate potential timely topics
    and descriptions for automated social media posts."""

    asst_prompt = """
    The output format should be a list in JSON, labelled "posts",  where each list element has the format:
    { "title":$TITLE, "description":$DESCRIPTION } where $TITLE and $DESCRIPTION
    are replaced with the generated topic and descriptions."""
    
    user_prompt = f"""
    Generate {topic_count} topic titles with one sentence descriptions for social media posts
    on subects related to {subject}."""

    # Why?
    topics_query = {
        "assistant":{ "content": asst_prompt },
        "developer":{ "content": dev_prompt },
        "user":     { "content": user_prompt }
    }

    # Pass this to OpenAI chat completions
    topic_query_msgA = [ { "role":role, "content":d["content"]} for role,d in topics_query.items() ]

    result = None
    topicL = []

    fn = os.path.join(args.out_dir,args.topic_fname)

    # if the topic file already exists then return it
    if os.path.isfile(fn):
        with open(fn) as f:
            result = json.load(f)
            
    else:
        # otherwise generate a new one
        result = args.openai.chat.completions.create( model="gpt-4o-mini",
                                                      response_format={ "type":"json_object" },
                                                      messages=topic_query_msgA )

        for c in result.choices:
            for i,(key,text) in enumerate(c.message):
                if key == 'content':
                    topicL += json.loads(text)["posts"]

        fn = os.path.join(args.out_dir,args.topic_fname)
        result = dict(label=args.session_label, subject=subject, query=topics_query, topicL=topicL)
        with open(fn,"w") as f:
            json.dump(result,f)

    return result
    
    
def generate_topic_facts( args, subject, title, description ):
    
    dev_prompt = """ You are an assistant who, given a topic title and
    short description, does research to find relevant and timely
    material which will eventually be used to generate automated
    social media posts.  The material should be broken out into
    paragraphs with the following titles 'full_description','background','significance',
    'impact','statistics'.  The 'full_description' is an expanded version
    of the given topic description. The 'background' paragraphs gives an
    overview of the topic. The 'signficance' paragraphs explain why,
    and to who, the topic may be important. The 'impact' paragraphs
    should describe what impact the topic may have to certain
    audiences.  The 'statistics' field should be included if there is
    statistical or quantifiable facts related to the topic. 
    """

    asst_prompt = """
    The output format should be in JSON with the following format:
    { "title":$TITLE, "description":$DESCRIPTION,
      "full_description":$FULL_DESCRIPTION, "background":$BACKGROUND,
      "significance":$SIGNIFICANCE, "impact":$IMPACT, "statistics":$STATISTICS
    } where $TITLE and $DESCRIPTION
    are replaced with the supplied input topic and descriptions.
    and $FULL_DESCRIPTION, $SIGNFICANCE, $IMPACT, $STATISICS are
    replaced with the paragraphs with the associated titles given in the developer prompt.
    """
    
    user_prompt = f"""
    Do research for an article titled {title} which will be about {description}. The research will
    be used to generate social media posts on subects related to {subject}."""

    
    topics_query = {
        "assistant":{ "content": asst_prompt },
        "developer":{ "content": dev_prompt },
        "user":     { "content": user_prompt }
    }

    topic_query_msgA = [ { "role":role, "content":d["content"]} for role,d in topics_query.items() ]

    factsD = None
    # https://platform.openai.com/docs/api-reference/chat/create
    result = args.openai.chat.completions.create( model="gpt-4o-mini",
                                                  response_format={ "type":"json_object" },
                                                  messages=topic_query_msgA )

    for c in result.choices:
        for i,(key,text) in enumerate(c.message):
            if key == 'content':
                factsD =json.loads(text)

    if factsD is None:
        print(f"The 'facts' could not be found for the topic: {title}.");
    else:
        out_dir = os.path.join(args.facts_dir,title_to_folder_name(title))
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir,exist_ok=True)
            
        fn = os.path.join(out_dir,args.facts_fname)            
        with open(fn,"w") as f:
            json.dump(factsD,f)

    return factsD

def generate_facts( args, subject ):
    # if facts already exist, return, if not call
    factsL = []

    # form fact file name
    fact_fn = os.path.join(args.out_dir,args.facts_fname)
    if os.path.isfile(fact_fn):
        with open(fact_fn) as f:
            r = json.load(f)
            factsL = r['factL']
    else:
        # get the list of titles/descs
        topic_fn = os.path.join(args.out_dir,args.topic_fname)
        with open(topic_fn) as f:
            topics = json.load(f)

        # for each title/desc
        for d in topics['topicL']:
            print(f"Generating facts for:{d['title']}")
            factsD = generate_topic_facts(args,subject,**d)

            factsL.append(factsD)

        with open(fact_fn,"w") as f:
            json.dump({"factL":factsL},f)
        
    return factsL
        

def wait_on_run(args, run, thread):
    # async call so you can call multiple assistants
    while run.status == "queued" or run.status == "in_progress":
        run = args.openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run
        
def generate_post_via_assistant( args, facts, asst_id ):

    # generate prompt to chatgpt
    msg_content = f"""Please generate a social media post titled \"{facts.title}\".
    The short description of this post is \"{facts.description}\".
    Based on previous research a full description of the post is: \"{facts.full_description}\"
    Based on previous research some background information is: \"{facts.background}\"
    Based on previous research the significance of this topic was found to be: \"{facts.significance}\"
    Based on previous research the impact of this topic was found to be: \"{facts.impact}\"
    Based on previous research some relevant statistics for this topic were given as: \"{facts.statistics}\"
    The previous research topics are intended to produce intersting, insightful and timely posts.
    The generated post should be limited to 2000 characters and given in the JSON format as a text field name 'social_media_post'.
    Do not include the facts provided in this input prompt in the output.
    """
    #print("msg_content: ", msg_content)

    # create a thread
    thread = args.openai.beta.threads.create()

    # add a prompt/message to the thread
    msg = args.openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=msg_content )

    # submit the prompt request to the specified assistant
    run = args.openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=asst_id )

    # wait for the request to complete
    run = wait_on_run(args,run,thread)

    # store the result
    post = None
    for msg in args.openai.beta.threads.messages.list(thread_id=thread.id):
        for c in msg.content:            
            d = c.to_dict()
            s = d['text']['value']
            if s.find('social_media_post') != -1:
                z = json.loads(s)
                if 'social_media_post' in z:
                    post = z['social_media_post']                    
                    return post

    return None


def generate_posts( args ):

    docL = []
    
    if os.path.isfile(args.cand_db_json_path):        
        with open(args.cand_db_json_path) as f:
            docL = json.load(f)        
    else:
        dirL = os.listdir(args.facts_dir)
        for folder in dirL:
            facts_dir = os.path.join(args.facts_dir,folder)
            path = os.path.join(facts_dir,args.facts_fname)

            with open(path) as f:
                factsD = json.load(f)

            posts_dir = os.path.join(facts_dir,args.posts_folder)
            if not os.path.isdir(posts_dir):
                os.makedirs(posts_dir,exist_ok=True)

            if factsD is None:
                print(f"'facts' file read failed for '{path}'.")
            else:
                for asst_label,asst_id in args.asstL:
                    print(f"Generating post for '{asst_label}' in '{folder}'.")
                    post = generate_post_via_assistant(args,types.SimpleNamespace(**factsD),asst_id)

                    if post:
                        print(post)
                        fn = os.path.join(posts_dir,f"{asst_label}.txt")
                        with open(fn,"w") as f:
                            f.write(post)

        docL = generate_candidate_database(args)

    return docL


def generate_candidate_database( args ):

    def _get_post_info( args ):
        docL = []
        fdirL = os.listdir(args.facts_dir)
        for folder in fdirL:
            facts_dir = os.path.join(args.facts_dir,folder)
            facts_fn = os.path.join(facts_dir,args.facts_fname)

            with open(facts_fn) as f:
                factsD = json.load(f)

            posts_dir = os.path.join(facts_dir,args.posts_folder)

            pdirL = os.listdir(posts_dir)

            for asst_label_fname in pdirL:

                post_fname = os.path.join(posts_dir,asst_label_fname)
                asst_label = ".".join(asst_label_fname.split(".")[:-1])

                post_id = folder + "-" + asst_label

                with open(post_fname) as f:
                    post_text = f.read()

                docL.append(dict(title=factsD['title'],writer=asst_label,post=post_text,post_id=post_id))
        return docL

    
    docL = _get_post_info(args)

    with open(args.cand_db_json_path,"w") as f:        
        f.write(json.dumps(docL,indent=4,sort_keys=True))
    
    return docL

def generate_review_document( args, out_html_fname ):

    post_template = """
    <div class=post>
      <div class=post_title>
         <input type="checkbox" id="$post_id" name="$post_id" onclick="on_check('$post_id')">
         <p>$title</p>
         <p>$writer</p>
      </div>
      <div>
        $post
      </div>
    </div>
    """
    with open(args.cand_db_json_path) as f:
        docL = json.load(f)
    
    post_html = ""
    for d in docL:
        post_html += Template(post_template).substitute(**d)

    with open(args.html_template_fname) as f:
        tpl = f.read()
        s = Template(tpl).substitute(posts_list=post_html)
        with open(out_html_fname,"w") as f:
            f.write(s)

            
def generate( session_label, subject, topic_count, review_html_fname ):

    args = session_setup( session_label )

    generate_topic_list(args, subject, topic_count)
    
    generate_facts(args, subject)

    generate_posts(args)

    generate_candidate_database( args )

    generate_review_document(args, review_html_fname)

    return args.cand_db_json_path;

def post_id_to_msg( cand_db_json_path, post_id ):

    with open(cand_db_json_path) as f:
        docL = json.load(f)

        for doc in docL:
            if doc['post_id'] == post_id:
                return doc['post']

    return None

def _gen_facts_file( args ):

    factL = []
    dirL = os.listdir(args.facts_dir)
    for folder in dirL:
        facts_dir = os.path.join(args.facts_dir,folder)
        path = os.path.join(facts_dir,args.facts_fname)

        with open(path) as f:
            factsD = json.load(f)

            factL.append(factsD)

    fn = os.path.join(args.out_dir,args.facts_fname)
    with open(fn,"w") as f:
        json.dump({"factL":factL},f)
        



if __name__ == "__main__":


    topic_count = 5
    session_label = "audio_ml"
    subject = "recent developments in audio and machine learning"
    
    
    args = session_setup(session_label)

    if False:
        generate_topic_list(args,subject,topic_count)

    if False:
        generate_facts(args,subject)

    if False:
        generate_posts(args)

    if False:
        generate_candidate_database( args )

    if False:
        generate_review_document(args,"templates/review.html")

    if True:
        _gen_facts_file(args)
    
