0. Get Openai API key here: https://platform.openai.com/settings/organization/api-keys
and save it. Eventually it will be exported like this:  `export OPENAI_API_KEY=<key>`

1. Get LinkedIn API access token:

- Sign into developer/linkedin.com
- If you do not have a company then create one.
- Be sure the 'page' associated with the company is the company 'dashboard' page.
- "My apps" | "Create app"
- Tab: "Products" select "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect"
- Tab: "Auth" in right column select link "OAuth 2.0 tools"
- "Create a new access token".
- Select all permission scopes.
- Generate token.
- Note that it is not necessary to 'Verify' the app on the 'Settings' tab.

Save the token. Eventually it will be exported like this:
`export LINKEDIN_ACCESS_TOKEN=<token>`

2. Setup the application environment

```
mkdir linkedin_post; cd linkedin_post  # Create the application folder
pyenv install 3.12.9
pyenv shell 3.12.9
python -m venv venv           # Create the app python environment.
source venv/bin/activate      # Activate the python environment
pip install --upgrade pip    # Get the latest pip.
pip install -r requirements.txt # Install python dependencies.
export OPENAI_API_KEY=<key>          # See step 0 above.
export LINKEDIN_ACCESS_TOKEN=<token> # See step 1 above.
```

3. Run the application server: `python flask_server.py`

4. Open the application web UI:  `http:\\localhost:5000`


5. Using the program:

- Generate a series of titles and descriptions for a post on a particular subject.
  + Enter a one word 'Session Label' to use as an identifier for
    associating all data generated during this program session. This can be used to
    later retrieve information.
  + Enter a subject for a new post. (e.g. Recent advances in generative ai technology.)
  + Set the number of title/descriptions to generate.
  + Click 'Generate Topics' and wait for the topic list to populate.

- Generate useful facts associated with each of the title/descriptions in the topic list
  by clicking the 'Generate Facts' button at the bottom of the window and
  wait for the facts list to populate.

- Generate candidate posts by clicking the 'Generate Posts' button on the bottom
  of the window and wait for the posts to generate.

- Select a post to publish by clicking the checkbox associated with it.

- Click 'Publish Selected Post' to upload the post to LinkedIn.


6. Notes:
- Results for each of the stages of post generation is cached in the
directory 'data/<session_label>.  If a given stage (e.g. topic generation, fact generation ...)
of the processing sequence is re-run then the cached data will be used
rather than making a new call to the API.  To avoid this use a new session label
or delete the associated cache file.
  + Topics cache: `data/<session_label>/topic.json`
  + Facts cache: `data/<session_label>/facts.json`
  + Post cache: `data/<session_label>/candidate_db.json`


- To do:
  + Improve/change the prompts. See `post_generator.py`
  + The post generator is designed to use multiple writing assistants
    each of which writes in a different style. Add more assistants to
    `post_generate.py sessionArgsD.assL`.
  + Improve the application CSS.
  + Clear the screen.
  + Load the index.html.

