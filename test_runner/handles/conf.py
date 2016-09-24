mongo_cfg = {
    "db_name": "diploma",
    "db_host": None,
    "db_port": None
}


test_run_manager_url = "http://127.0.1.1:5003"
test_run_manager_job_finish_by_id_url = "/v1/test-job-finish/{tr_id}"

cfg = {
    "service": {
        "home": {
            "host": None,  # Host will be assigned automatically
            "port": 5003,
        },
        "email": {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 465,
            "login": "book.search.app.test@gmail.com",
            "password": "book.search.app.test111",
        }
    },
    "server": {
        "app_log": {
            "config": {
                "method": "*",
                "endpoint": "/log",
                "handle": "log_get",
                "timeout": 0,
                "log_file": "app.log",
            },
        },
        "add_test_run": {
            "config": {
                "desc": "Start test run for specified ts_id",
                "method": "POST",
                "endpoint": "/v1/add-test-run/{ts_id}",
                "handle": "TestRunHandler.add_test_run",
                "timeout": 0,
                "log_file": "app.log"
            }
        },
        "finish_test_run":{
            "config": {
                "desc": "Signal for test finish by job uid",
                "method": "POST",
                "endpoint": "/v1/test-job-finish/{tr_id}",
                "handle": "TestRunHandler.test_job_finish",
                "timeout": 0,
                "log_file": "app.log"
            }
        },
        "get_test_runs": {
            "config": {
                "desc": "Returns list of all test runs in database",
                "method": "GET",
                "endpoint": "/v1/test-runs",
                "handle": "TestRunHandler.get_test_runs",
                "timeout": 0,
                "log_file": "app.log"
            }
        },
        "test_run_by_id": {
            "config": {
                "desc": "Returns or deletes test runs by ID",
                "method": "*",
                "endpoint": "/v1/test-run/{tr_id}",
                "handle": "TestRunHandler.test_run_by_id",
                "timeout": 0,
                "log_file": "app.log"
            }
        },

    }
}

logger_msg = {
    "app_start": "Book Search server START...",
    "app_stop": "Book Search server STOP...",
    "invalid_request": "[{uid}] Got invalid search request",
    "invalid_email": "[{uid}] Got invalid search request - e-mail ({e_mail}) is not valid",
    "invalid_max_time": "[{uid}] Error in parsing time: {e}",
    "no_time_limit": "[{uid}] Searching without time limit",
    "valid_request": "[{uid}] Got valid search request to find: '{term}' and send results to e-mail: {e_mail}",
    "search_started": "[{uid}] Search results preparation started at: {time} with limit of: '{time_limit}' seconds",
    "search_finished": "[{uid}] Full search results preparation finished at: {time} and took: {delta}",
    "parser_got_job": "[{uid}] Received job to process file: '{filename}' and title: '{title}'",
    "parser_validator_pass": "[{uid}] Job passed validator",
    "parser_save_file": "[{uid}] File '{filename}' saved to folder '{foldername}'",
    "parser_folder_created": "[{uid}] Folder created: {foldername}",
    "parser_mongo_start": "[{uid}] Started parsing *.txt file and submitting to mongodb",
    "parser_mongo_finish": "[{uid}] Finished parsing. Record created in 'roots' collections: {root_id}",
}

message = """
Hi dear customer!
You have submitted search request for term:
{request}

Here are your results:
{result}
"""
sub_message = """
        In book: {book_name}
        In part: {part_name}
        In chapter: {chapter_name}
        In paragraph #: {paragraph_num}
        Text:
        {paragraph_text}
        """
