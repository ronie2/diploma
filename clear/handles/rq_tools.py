from rq import Queue
from redis import Redis
from handles.test_run import *


def archive_folder_by_path(path):
    normalised_path = os.path.abspath(path)
    arch_file_path = normalised_path + ".tar.gz"
    root_folder_path = os.path.dirname(normalised_path)
    folder_name = os.path.basename(normalised_path)
    try:
        task = subprocess.run(["tar", "cvzf", arch_file_path, "-C",
                               root_folder_path, folder_name])
    except Exception as e:
        raise Exception(e)
    else:
        if task.returncode != 0:
            raise Exception("Something went wrong while archiving folder"
                            "return code by 'tar' is not '0'")


def run_jmeter_instance(jmx_file, jtl_file, log_file):
    try:
        task = subprocess.run(
            ["jmeter", "-n",
             "-t", jmx_file,
             "-l", log_file,
             "-j", jtl_file])
        if task.returncode != 0:
            raise Exception(
                "Return code by 'jmeter' process is not '0' but: {0}".format(
                    task.returncode))
    except Exception as e:
        raise Exception("Something went wrong while running JMeter test: ", e)


class RQWorker:
    def __init__(self):
        self.redis_conn = Redis()
        self.queue = Queue(connection=self.redis_conn)

    def enqueue_calable(self, calable, *args, **kwargs):
        self.queue.enqueue(calable, *args, **kwargs)
