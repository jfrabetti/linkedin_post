import os
import requests

def headers(access_token):
    '''
    Make the headers to attach to the API call.
    '''
    headers = {
    'Authorization': f'Bearer {access_token}',
    'cache-control': 'no-cache',
    'X-Restli-Protocol-Version': '2.0.0'
    }
    return headers

def get_user_id(access_token):

    hdrs = headers(access_token)
    response = requests.get("https://api.linkedin.com/v2/userinfo", headers={'Authorization': f'Bearer {access_token}'})
    r = response.json()

    if 'sub' not in r:
        print("LinkedIn user id query failed.")
        print(r)
    else:
        user_id = r['sub']

    return user_id

def make_post( access_token, msg ):

    hdrs = headers(access_token)
    #print("LinkedIn access_token: ", access_token)
    
    user_id = get_user_id(access_token)
    #print("LinkedIn user_id: ", user_id)
    
    if user_id:
        post_data = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": msg
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        if True:
            r = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=hdrs, json=post_data)

            r = r.json()

            if 'id' in r and r['id'].find("urn:li:share:") == 0:
                print("SUCCESS!")
            else:
                print("Post failed.")
                print(r)
            
            

def post(msg):
    access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]

    make_post(access_token,msg)

if __name__ == "__main__":

    post("foo")
