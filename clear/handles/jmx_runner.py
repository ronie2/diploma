import logging
from handles.general_tools_mixin import archive_folder_by_path
import subprocess
import os.path
from copy import deepcopy


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
            await JMXRunner.run_jmeter_instance(self)
        except Exception as e:
            raise Exception(
                "[{uid}]Error while running JMeter test: {e}".format(
                    uid=self.test_run_uid, e=e))
        else:
            try:
                await JMXRunner.archive_jmx_test_results(self)
            except Exception as e:
                raise Exception(
                    "Error while archiving JMeter test run "
                    "results folder: {e}".format(e=e))

    async def run_jmeter_instance(self):
        task = subprocess.Popen(["jmeter", "-n",
                                 "-t", self.jmx_file_path,
                                 "-l", await self.prepare_jtl_file_path(),
                                 "-j", await self.prepare_log_file_path()])
        # if task.returncode != 0:
        #     raise Exception("Something went wrong while running JMeter"
        #                     "return code by 'jmeter' process is not '0'")

    async def prepare_log_file_path(self):
        normalised_path = os.path.abspath(self.test_run_folder_path)
        return normalised_path + "/jmeter_report.jtl"

    async def prepare_jtl_file_path(self):
        normalised_path = os.path.abspath(self.test_run_folder_path)
        return normalised_path + "/jmeter.log"

    async def archive_jmx_test_results(self):
        archive_folder_by_path(self.test_run_folder_path)
