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
from celery_batch import celery_jmeter_tasks
from uuid import UUID
from .database_tools import DatabaseAgent
from bson.objectid import ObjectId

# class TestRunJob:
#     def __init__(self):


class TestRunHandler:
    jobs = {}

    def __init__(self):
        pass



    async def add_test_run(request):
        job = await TestRunHandler.create_job_object(request)
        logging.debug("[{uid}] Got new test run job...".format(uid=job["uid"]))
        try:
            await celery_jmeter_tasks.run_jmeter_test(job)
            job["status"] = 2
        except Exception as e:
            logging.info("[{uid}] Error while adding test run: {e}".format(
                uid=job["uid"], e=e))
        else:
            return web.Response(text=dumps({"uid": job["uid"]}),
                                content_type="application/json")

    async def test_job_finish(request):

        data = await request.post()

        #logging.info("URL: {}".format(data))
        test_run_id = request.match_info["tr_id"]
        test_results_path = data["path"]

        job = await TestRunHandler.find_job_by_uid(test_run_id)
        job["finished"] = datetime.datetime.now()
        job["test_results_path"] = test_results_path

        job_to_response = deepcopy(job)

        await TestRunHandler.add_test_run_data_to_db(request, job)
        await TestRunHandler.unregister_job_by_uid(test_run_id)

        return web.Response(text=dumps(job_to_response),
                            content_type="application/json")

    async def get_test_run_data_from_db(request):
        agent = DatabaseAgent()
        script_cursor = agent.find_all("test_runs")
        return script_cursor


    async def get_test_runs(request):
        finished_test_runs = await TestRunHandler.get_test_run_data_from_db(
            request
        )
        return web.Response(text=dumps(finished_test_runs),
                            content_type="application/json")

    async def test_run_by_id(request):
        if request.method == "GET":
            return await TestRunHandler.get_test_run_data(request)
        elif request.method == "DELETE":
            return await TestRunHandler.delete_test_run_data(request)
        else:
            return # web.Response(web.HTTPMethodNotAllowed(request.method))

                # return web.Response(
        #     text="Hallo, GET {}".format(request.match_info["tr_id"]))
    async def get_test_run_data(request):

        test_run_id = request.match_info["tr_id"]

        test_run_data = await TestRunHandler.get_test_run_data_by_id(
            test_run_id)
        json_test_run_data = dumps(test_run_data)
        return web.Response(text=json_test_run_data,
                            content_type="application/json")

    async def get_test_run_data_by_id(test_run_id):
        db_agent = DatabaseAgent()
        return db_agent.find_one("test_runs", {"_id": ObjectId(test_run_id)})


    async def delete_test_run_data(request):
        try:
            test_run_id = request.match_info["tr_id"]
            logging.info(test_run_id)
            res = await TestRunHandler.delete_test_run_by_id(test_run_id)
            logging.info("OK Delete Script")
            return web.Response(text="DONE")
        except Exception as e:
            logging.info("Error while deleting by id: {}".format(e))


    async def delete_test_run_by_id(test_run_id):
        agent = DatabaseAgent()
        return agent.delete_one("test_runs",
                                {"_id": ObjectId(test_run_id)})


    async def get_test_run_script(test_script_id):
        await TestScriptHandler.get_script_data_by_id(test_script_id)

    async def register_job(job):
        TestRunHandler.jobs.update({str(job["uid"]): job})

    async def unregister_job_by_uid(job_uid):
        del TestRunHandler.jobs[job_uid]

    async def find_job_by_uid(job_uid):
        return TestRunHandler.jobs[job_uid]

    async def create_job_object(request):
        data = await request.post()

        job = {
            "description": data["description"],
            "ts_id": request.match_info["ts_id"],
            "uid": uuid4(),
            "created": datetime.datetime.now(),
            "status": 1,
            "jobs_order": ["ERROR", "NEW", "TASK_QUEUED", "FINISHED"],
            "finished": None,
            "test_results_path": None
        }
        await TestRunHandler.register_job(job)
        return job

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
