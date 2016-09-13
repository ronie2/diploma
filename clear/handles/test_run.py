from aiohttp import web
from uuid import uuid4
import datetime
from copy import deepcopy
import logging
from handles.database_tools import *
from handles.test_script import TestScriptHandler
from handles.general_tools_mixin import *
from handles.jmx_runner import JMXRunner
import os.path
from bson.json_util import dumps

class TestRunHandler:
    def __init__(self):
        pass

    async def add_test_run(request):
        logging.debug("hahahdfkasdhkfjha")
        job = await TestRunHandler.add_test_run_factory(request)
        logging.debug("[{uid}] Got new test run job...".format(uid=job["uid"]))
        try:
            job["test_results_path"] = await TestRunHandler.exectute_test_run(
                request=request, job=job)
            job["finished"] = datetime.datetime.now()
            await TestRunHandler.add_test_run_data_to_db(request=request,
                                                         job=job)
        except Exception as e:
            logging.info("[{uid}] Error while adding test run: {e}".format(
                uid=job["uid"], e=e))
        else:
            return web.Response(text=dumps(job),
                                content_type="application/json")

            # return web.Response(
            #     text="Hallo, POST {}".format(request.match_info["ts_id"]))

    async def get_test_runs(request):
        return web.Response(text="Hallo")

    async def test_run_by_id(request):
        return web.Response(
            text="Hallo, GET {}".format(request.match_info["tr_id"]))

    async def add_test_run_factory(request):
        data = await request.post()

        return {
            "description": data["description"],
            "ts_id": request.match_info["ts_id"],
            "uid": uuid4(),
            "created": datetime.datetime.now(),
            "finished": None,
            "test_results_path": None
        }

    async def add_test_run_data_to_db(request=None, job=None):
        data_to_db = deepcopy(job)
        try:
            db_agent = DatabaseAgent()
            inserted_data = db_agent.insert_one("test_runs", data_to_db)
        except Exception as e:
            logging.debug(
                "[{uid}] Error while adding test run to DB: {e}".format(
                    uid=job["uid"], e=e))
        else:
            logging.info(
                "[{uid}] Test run successfully added to DB".format(
                    uid=job["uid"]))
            return inserted_data.inserted_id

    async def exectute_test_run(request=None, job=None):
        test_script_id = job["ts_id"]
        test_run_uid = job["uid"]
        logging.info("[{uid}] Starting test run...".format(uid=test_run_uid))
        return await TestRunHandler.run_test_script_by_id(
            test_script_id=test_script_id,
            test_run_uid=test_run_uid)

    async def run_test_script_by_id(test_script_id=None,
                                    test_run_uid=None):
        script_data = await TestScriptHandler.get_script_data_by_id(
            test_script_id)
        test_run_folder = await TestRunHandler.prepare_test_run_folder(
            script_data=script_data,
            test_run_uid=test_run_uid)

        await TestRunHandler.run_test(script_data=script_data,
                                      test_run_folder=test_run_folder,
                                      test_run_uid=test_run_uid)
        return test_run_folder

    async def copy_test_script_to_run_folder(test_script_path=None,
                                             test_run_folder=None):

        await copy_file_to_folder(file_path=test_script_path,
                                  folder_path=test_run_folder)

    async def prepare_test_run_folder(script_data=None, test_run_uid=None):
        test_script_path = script_data["file_path"]

        test_run_folder_path = await TestRunHandler.create_test_run_folder(
            script_data=script_data,
            test_run_uid=test_run_uid)

        await TestRunHandler.copy_test_script_to_run_folder(
            test_script_path=test_script_path,
            test_run_folder=test_run_folder_path)

        return test_run_folder_path

    async def create_test_run_folder(script_data=None, test_run_uid=None):
        try:
            # Create directory for new job
            server_dir = get_server_root_folder()
            dir_path = server_dir + "/test_runs/" + str(test_run_uid)
            os.makedirs(dir_path)
        except Exception as e:
            logging.info(
                "[{uid}] Failed to create folder for test run".format(
                    uid=test_run_uid))
        else:
            return dir_path

    async def run_test(script_data=None,
                       test_run_folder=None,
                       test_run_uid=None):

        test_runner = JMXRunner(script_data=script_data,
                                test_run_folder=test_run_folder,
                                test_run_uid=test_run_uid)

        await test_runner.run_jmx_test()
