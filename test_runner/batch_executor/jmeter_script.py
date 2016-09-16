import subprocess
import os
from bson.json_util import loads

from .rq_tools import RQWorker
import requests


def create_test_folder(job_uid=None):
    if job_uid is None:
        raise Exception("Can't create test folder: job_uid can't be 'None'")

    def get_server_root_folder():
        return os.path.abspath(__file__ + "/../")

    try:
        # Create directory for new job
        server_dir = get_server_root_folder()
        dir_path = server_dir + "/test_runs/" + str(job_uid)
        os.makedirs(dir_path)
    except Exception as e:
        raise Exception("Failed to create folder for test run: {0}".format(e))
    else:
        return dir_path


def get_script_manager_url():
    return "http://127.0.1.1:5002"


def get_script_manager_test_script_by_id_url():
    return "/v1/test-script/{ts_id}"


def generate_url_to_script_by_id(test_script_id):
    endpoint = get_script_manager_url() + \
               get_script_manager_test_script_by_id_url()
    return endpoint.format(ts_id=test_script_id)


# def copy_file_to_folder(test_script_id=None, folder_path=None):
#     if (test_script_id is None) or (folder_path is None):
#         raise Exception("File path and/or folder path can't be 'None'")
#     try:
#         url_to_script = generate_url_to_script_by_id()
#         request = requests.get(url_to_script)
#
#         test_script_content = get_script_content(request)
#         file_name = get_script_file_name(request)
#
#         full_script_path = get_full_path_to_script(file_name, folder_path)
#         with open(full_script_path, "w") as f:
#             f.write(test_script_content)
#             # new_file_path = shutil.copy(test_script_id, folder_path)
#     except Exception as e:
#         raise Exception("Can't copy file to folder: {0}".format(e))
#     else:
#         return full_script_path

def copy_file_to_folder(test_script_id=None, folder_path=None):
    if (test_script_id is None) or (folder_path is None):
        raise Exception("File path and/or folder path can't be 'None'")
    try:
        url_to_script = generate_url_to_script_by_id(test_script_id)

        request = requests.get(url_to_script)

        test_script_content = get_script_content(request)
        file_name = get_script_file_name(request)

        full_script_path = get_full_path_to_script(file_name, folder_path)
        with open(full_script_path, "x") as f:
            f.write(test_script_content)
    except Exception as e:
        raise Exception("Can't copy file to folder: {0}".format(e))
    else:
        return full_script_path


def get_full_path_to_script(file_name, folder_path):
    return folder_path + "/" + file_name


def get_script_file_name(request):
    return loads(request.text)["filename"]


def get_script_content(request):
    return loads(request.text)["content"].decode()


def run_jmeter_instance(jmx_file=None, log_file=None, jtl_file=None):
    try:
        task = subprocess.run(
            ["jmeter", "-n",
             "-t", jmx_file,
             "-l", log_file,
             "-j", jtl_file])
    except Exception as e:
        raise Exception("Can't run JMeter test: {0}".format(e))
    else:
        if task.returncode != 0:
            raise Exception(
                "Return code by 'JMeter' process is not '0' but: {0}".format(
                    task.returncode))
        return


def archive_folder_by_path(folder_path=None):
    normalised_path = os.path.abspath(folder_path)
    arch_file_path = normalised_path + ".tar.gz"
    root_folder_path = os.path.dirname(normalised_path)
    folder_name = os.path.basename(normalised_path)
    try:
        task = subprocess.run(["tar", "cvzf", arch_file_path, "-C",
                               root_folder_path, folder_name])
    except Exception as e:
        raise Exception("Can't archive folder: {0}".format(e))
    else:
        if task.returncode != 0:
            raise Exception("Something went wrong while archiving folder"
                            "return code by 'tar' is not '0'")


def prepare_log_file_path(test_run_folder=None):
    normalised_path = os.path.abspath(test_run_folder)
    return normalised_path + "/jmeter.log"


def prepare_jtl_file_path(test_run_folder=None):
    normalised_path = os.path.abspath(test_run_folder)
    return normalised_path + "/jmeter_report.jtl"


def script_run(job_uid, file_path):
    folder_path = create_test_folder(job_uid=job_uid)
    jmx_file_path = copy_file_to_folder(test_script_id=file_path,
                                        folder_path=folder_path)
    log_file_path = prepare_jtl_file_path(test_run_folder=folder_path)
    jtl_file_path = prepare_log_file_path(test_run_folder=folder_path)
    run_jmeter_instance(jmx_file=jmx_file_path,
                        jtl_file=jtl_file_path,
                        log_file=log_file_path)
    archive_folder_by_path(folder_path=folder_path)


def script_batch_run(job_uid, test_script_id):
    worker = RQWorker()
    folder_path = create_test_folder(job_uid=job_uid)

    copy_file_to_folder_job = worker.enqueue_calable("batch_executor.jmeter_script.copy_file_to_folder",
                                                     test_script_id=test_script_id,
                                                     folder_path=folder_path)
    while copy_file_to_folder_job.result is None:
        continue

    jmx_file_path = copy_file_to_folder_job.result

    log_file_path = prepare_log_file_path(test_run_folder=folder_path)
    jtl_file_path = prepare_jtl_file_path(test_run_folder=folder_path)

    test_run_job = worker.enqueue_calable(run_jmeter_instance,
                                          jmx_file=jmx_file_path,
                                          jtl_file=jtl_file_path,
                                          log_file=log_file_path,
                                          depends_on=copy_file_to_folder_job)

    archive_job = worker.enqueue_calable(archive_folder_by_path,
                                         folder_path=folder_path,
                                         depends_on=test_run_job)
