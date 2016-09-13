import os.path
from handles.rq_tools import *
import handles.rq_tools


class JMXRunner:
    def __init__(self,
                 script_data=None,
                 test_run_folder=None,
                 test_run_uid=None):

        self.script_data = deepcopy(script_data)
        self.test_run_folder_path = test_run_folder
        self.jmx_file_path = self.script_data["file_path"]
        self.test_run_uid = test_run_uid

    async def run_jmx_test(self):
        try:
            JMXRunner.run_test(self)
        except Exception as e:
            raise Exception(
                "[{uid}]Error while running JMeter test: {e}".format(
                    uid=self.test_run_uid, e=e))
        else:
            try:
                JMXRunner.archive_jmx_test_results(self)
            except Exception as e:
                raise Exception(
                    "Error while archiving JMeter test run "
                    "results folder: {e}".format(e=e))

    def run_test(self):
        jmx_file = self.jmx_file_path
        jtl_file = self.prepare_jtl_file_path()
        log_file = self.prepare_log_file_path()

        worker = RQWorker()
        worker.enqueue_calable(handles.rq_tools.run_jmeter_instance,
                               jmx_file, jtl_file, log_file)
        return

    def prepare_log_file_path(self):
        normalised_path = os.path.abspath(self.test_run_folder_path)
        return normalised_path + "/jmeter_report.jtl"

    def prepare_jtl_file_path(self):
        normalised_path = os.path.abspath(self.test_run_folder_path)
        return normalised_path + "/jmeter.log"

    def archive_jmx_test_results(self):
        worker = RQWorker()
        worker.enqueue_calable(handles.rq_tools.archive_folder_by_path,
                               self.test_run_folder_path)
        return
