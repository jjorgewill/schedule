import random
import string

from datetime import timedelta


def generate(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def date_range(start_date,end_date):
    for n in range(int((end_date-start_date).days)):
        yield start_date + timedelta(n)