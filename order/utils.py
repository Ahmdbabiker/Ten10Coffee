import random
import string


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_stamp_code_generator(instance):
    new_stamp_code = random_string_generator(size=8)

    qs_exists = instance.__class__.objects.filter(code=new_stamp_code).exists()
    if qs_exists:
        return unique_stamp_code_generator(instance)
    return new_stamp_code
