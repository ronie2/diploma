import batch_executor 
from uuid import uuid4
import sys


# file_path = "/home/kali/DIPLOMA/diploma/clear/db/HTTP My File.jmx"
batch_executor.jmeter_script.script_batch_run(str(uuid4()), "57dab31eb179a976f6372579")
#
# jmx_file = "/home/kali/DIPLOMA/diploma/clear/batch_executor/test_runs/d98f4ed8-92da-429f-a18d-efc5021994e8/HTTP.jmx"
# jmx_file = "/home/kali/DIPLOMA/diploma/clear/batch_executor/test_runs/d98f4ed8-92da-429f-a18d-efc5021994e8/HTTP.jtl"
# log_file = "/home/kali/DIPLOMA/diploma/clear/batch_executor/test_runs/d98f4ed8-92da-429f-a18d-efc5021994e8/HTTP.log"
#
# jmeter_script.run_jmeter_instance(jmx_file=jmx_file,
#                                   jtl_file=jmx_file,
#                                   log_file=log_file)
# # worker = rq_tools.RQWorker()
# worker.enqueue_calable(jmeter_script.script_run, "fkjdasklfj", file_path)
