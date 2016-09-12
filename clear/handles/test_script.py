import logging
import os.path
from datetime import datetime
from uuid import uuid4

from aiohttp import web
from config.conf import logger_msg
from handles.database_tools import DatabaseAgent
from copy import deepcopy
from bson.json_util import dumps
from bson.objectid import ObjectId
from handles.general_tools_mixin import get_server_root_folder


class TestScriptHandler:
    def __init__(self):
        pass

    async def add_test_script(request):
        job = await TestScriptHandler.add_test_script_factory(request=request)
        await TestScriptHandler.log_got_now_add_job(request, job=job)
        job["directory"] = await TestScriptHandler.create_new_directory(
            request, job=job)
        job["file_path"] = await TestScriptHandler.create_script_file(request,
                                                                      job=job)
        job["created"] = datetime.now()

        added_data = deepcopy(job)
        try:
            added_data[
                "db_id"] = await TestScriptHandler.add_script_data_to_db(
                request, data_to_add=job)
        except:
            logging.info("[{uid}] Test script was not added to DB...".format(
                uid=job["uid"]))
        return web.Response(text=dumps(added_data),
                            content_type="application/json")

    async def add_script_data_to_db(self, data_to_add):
        from copy import deepcopy
        data_to_db = deepcopy(data_to_add)
        # del data_to_db["file"]

        try:
            db_agent = DatabaseAgent()
            inserted_data = db_agent.insert_one("test_scripts", data_to_db)
        except Exception as e:
            logging.info("Error while entering database: {}".format(e))
        else:
            logging.info(
                "HHHHHHHHHHHHHHHHHHHHHAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHAAAAAAAAA")
            return inserted_data.inserted_id

    async def create_script_file(self, job=None):
        file_path = job["directory"] + "/" + job["filename"]

        try:
            # Save new job file to folder
            with open(file_path, "wb") as f:
                f.write(job["content"])
        except Exception as e:
            logging.info(e)
        else:
            logging.info(logger_msg["parser_save_file"].format(uid=job["uid"],
                                                               filename=job[
                                                                   "filename"],
                                                               foldername=job[
                                                                   "directory"]))
        return file_path

    async def create_new_directory(self, job=None):

        try:
            # Create directory for new job
            server_dir = get_server_root_folder()
            dir_path = server_dir + "/db/" + str(job["uid"])
            os.makedirs(dir_path)

        except Exception as e:
            logging.exception(
                "[{uid}] Failed to create directory for script: {e}".format(
                    uid=job["uid"], e=e))

        else:
            logging.info(
                logger_msg["parser_folder_created"].format(uid=job["uid"],
                                                           foldername=dir_path))

        return dir_path

    async def log_got_now_add_job(self, job=None):
        logging.info(logger_msg["parser_got_job"].format(uid=job["uid"],
                                                         filename=job[
                                                             "filename"],
                                                         title=job[
                                                             "description"]))

    async def add_test_script_factory(request=None):
        data = await request.post()
        return {
            "description": data["description"],
            # "file": data["script"].file,
            "filename": data["script"].filename,
            "content": data["script"].file.read(),
            "uid": uuid4(),
            "directory": None,
            "file_path": None,
            "created": None,
            "db_id": None
        }

    async def show_test_scripts(request):
        data_to_return = await TestScriptHandler.get_scripts_data_from_db(
            request)
        return web.Response(text=dumps(data_to_return),
                            content_type="application/json")

    async def get_scripts_data_from_db(request):
        agent = DatabaseAgent()
        script_cursor = agent.find_all("test_scripts")
        return script_cursor

    async def get_script_data_by_id(test_script_id):
        db_agent = DatabaseAgent()
        return db_agent.find_one("test_scripts", {"_id": ObjectId(test_script_id)})

    async def test_script_by_id(request):
        if request.method == "GET":
            return await TestScriptHandler.get_script_data(request)
        elif request.method == "DELETE":
            return await TestScriptHandler.delete_script_data(request)
        elif request.method == "PUT":
            return await TestScriptHandler.put_script_data(request)

    async def get_script_data(request):
        test_script_id = request.match_info["ts_id"]
        script_data = await TestScriptHandler.get_script_data_by_id(
            test_script_id)
        json_script_data = dumps(script_data)
        return web.Response(text=json_script_data,
                            content_type="application/json")

    async def delete_script_data(request):
        try:
            test_script_id = request.match_info["ts_id"]
            res = await TestScriptHandler.delete_script_by_id(test_script_id)
        except Exception as e:
            logging.info("Error while deleting by id: {}".format(e))
        else:
            logging.info("OK Delete Script")
            return res

    async def put_script_data(request):
        pass

    async def delete_script_by_id(_id):
        agent = DatabaseAgent()
        return agent.delete_one({"_id": ObjectId(_id)})
