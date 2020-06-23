import csv
import json

"""
read(data: string)
"""
def read(data):
    try:
        x = csv.reader(data.split('\n'), delimiter=',')
        resp = []

        headers = None


        for y in x:
            if headers == None:
                headers = y
            else:
                entry = {}
                for i in range(len(y)):
                    z = headers[i]
                    entry.update({z: y[i]})
                resp.append(entry)

        return resp
    except Exception as e:
        print(e)
        return "Something went wrong"
