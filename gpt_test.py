import openai
import os
from dotenv import load_dotenv

load_dotenv()

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

system_prompt = """You are an expert content rewriter who transforms text into a unique format
to avoid plagiarism while preserving the original meaning.
Rewrite the provided Reddit post with the title on the first line, followed by the description.
Ensure the content is rephrased and structured differently, maintaining clarity and relevance, 
without adding any labels Such as Title: or Description: only the content straight away or any extra commentary. 
DO NOT EVER INCLUDE THE WORD TITLE/DESCRIPTION"""

title = "Now we know. It was Retail CEOS who got to Trump on Monday"
description = """
As reported by Axios, Trump was shaken Monday after meeting with CEO’s of top retail companies like Target. They warned him that disrupted supply chains due to his China tariffs would mean empty shelves and soaring prices very soon. You can imagine how the optics of bare shelves all around the country would look.

Maybe they will get exemptions as Trump’s crony capitalism marches on but a huge number of small businesses won’t and will go under.

Somewhere Xi is smirking.

https://dailyboulder.com/shaken-trump-makes-u-turn-on-tariffs-after-being-rattled-by-dire-ceo-warning/"""

message = f"""
Title: {title}
Descriptiom: {description}
"""
x, y = send_to_gpt(system_prompt=system_prompt,message=message, r='post')
print(x)
print(y)
