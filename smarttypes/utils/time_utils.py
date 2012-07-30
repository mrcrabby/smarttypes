from datetime import datetime, timedelta

def timedelta_to_secs(delta):
    return (delta.days * 24 * 60 * 60) + delta.seconds

def base_datetime(dt):
    return datetime(dt.year, dt.month, dt.day)

def year_weeknum_strs(start_w_this_dt, number_of_weeks, forward=False):
    """
    returns a list like ['2011_00', '2011_01']
    """
    return_list = []
    for i in range(number_of_weeks):
        if forward:
            new_week = start_w_this_dt + (i * timedelta(days=7))
        else:
            new_week = start_w_this_dt - (i * timedelta(days=7))
        return_list.append(new_week.strftime('%Y_%U'))
    if forward:
        return_list.reverse()
    return return_list
    




