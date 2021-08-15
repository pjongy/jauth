import datetime
import random
import re
import string

from dateutil.parser import parse

from jauth.util.exception.parser import DatetimeParsingError

KST = datetime.timezone(datetime.timedelta(hours=9), "KST")
UTC = datetime.timezone(datetime.timedelta(hours=0), "UTC")
email_validator = re.compile(
    r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", re.IGNORECASE
)


def json_encoder(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def to_string(string):
    if isinstance(string, bytes):
        return string.decode()

    if isinstance(string, int):
        return str(string)

    if isinstance(string, str):
        return string

    raise TypeError(f"Passed value is not str or bytes or int ({type(string)})")


def string_to_utc_datetime(datestring):
    if datestring:
        try:
            datetime_ = parse(datestring)
        except ValueError as e:
            raise DatetimeParsingError(e)

        if not datetime_.tzinfo:
            return datetime_.replace(tzinfo=UTC)
        else:
            return datetime_.astimezone(UTC)


def datetime_to_utc_datetime(datetime_):
    if datetime_:
        if not datetime_.tzinfo:
            return datetime_.replace(tzinfo=UTC)
        else:
            return datetime_.astimezone(UTC)


def datetime_to_kst_datetime(datetime_):
    if datetime_:
        if not datetime_.tzinfo:
            return datetime_.replace(tzinfo=KST)
        else:
            return datetime_.astimezone(KST)


def utc_now() -> datetime.datetime:
    current_time = datetime.datetime.now(UTC)
    return current_time


def kst_now() -> datetime.datetime:
    current_time = datetime.datetime.now(KST)
    return current_time


def random_string(length=8):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def object_to_dict(obj) -> dict:
    if not hasattr(obj, "__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(object_to_dict(item))
        else:
            element = object_to_dict(val)
        result[key] = element
    return result


def is_valid_email(email: str):
    return re.match(email_validator, email) is not None


def is_valid_account(account: str):
    return account.isalnum()


def is_valid_password(password: str) -> bool:
    return len(password) >= 8
