import requests
import openai
from db_service import insert_post
from dotenv import load_dotenv
import os
load_dotenv()

circle_key = os.getenv("CIRCLE_API")
circle_headers = {
'Authorization': f'Token {circle_key}'
}

def send_to_gpt(message,system_prompt,r="None"):
    openai.api_key = os.getenv("GPT_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (system_prompt),
            },
            {"role": "user", "content": message}
        ]
    )
    rewrite = response["choices"][0]["message"]["content"]
    if r.lower() == "post":
        title = rewrite.split('\n')[0]
        description = ''.join(rewrite.split('\n')[1:])
        return title, description
    else:
        return rewrite


def like_post(post_id, email):
    url = f"https://app.circle.so/api/v1/posts/{post_id}/likes?user_email={email}"
    requests.post(url,headers=circle_headers)

def comment_on_post(community_id, space_id, post_id, body, user_email):
    url = "https://app.circle.so/api/v1/comments?"
    system_prompt = """You are an expert comment writer who creates concise, relevant, and engaging comments on posts. Your comments should be natural, friendly, and supportive while
    staying true to the topic. Keep them short, thoughtful, and avoid sounding robotic or generic. Only return the comment, without any additional explanations."""
    payload = {"community_id": community_id,
               "space_id": space_id,
               "post_id": post_id,
               "body": body,
               "user_email": user_email}
    
    response = requests.post(url, headers=circle_headers, data=payload)


def create_post(community_id, space_id, email, title, description, url):
    system_prompt = """You are an expert content rewriter who transforms text into a unique format
to avoid plagiarism while preserving the original meaning.
Rewrite the provided Reddit post with the title on the first line, followed by the description.
Ensure the content is rephrased and structured differently, maintaining clarity and relevance, 
without adding any labels Such as Title: or Description: only the content straight away or any extra commentary. 
DO NOT EVER INCLUDE THE WORD TITLE/DESCRIPTION"""

    message = f"""
Title: {title}
Descriptiom: {description}
"""
    original_title = title
    original_description = description
    url = f"https://app.circle.so/api/v1/posts?"
    title, description = send_to_gpt(message=message, system_prompt=system_prompt, r="post")
    payload={"space_id": space_id,
            "community_id": community_id,
            "user_email": email,
            "is_comments_enabled": True,
            "is_liking_enabled": True,
            "name": title,
            "body": description}
    
    response = requests.request("POST", url, headers=circle_headers, data=payload)
    if response.status_code == 200:
        print("Post Created")
        data  = response.json() 
        post_id = data['post']['id']
        insert_post(original_title, original_description, title, description, post_id, space_id, url)
