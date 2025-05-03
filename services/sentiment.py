import random

def generate_sentiment():
    sentiment_roll = random.random()

    if sentiment_roll < 0.60:
        return random.choice(["supportive", "encouraging"])
    elif sentiment_roll < 0.85:
        return random.choice(["question-asking", "clarifying"])
    else:
        return random.choice(["minor disagreements", "different experiences"])

