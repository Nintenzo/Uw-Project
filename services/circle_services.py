import requests
import openai
from .db_service import insert_post
from dotenv import load_dotenv
from .db_service import get_gender
from .seen_service import last_seen
from settings.sentiments_keywords import sentiments
import os
import random
import time

load_dotenv()
circle_key = os.getenv("CIRCLE_API")
circle_headers = {
    'Authorization': f'Token {circle_key}'
}


def send_to_gpt(message, is_post, final_idenitity, original_identity, n=30):
    sentiment = random.choice(sentiments)
    system_prompt_post = f"""You are posting as a '{final_idenitity} {original_identity}' You are an expert content rewriter who transforms text into a unique format
    to avoid plagiarism while preserving the original meaning.
    Rewrite the provided Reddit post with the title on the first line, followed by the description.
    Ensure the content is rephrased and structured differently, maintaining clarity and relevance, 
    without adding any labels Such as Title: or Description: only the content straight away or any extra commentary.
    DO NOT EVER INCLUDE THE WORD TITLE/DESCRIPTION AND THE TITLE MUST MUST MUST BE LESS THAN 230 CHARACTERS NO MORE EVEN IF THE ORIGINAL TITLE IS MORE THAN 230 YOU NEED TO MAKE IT SHORTER THAN THAT 
    THAN THAT AND DO NOT INCLUDE ANYTHING THAT MAKE IT RELEATED TO A SPECIFIC SOCIAL MEDIA PLATFORM """

    system_prompt_comment = f"""You are commenting as a '{final_idenitity} {original_identity}'. Ensure the comment has a unique opening— You are a human participating in online discussions. When given a post, your task is to write a short,
    thoughtful, and natural-sounding comment in response to it. Your replies should sound like they were written by a real person—casual, relevant, and engaging.
    Keep your comment brief and concise, suitable for a typical online comment. Your comment type should be: {sentiment} Avoid sounding robotic, overly formal, or scripted. Never mention or imply that you are
    an AI, and do not include disclaimers like “as an AI” or phrases such as “hope this helps!” unless they naturally fit the tone.
    Your tone should match the context of the original post, whether that’s supportive, humorous, informative, or empathetic.
    **Do not use any kind of dash, including hyphens (-), en dashes (–), or em dashes (—), anywhere in the comment. Do not use them to join phrases, emphasize ideas, or for any other purpose. Use commas, periods, or separate sentences instead.**
    When appropriate, include light personal insights, relatable advice, or friendly observations. Keep responses under {n} 
    words and make sure they feel like part of a natural conversation.
    Your goal is to contribute meaningfully and seamlessly to the discussion without standing out as artificial."""

    
    openai.api_key = os.getenv("GPT_KEY")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (system_prompt_post if is_post else system_prompt_comment),
                },
                {"role": "user", "content": message}
            ]
        )
        rewrite = response["choices"][0]["message"]["content"]
    except Exception:
        time.sleep(10)
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (system_prompt_post if is_post else system_prompt_comment),
                },
                {"role": "user", "content": message}
            ]
        )
        rewrite = response["choices"][0]["message"]["content"]
        
    if is_post:
        title = rewrite.split('\n')[0]
        description = ''.join(rewrite.split('\n')[1:])
        return title, description
    else:
        return rewrite


def like_post(post_id, email):
    url = f"https://app.circle.so/api/v1/posts/{post_id}/likes?user_email={email}"
    try:
        data = requests.post(url,headers=circle_headers)
    except Exception:
        time.sleep(10)
        data = requests.post(url,headers=circle_headers)
    if data.json()['message'] == "Post has been liked":
        print(data.json()['message'])
        last_seen(email=email)
    else:
        print(data.json()['message'])
    return data.json()


def comment_on_post(space_id, post_id, user_email):
    """
    This function comments on a post.
    It first fetches the post and then sends the post to GPT to get a comment.
    It then creates a comment on the post.
    """
    gender = get_gender(user_email)
    final_idenitity = gender[0][0]
    original_identity = gender[0][1]
    community_id = os.getenv("COMMUNITY_ID")
    circle_post = f"https://app.circle.so/api/v1/posts/{post_id}?community_id={community_id}"
    r = requests.get(circle_post, headers=circle_headers)
    title = r.json()['name']
    description = r.json()['body']['body']

    message = f"""
    Title: {title}
    Description: {description}
    """
    body = send_to_gpt(message=message, is_post=False, final_idenitity=final_idenitity, original_identity=original_identity, n=random.randint(10,70))
    url = "https://app.circle.so/api/v1/comments?"
    payload = {"community_id": community_id,
               "space_id": space_id,
               "post_id": post_id,
               "body": body,
               "user_email": user_email}
    try:
        response = requests.post(url, headers=circle_headers, data=payload)
    except Exception:
        time.sleep(10)
        response = requests.post(url, headers=circle_headers, data=payload)
    if response.status_code == 200:
        print("Comment Created")
        last_seen(email=user_email)
    else:
        print("Comment Not Created")


def create_post(space_id, email, title, description, url):
    try:
        gender = get_gender(email)
        final_idenitity = gender[0][0]
        original_identity = gender[0][1]
        message = f"""
        Title: {title}
        Description: {description}
        """
        original_title = title
        original_description = description
        circle_url = "https://app.circle.so/api/v1/posts?"
        title, description = send_to_gpt(message=message, is_post=True, final_idenitity=final_idenitity, original_identity=original_identity)
        payload = {
                    "space_id": space_id,
                    "community_id": os.getenv("COMMUNITY_ID"),
                    "user_email": email,
                    "is_comments_enabled": True,
                    "is_liking_enabled": True,
                    "name": title,
                    "body": description
                }
        try:
            response = requests.request("POST", circle_url, headers=circle_headers, data=payload)
        except Exception:
            time.sleep(10)
            response = requests.request("POST", circle_url, headers=circle_headers, data=payload)
        if response.status_code == 200:
            print("Post Created")
            last_seen(email)
            data = response.json()
            post_id = data['post']['id']
        # needed_likes = random.randint(200,1050)
            needed_likes = random.randint(80,180)
            needed_comments = random.randint(int(needed_likes * 0.08), int(needed_likes * 0.15))
            insert_post(original_title, original_description, title, description, post_id, space_id, url, needed_likes=needed_likes, needed_comments=needed_comments)
    except Exception as e:
        print(e)
        print(title)
        time.sleep(55)
