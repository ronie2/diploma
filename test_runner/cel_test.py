from celery_batch.tasks import *
from celery import chain
from uuid import uuid4

result = chain(create_test_folder.s(str(uuid4())) |
               copy_file_to_folder.s("57dab31eb179a976f6372579") |
               run_jmeter_instance.s() |
               archive_folder_by_path.s())()
print("result")
