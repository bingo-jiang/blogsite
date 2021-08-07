import datetime


def filename_format(username, file_name):
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_type = str(file_name).split(".")[-1]
    final_name = str(username) + '_' + current_datetime + '.' + file_type
    return final_name
