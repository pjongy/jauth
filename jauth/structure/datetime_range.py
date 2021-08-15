import datetime

import deserialize

from jauth.util.util import string_to_utc_datetime


@deserialize.parser("start", string_to_utc_datetime)
@deserialize.parser("end", string_to_utc_datetime)
class DatetimeRange:
    start: datetime.datetime
    end: datetime.datetime
