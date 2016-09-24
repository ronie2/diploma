from .tasks import *
from celery import chain


async def run_jmeter_test(job):
    job_uid = job["uid"]
    test_script_id = job["ts_id"]
    try:
        tasks = chain(create_test_folder.s(job_uid) |
              copy_file_to_folder.s(test_script_id) |
              run_jmeter_instance.s() |
              archive_folder_by_path.s() |
              delete_folder_by_path.s() |
              send_test_finish.s(job_uid))()

    except Exception as e:
        print(e)

    # return tasks.get()
