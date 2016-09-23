import re
import pymongo
from database_tools import DatabaseAgent
import datetime

start = datetime.datetime.now()
print(start)
agent = DatabaseAgent()

MAX_SAMPLES_IN_INSERT_MANY = 1000

keys = [
    ("t", pymongo.ASCENDING),
    ("ts", pymongo.ASCENDING),
    ("s", pymongo.ASCENDING),
    ("lb", pymongo.ASCENDING),
    ("rc", pymongo.ASCENDING),
    ("rm", pymongo.ASCENDING),
    ("tn", pymongo.ASCENDING),
    ("by", pymongo.ASCENDING),
    ("ng", pymongo.ASCENDING),
    ("na", pymongo.ASCENDING)
]

for key in keys:
    agent.create_index("test_results", key=key[0])


def parse_http_sample_string(result):
    if result is not None:
        new_dict = {}
        for item in result:
            try:
                new_dict[item[0]] = int(item[1])
            except Exception:
                new_dict[item[0]] = item[1]
        return new_dict


def insert_test_sample_to_db(agent=agent, data_to_insert=None):
    agent.insert_many("test_results", data_to_insert, ordered=False)


def jmx_parser(jmx_file_path=None):
    re_compile = re.compile("\s([^\s]*?)=\"(.*?)\"")
    sample_text = "<httpSample "
    samples_list = []

    with open(jmx_file_path, "r") as f:
        for line in f:
            if sample_text in line:
                result = re.findall(re_compile, line)
                samples_list.append(parse_http_sample_string(result))
                if len(samples_list) == MAX_SAMPLES_IN_INSERT_MANY:
                    insert_test_sample_to_db(data_to_insert=samples_list)
                    samples_list = []
        else:
            if len(samples_list) > 0:
                insert_test_sample_to_db(data_to_insert=samples_list)


if __name__ == "__main__":
    path = "/home/kali/DIPLOMA/diploma/test_runner/celery_batch/jmeter.log"
    jmx_parser(jmx_file_path=path)

print(datetime.datetime.now() - start)
