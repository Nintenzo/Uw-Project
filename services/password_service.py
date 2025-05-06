import random
import string

def generate_password(length=12):
	if length < 4:
		raise ValueError("Password length should be at least 4")

	symbols = "@-_!#$()*&^%"
	allowed_chars = string.ascii_letters + string.digits + symbols

	password_chars = [
		random.choice(string.ascii_lowercase),
		random.choice(string.ascii_uppercase),
		random.choice(string.digits),
		random.choice(symbols),
	]

	password_chars += random.choices(allowed_chars, k=length - len(password_chars))
	random.shuffle(password_chars)

	return ''.join(password_chars)