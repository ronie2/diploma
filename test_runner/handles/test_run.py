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
        job = await TestRunHandler.add_test_run_factory(request)
        logging.debug("[{uid}] Got new test run job...".format(uid=job["uid"]))
        try:
            await TestRunHandler.get_test_run_script()
            job["finished"] = datetime.datetime.now()
            await TestRunHandler.execute_test_run(request=request, job=job)
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

    async def get_test_run_script(test_script_id):
        await TestScriptHandler.get_script_data_by_id(test_script_id)

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

    async def execute_test_run(request=None, job=None):
        script_type = "JMeter"
        if script_type == "JMeter":
            JMXRunner(
                script_data=await TestScriptHandler.get_script_data_by_id(
                    job["ts_id"]),
                request=request,
                job=job)

    async def run_test(script_data=None,
                       test_run_folder=None,
                       test_run_uid=None):

        test_runner = JMXRunner(script_data=script_data,
                                test_run_folder=test_run_folder,
                                test_run_uid=test_run_uid)

        await test_runner.run_jmx_test()
