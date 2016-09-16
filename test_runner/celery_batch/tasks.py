import requests
import os
import subprocess
from bson.json_util import loads

from celery_batch.celery import app


@app.task
def create_test_folder(job_uid):
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


@app.task
def copy_file_to_folder(folder_path, test_script_id):
    def get_script_file_name(request):
        return loads(request.text)["filename"]

    def get_script_content(request):
        return loads(request.text)["content"].decode()

    def get_full_path_to_script(file_name, folder_path):
        return folder_path + "/" + file_name

    def generate_url_to_script_by_id(test_script_id):
        def get_script_manager_url():
            return "http://127.0.1.1:5002"

        def get_script_manager_test_script_by_id_url():
            return "/v1/test-script/{ts_id}"

        endpoint = get_script_manager_url() + \
                   get_script_manager_test_script_by_id_url()

        return endpoint.format(ts_id=test_script_id)

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


@app.task
def run_jmeter_instance(jmx_file):
    def get_test_run_path(jmx_file_path):
        return os.path.abspath(jmx_file_path + "/../")

    def prepare_log_file_path(test_run_folder=None):
        normalised_path = os.path.abspath(test_run_folder)
        return normalised_path + "/jmeter.log"

    def prepare_jtl_file_path(test_run_folder=None):
        normalised_path = os.path.abspath(test_run_folder)
        return normalised_path + "/jmeter_report.jtl"

    test_run_folder = get_test_run_path(jmx_file)
    log_file = prepare_log_file_path(test_run_folder=test_run_folder)
    jtl_file = prepare_jtl_file_path(test_run_folder=test_run_folder)

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
        return test_run_folder


@app.task
def archive_folder_by_path(folder_path):
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
