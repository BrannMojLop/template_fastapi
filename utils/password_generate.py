from random import choice


def password_generate(large):
    values = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
    password = ""
    password = password.join([choice(values) for i in range(large)])
    return password
