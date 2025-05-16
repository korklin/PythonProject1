
def filter_by_state(data_base: list, state='EXECUTED') -> list:
    new_data_base = []
    for data in data_base:
        if data['state'] == state:
            new_data_base.append(data)
        else:
            continue
    return new_data_base


user_base = [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
             {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
             {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
             {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}]
print(filter_by_state(user_base, 'EXECUTED'))

#def sort_by_date(data_base: list, )