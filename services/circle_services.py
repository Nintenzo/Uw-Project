import requests
import openai
from .db_service import insert_post, get_random_user_email
from .sentiment import generate_sentiment
from dotenv import load_dotenv
from .db_service import get_gender
from .seen_service import last_seen
from settings.sentiments_keywords import sentiments
from math import floor
import os
import random
import time

load_dotenv()
circle_key = os.getenv("CIRCLE_API")
circle_headers = {
    'Authorization': f'Token {circle_key}'
}
community_id = os.getenv("COMMUNITY_ID")
def send_to_gpt(message, is_post, final_idenitity, original_identity, n=30, previous_openings=None):
    sentiment = random.choice(sentiments)
    comment_type = generate_sentiment()
    system_prompt_post = f"""You are posting as a '{final_idenitity} {original_identity}' You are an expert content rewriter who transforms text into a unique format
    to avoid plagiarism while preserving the original meaning.
    Rewrite the provided Reddit post with the post type on the first line with no space or anything extra('educational', 'reference', 'question', 'emotional' , 'polls', 'hot')
    on the first line, followed by the title on the second line followed by the description.
    Ensure the content is rephrased and structured differently, maintaining clarity and relevance, 
    without adding any labels Such as Title: or Description: only the content straight away or any extra commentary.
    DO NOT EVER INCLUDE THE WORD TITLE/DESCRIPTION AND THE TITLE MUST MUST MUST BE LESS THAN 230 CHARACTERS NO MORE EVEN IF THE ORIGINAL TITLE IS MORE THAN 230 YOU NEED TO MAKE IT SHORTER THAN THAT 
    THAN THAT AND DO NOT INCLUDE ANYTHING THAT MAKE IT RELEATED TO A SPECIFIC SOCIAL MEDIA PLATFORM IMPORT NOTE IF THE DESCIRPTION I PROVIDED IS EMPTY TRY TO CREATE A DESCRIPTION YOURSELF IF YOU CAN'T THEN JUST RETURN FALSE IN ALL 3 LINES
    """

    spelling = random.choices(["True", "False"], [0.75, 0.25])
    respect = random.choices(["True", "False"], [0.75, 0.25])

    if not is_post and previous_openings:
        openings_text = "\n".join([f"- {o}" for o in previous_openings])
        openings_section = f"Here are the openings of previous comments on this post:\n{openings_text}\nDo NOT start your comment with any of these openings or anything similar. Make your opening sentence unique and different from the above.\n"
    else:
        openings_section = ""

    system_prompt_comment = f"""{openings_section}You are commenting as a '{final_idenitity} {original_identity}'.
    Start every comment with a distinct, creative, and natural opening sentence that is different from previous comments. Do not use generic phrases like
    “That is too sad,” “That’s interesting,”
    or similar. Avoid repeating the same structure or wording at the beginning of your comments. For example, you might start with a personal reaction, a question,
    or a specific observation, 
    such as: “I remember facing something similar...”, “Have you tried...?”, “It’s amazing how...”, etc. But always make your opening unique and relevant to the post.
    You are a human participating in online discussions. When given a post, your task is to write a short, thoughtful, and natural-sounding comment in response to it. 
    Your replies should sound like they were written by a real person—casual, relevant, and engaging.
    Keep your comment brief and concise, suitable for a typical online comment. Your comment type should be: {sentiments} and it should be 100% {comment_type} You can use slang language Avoid sounding robotic,
    overly formal, or scripted. Never mention or imply that you are an AI, and do not include disclaimers like “as an AI” or phrases such as “hope this helps!” unless they naturally fit the tone.
    Your tone should match the context of the original post, whether that’s supportive, humorous, informative, or empathetic.
    **Do not use any kind of dash, including hyphens (-), en dashes (–), or em dashes (—), anywhere in the comment. Do not use them to join phrases, emphasize ideas,
    or for any other purpose. Use commas, periods, or separate sentences instead.**
    When appropriate, include light personal insights, relatable advice, or friendly observations. Keep responses under {n} 
    words and make sure they feel like part of a natural conversation.
    Your goal is to contribute meaningfully and seamlessly to the discussion without standing out as artificial."""

    # Add-on behaviors
    spelling_mistakes = "YOU MUST HAVE SPELLING MISTAKES"
    no_cap_punc = "YOU MUST NOT RESPECT CAPITILIZATION AND PUNCUATIONS"
    no_sentence_caps = "YOU MUST NOT START SENTENCES WITH CAPITAL LETTERS"

    # Imperfect variations
    imperfect_variants = [
        system_prompt_comment + "\n" + spelling_mistakes,
        system_prompt_comment + "\n" + no_cap_punc,
        system_prompt_comment + "\n" + spelling_mistakes + " " + no_cap_punc
    ]

    if random.random() < 0.88:
        final_prompt = system_prompt_comment
    else:
        final_prompt = random.choice(imperfect_variants)

    if random.random() < 0.5:
        final_prompt += "\n" + no_sentence_caps

    system_prompt_comment = final_prompt
        
    openai.api_key = os.getenv("GPT_KEY")
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
        sentiment = rewrite.split('\n')[0]
        title = rewrite.split('\n')[1]
        description = ''.join(rewrite.split('\n')[2:])
        return sentiment, title, description
    else:
        return rewrite

def like_post(post_id, email):
    post_data = get_post_data(post_id, community_id)
    poster_email = post_data['user_email']
    while email == poster_email:
        email = get_random_user_email()
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


def get_post_data(post_id, community_id):
    """
    This function fetches the post data from Circle API.
    It returns the post data in JSON format.
    """
    url = f"https://app.circle.so/api/v1/posts/{post_id}?community_id={community_id}"
    try:
        response = requests.get(url, headers=circle_headers)
    except Exception:
        time.sleep(10)
        response = requests.get(url, headers=circle_headers)
    return response.json()

def comment_on_post(space_id, post_id, user_email, previous_openings=None):
    """
    This function comments on a post.
    It first fetches the post and then sends the post to GPT to get a comment.
    It then creates a comment on the post.
    """
    gender = get_gender(user_email)
    final_idenitity = gender[0][0]
    original_identity = gender[0][1]
    post_data = get_post_data(post_id, community_id)
    title = post_data['name']
    description = post_data['body']['body']
    message = f"""
    Title: {title}
    Description: {description}
    """
    body = send_to_gpt(message=message, is_post=False, final_idenitity=final_idenitity, original_identity=original_identity, n=random.randint(10,70), previous_openings=previous_openings)
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
        return body
    else:
        print("Comment Not Created")
        return None

def assign_comments(sen, needed_likes):
    sen = sen.lower().strip()
    if sen == "educational" or sen == "reference":
        return needed_likes * random.uniform(0.04, 0.07)
    elif sen == "question" or sen == "emotional":
        return needed_likes * random.uniform(0.12, 0.18)
    elif sen == "polls" or sen == "hot":
        return needed_likes * random.uniform(0.20, 0.30)
   
def create_post(space_id, email, title, description, url):
    
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
    sen, title, description = send_to_gpt(message=message, is_post=True, final_idenitity=final_idenitity, original_identity=original_identity)
    if sen.lower().strip() == "false":
        print("GPT returned false, skipping post creation.")
        return "false"
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
        needed_likes = random.randint(60, 400)
        try:
            needed_comments = floor(assign_comments(sen, needed_likes))
        except Exception:
            delete_url = f"https://app.circle.so/api/v1/posts/{post_id}?community_id={community_id}"
            response = requests.delete(delete_url, headers=circle_headers)
            print(response.json())
            print("Error during comment assignment")
            return "false"
        insert_post(original_title, original_description, title, description, post_id, space_id, url, needed_likes=needed_likes, needed_comments=needed_comments)
        return "not false"