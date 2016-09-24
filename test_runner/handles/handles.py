from .conf import cfg
from .plugins import get_log
from .test_run import TestRunHandler
from aiohttp import web

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
