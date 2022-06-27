import csv
import pandas as pd


def dataframe():
    with open('WCWA.txt', encoding='utf8') as f:
        lines = []
        for line in f:
            if line[6:10] == '2021' or line[6:10] == '2022':
                lines.append(line[:-1])

    lines_list = []
    for line in lines:
        date = line[:10]
        time = line[12:17]
        message = line[20:]
        Msg = message.split(':', 1)
        if Msg[1:]:
            name = Msg[0]
            msg = Msg[1]
        else:
            name = 'Group Notification'
            msg = Msg[0]
        lines_list.append([date, time, name, msg])

    header = ['date', 'time', 'name', 'msg']
    with open('data.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(lines_list)

    data = pd.read_csv('data.csv')
    data['date-time'] = data['date'] + " " + data['time']
    data['date-time'] = pd.to_datetime(data['date-time'], format="%d/%m/%Y %H:%M")
    data.drop(['date', 'time'], axis=1, inplace=True)
    data['year'] = data['date-time'].dt.year
    data['month'] = data['date-time'].dt.month_name()
    data['only-date'] = data['date-time'].dt.date
    data['day'] = data['date-time'].dt.day
    data['hour'] = data['date-time'].dt.hour
    data['minute'] = data['date-time'].dt.minute
    data['day_name'] = data['date-time'].dt.day_name()

    period = []
    for hour in data[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str("00"))
        elif hour == 0:
            period.append(str("00") + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    data['period'] = period

    return data
