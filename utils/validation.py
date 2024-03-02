import re

def validate_email(email: str) -> bool:
    regex = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

    return bool(re.fullmatch(regex, email))

def validate_password(password: str) -> bool:
    if len(password) < 8:
        print(1)
        return False
    elif re.search('[0-9]',password) is None:
        print(2)
        return False
    elif re.search('[A-Z]',password) is None: 
        print(3)
        return False
    elif re.search('[^a-zA-Z0-9]',password) is None: 
        print(4)
        return False
    return True


    return bool(re.fullmatch(r"^(?=\S{6,20}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])", password))

if __name__ == "__main__":
    print(validate_password(input()))