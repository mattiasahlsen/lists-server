import random
import string

random_char = lambda: random.SystemRandom().choice(
    string.ascii_letters + string.digits
)
def random_string(N = 16):
    return ''.join(random_char() for _ in range(N))

