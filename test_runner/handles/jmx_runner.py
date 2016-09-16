from asyncio import Event

import batch_executor.rq_tools
from batch_executor.rq_tools import *


class JMXRunner:
    def __init__(self,
                 script_data=None,
                 request=None,
                 job=None):
        self.job = job
        self.script_data = deepcopy(script_data)
        self.jmx_file_path = self.script_data["file_path"]
        self.test_run_folder = None

    async def run_jmx_test(self):
        try:
            self.test_run_folder = self.create_test_folder()
            self.copy_test_script_to_run_folder()
            self.run_test()
            self.archive_jmx_test_results()
        except Exception as e:
            raise Exception(
                "[{uid}]Error while running JMeter test: {e}".format(
                    uid=self.test_run_uid, e=e))

    def run_test(self):
        jmx_file = self.jmx_file_path
        jtl_file = self.prepare_jtl_file_path()
        log_file = self.prepare_log_file_path()

        worker = RQWorker()
        worker.enqueue_calable(batch_executor.rq_tools.run_jmeter_instance,
                               jmx_file, jtl_file, log_file)
        return

    def archive_jmx_test_results(self):
        worker = RQWorker()
        worker.enqueue_calable(batch_executor.rq_tools.archive_folder_by_path,
                               self.test_run_folder)
        return
