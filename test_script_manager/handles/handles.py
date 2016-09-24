import os.path

import aiohttp_jinja2

from .conf import cfg, sub_message
from .plugins import get_log

# import all handles classes
from .test_script import *


async def parse_validator():
    """parse_validator validates files to be parsed

    NOT IMPLEMENTED JET

    Returns:
        True
    """
    # Not implemented yet
    return True


# 'Parser page'
@aiohttp_jinja2.template("parser.jinja2")
async def book_parser_handle(request):
    """book_parser_handle function processes new books parsing

    Args:
        request (aiohttp request): http request

    Returns:
        If 'POST' method:
            String with result of parsing

        If 'GET' method:
            Config dict for jinja2 template
    """
    if request.method == "POST":
        data = await request.post()
        job = {
            "title": data["title"],
            "file": data["book"].file,
            "filename": data["book"].filename,
            "content": data["book"].file.read(),
            "uid": uuid4(),
        }

        logging.info(logger_msg["parser_got_job"].format(uid=job["uid"],
                                                         filename=job[
                                                             "filename"],
                                                         title=job["title"]))
        # content = job["file"].read()

        if await parse_validator():
            logging.info(
                logger_msg["parser_validator_pass"].format(uid=job["uid"]))

            # Create directory for new job
            server_dir = os.path.abspath(__file__ + "/../../")
            db_dir = server_dir + "/db/" + str(job["uid"])
            os.makedirs(db_dir)
            logging.info(
                logger_msg["parser_folder_created"].format(uid=job["uid"],
                                                           foldername=db_dir))
            file_name = db_dir + "/" + job["filename"]

            # Save new job file to folder
            with open(file_name, "wb") as f:
                f.write(job["content"])

            logging.info(logger_msg["parser_save_file"].format(uid=job["uid"],
                                                               filename=job[
                                                                   "filename"],
                                                               foldername=db_dir))

            logging.info(
                logger_msg["parser_mongo_start"].format(uid=job["uid"]))
            mongo_job = mongo_parser(parse_book(file_name, title=job["title"]))
            logging.info(
                logger_msg["parser_mongo_finish"].format(uid=job["uid"],
                                                         root_id=mongo_job))

            result_string = "File: '{filename}' parsed successfully  to 'roots' collection mongodb with id: {root_id}"
            return web.Response(
                body=result_string.format(filename=job["filename"],
                                          root_id=mongo_job).encode())

    # If request metod GET => render jinja form
    if request.method == "GET":
        return {
            "title": cfg["server"]["book_parser"]["config"]["jinja2"]["title"],
            "legend": cfg["server"]["book_parser"]["config"]["jinja2"][
                "legend"]
        }


# 'Search page' jinja2 template preparation
@aiohttp_jinja2.template('search.jinja2')
async def search_handle(request):
    """search_handle function processes search form

    Args:
        request (aiohttp request): http request

    Returns:
        Config dict for jinja2 template
    """
    if request.method == "GET":
        return {
            "title": cfg["server"]["search"]["config"]["jinja2"]["title"],
            "legend": cfg["server"]["search"]["config"]["jinja2"]["legend"]
        }


# 'Results page' jinja2 template preparation
@aiohttp_jinja2.template('result.jinja2')
async def result_handle(request):
    """result_handle function processes search

    Args:
        request (aiohttp request): http request

    Returns:
        Config dict for jinja2 template with processing results
    """
    from validate_email import validate_email
    if request.method == "GET":

        # Awaiting request
        job = {
            "request": request.GET,
            "uid": uuid4(),
        }

        # If no search term info was given => show error notification
        if len(job["request"]) == 0:
            logging.info(logger_msg["invalid_search"])
            # Return data for 'Results page' to jinja2 template engine
            return {
                "message": "No info to process!<br>Please provide valid info to process!",
                "status_code": 0,
                "title": cfg["server"]["result"]["config"]["jinja2"]["title"]
            }

        # If given email is valid
        elif validate_email(job["request"]["email"], check_mx=True):
            logging.info(logger_msg["valid_request"].format(uid=job["uid"],
                                                            term=
                                                            job["request"][
                                                                "searchinput"],
                                                            e_mail=
                                                            job["request"][
                                                                "email"]))

            started_at = datetime.now()
            logging.info(logger_msg["search_started"].format(uid=job["uid"],
                                                             time=datetime.now(),
                                                             time_limit=
                                                             job["request"][
                                                                 "time"]))

            # Get list of search results 'sub-emails'
            try:
                result_list = []
                for item in find_phrase(job["request"]["searchinput"]):
                    if (item["time"] - started_at).total_seconds() > float(
                            job["request"]["time"]):
                        break
                    else:
                        result_list.append(item["message"])
                result = "\n".join(result_list)

            # If can't parse max search time as float => search without time limit
            except Exception as e:
                logging.info(
                    logger_msg["invalid_max_time"].format(uid=job["uid"], e=e))
                logging.info(
                    logger_msg["no_time_limit"].format(uid=job["uid"]))
                result_list = [item["message"] for item in
                               find_phrase(job["request"]["searchinput"])]
                result = "\n".join(result_list)

            # Logging job execution time
            finished_at = datetime.now()
            logging.info(logger_msg["search_finished"].format(uid=job["uid"],
                                                              time=finished_at,
                                                              delta=finished_at - started_at))

            # If list of 'sub-emails' is empty => send nothing was found message
            if len(result) == 0:
                result = "Phrase was not found!"

            # If validators pass => enqueue e-mail for sending by RQ
            enqueue_email(result, job["request"]["email"],
                          job["request"]["searchinput"])

            # Return data for 'Results page' to jinja2 template engine
            return {
                "message": "Search started for this request: " + str(
                    job["request"]["searchinput"]) + "<br>" +
                           "Results will be sent to this e-mail: " + str(
                    job["request"]["email"]),
                "status_code": 1,
                "title": cfg["server"]["result"]["config"]["jinja2"]["title"]
            }

        # If given email is NOT valid
        else:
            logging.info(logger_msg["invalid_email"].format(uid=job["uid"],
                                                            e_mail=
                                                            job["request"][
                                                                "email"]))

            # Return data for 'Results page' to jinja2 template engine
            return {
                "message": "Wrong e-mail!<br>Please provide valid e-mail!",
                "status_code": 0,
                "title": cfg["server"]["result"]["config"]["jinja2"]["title"]
            }


class TestResultHandler:
    def __init__(self):
        pass

    async def add_test_result(request):
        return web.Response(text="Hallo")

    async def get_test_results(request):
        return web.Response(text="Hallo")

    async def test_result_by_id(request):
        return web.Response(
            text="Hallo, {}".format(request.match_info["tres_id"]))


async def log_get(request):
    """log_app function processes log web interface

    Args:
        request (aiohttp request): http request

    Returns:
        Text web response with log string
    """
    if request.method == "GET":
        return web.Response(text=await get_log(
            log_file_name=cfg["server"]["app_log"]["config"]["log_file"]))


def find_phrase(search_term):
    """find_phrase generator yield search result strings

    Args:
        search_term (str): search term customer searches

    Yields:
        'serch_result' strings
    """
    for result in mongo_search(search_term):
        serch_result = {
            "message": sub_message.format(
                book_name=result["result"]["book"],
                part_name=result["result"]["part"],
                chapter_name=result["result"]["chapter"],
                paragraph_num=result["result"]["paragraph"],
                paragraph_text=result["result"]["text"]),
            "time": datetime.now()
        }
        yield serch_result


def enqueue_email(results, receiver, request):
    """enqueue_email functions enqueues job to send e-mail to RQ WORKER

    Args:
        results (str): formatted search results as one string
        receiver (str): e-mail of customer
        request (str): search term customer searches

    Returns:
        None
    """
    from rq import Queue
    from redis import Redis

    redis_conn = Redis()
    q = Queue(connection=redis_conn)
    q.enqueue(send_email, results, receiver, request)
