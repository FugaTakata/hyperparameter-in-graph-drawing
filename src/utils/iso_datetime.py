# Standard Library
import datetime


def get_now_jst():
    tz_jst = datetime.timezone(datetime.timedelta(hours=+9))
    dt_now_jst = datetime.datetime.now(tz=tz_jst)
    dt_now_jst_iso = datetime.datetime.isoformat(dt_now_jst)

    return dt_now_jst_iso
