import os.path
import subprocess
import shutil


def get_server_root_folder():
    return os.path.abspath(__file__ + "/../../")


def archive_folder_by_path(path):
    normalised_path = os.path.abspath(path)
    arch_file_path = normalised_path + ".tar.gz"
    root_folder_path = os.path.dirname(normalised_path)
    folder_name = os.path.basename(normalised_path)
    try:
        task = subprocess.run(["tar", "cvzf", arch_file_path, "-C",
                               root_folder_path, folder_name])
    except Exception as e:
        raise Exception(e)
    else:
        if task.returncode != 0:
            raise Exception("Something went wrong while archiving folder"
                            "return code by 'tar' is not '0'")


async def copy_file_to_folder(file_path=None, folder_path=None):
    shutil.copy(file_path, folder_path)