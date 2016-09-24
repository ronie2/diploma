async def get_log(log_file_name="log.log"):
    """get_log function returns data in log file as string

    Args:
        log_file_name (str): path to log file

    Returns:
        Log file data as single string
    """
    import os
    # Check if file exists and create file if it doesn't
    if not os.path.isfile(log_file_name):
        with open(log_file_name, "w") as f:
            pass

    log_records = ""
    with open(log_file_name, "r") as log:
        return log_records.join(log)

async def write_log(request, log_file_name="log.log"):
    import os
    # Check if file exists and create file if it doesn't
    if not os.path.isfile(log_file_name):
        with open(log_file_name, "w") as f:
            pass

    import datetime
    mode = "a+"
    line_width = 50
    with open(log_file_name, mode, encoding="utf-8") as log:
        log.write("\n" + "*" * line_width + "\n")
        log.write(str(datetime.datetime.now()))
        log.write("\n" + "*" * line_width + "\n")
        log.write("START LINE:\n")
        log.write("***\n")
        log.write(request.method + " " +
                  request.host + " " +
                  request.scheme.upper() + "/" +
                  str(request.version[0]) +
                  "." +
                  str(request.version[1])
                  )
        log.write("\n\nHEADER:\n")
        log.write("***\n")
        for field in request.headers.items():
            log.write(str(field[0] + ": " + field[1]) + "\n")
        log.write("\nBODY:\n")
        log.write("***\n")
        body = await request.read()
        log.write(body.decode())
        log.write("\n")

async def sleep(endpoint, method_name):
    import asyncio
    from handles.conf import cfg
    try:
        await asyncio.sleep( \
            cfg["server"][endpoint][method_name]["timeout"])
    except Exception as e:
        print("Error in Timeout Plugin: " + e)

    return

async def get_ssh_log():
    import os
    from paramiko import SSHClient
    from scp import SCPClient

    ssh = SSHClient()
    ssh.load_system_host_keys()
    local_path = os.getcwd()
    main_log = "path/to/log"
    ssh.connect("URI", 22, "login_here", "password_here")
    scp = SCPClient(ssh.get_transport())
    scp.get(main_log, local_path = local_path)
    log_records = ""

    with open("logMain.log", "r+") as log:
        return log_records.join(log)

    return "Some error happened!!!"
