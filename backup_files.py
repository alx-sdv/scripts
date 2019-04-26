import logging
from datetime import datetime
import os
import shutil
import filecmp

"""
This script performs incremental local file backup from given list of sources to specified destination. 
See "logs" directory to get information about backup process.

Attributes:
    source_path_list (list): files and folders to be copied
    target_path (str): destination device or folder
    working_folder (str): first time this folder will be created to store all backups, each backup has it's subfolder
    target_free_space_threshold_gb (float): check target available space before start

Do not modify working folder content manually.

TODO:
    * Replace global variables by func args
    * Calculate source files size before copying
    * Add external config
    * Log skipped files
    * Do not create empty folders
"""

################################################################################

# source settings
source_path_list = [
    '/mnt/123/files/',
    '/home/user/Downloads/file.doc'
]
ignore_patterns_list = ['*.bak', '*.pyc', '*.tmp', '.git']

# target settings
target_path = '/media/user/disk/'
working_folder = 'bkp_home'
target_free_space_threshold_gb = 0.001

################################################################################


def perform_checks():
    logger.info('Performing checks...')
    logger.info('Checking source files...')
    for source in source_path_list:
        if not os.path.exists(source):
            logger.error(f'Not found {source}')
            quit()
    logger.info(f'Ok ({len(source_path_list)} items in source list)')

    logger.info('Checking disk usage...')
    if not os.path.exists(target_path):
        logger.error(f'Not found {target_path}')
        quit()
    disk_usage = shutil.disk_usage(target_path)
    if disk_usage.free / 1024 / 1024 / 1024 > target_free_space_threshold_gb:
        logger.info(f'Ok (total: {disk_usage.total / 1024 / 1024 / 1024 :1.2f} Gb; '
                    f'used {disk_usage.used / 1024 / 1024 / 1024 :1.2f} Gb; '
                    f'free {disk_usage.free / 1024 / 1024 / 1024 :1.2f} Gb)')
    else:
        logger.error(f'Not enough free space ({disk_usage.free / 1024 / 1024 / 1024 :1.2f} Gb)')
        quit()

    try:
        os.mkdir(target_folder)
    except FileExistsError:
        logger.error(f'Target folder "{target_folder.split(os.sep)[-1]}" already exists, please cleanup')
        quit()
    logger.info('Everything is seems to be ok')
    if prev_backup_list:
        logger.info(f'Previous backup found {prev_backup_list}')
    else:
        logger.info(f'It seems to be initial (full) backup')
    logger.info(f'Created {target_folder}')


def do_copy(src, dst):
    prev_version_path = ''
    for backup_name in prev_backup_list:
        path_to_find = working_folder + os.sep + backup_name + os.sep + src.replace(':', os.sep).lstrip(os.sep)
        if os.path.exists(path_to_find):
            prev_version_path = path_to_find
            break
    if not (prev_version_path and filecmp.cmp(src, prev_version_path)):
        logger.info(f'Copy {src}')
        return shutil.copy2(src, dst)


def perform_backup():
    logger.info('Backup started...')
    for source in source_path_list:
        prepared_dest_path = target_folder + os.sep + source.replace(':', os.sep).lstrip(os.sep)
        if os.path.isdir(source):
            shutil.copytree(source,
                            prepared_dest_path,
                            ignore=shutil.ignore_patterns(*ignore_patterns_list),
                            copy_function=do_copy)
        else:
            os.makedirs(os.path.dirname(prepared_dest_path), exist_ok=True)
            do_copy(source, prepared_dest_path)
    total_size = 0
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(target_folder):
        for file in filenames:
            total_size += os.path.getsize(os.path.join(dirpath, file))
            total_files += 1
    logger.info(f'{total_files} files copied ({total_size / 1024 / 1024 / 1024 :1.2f} Gb)')
    logger.info('Backup finished')


if __name__ == '__main__':
    working_folder = os.path.join(target_path, working_folder)
    os.makedirs(working_folder, exist_ok=True)
    log_folder = os.path.join(working_folder, 'logs')
    target_folder = os.path.join(working_folder, datetime.now().strftime('%Y%m%d'))
    prev_backup_list = sorted([d for d in os.listdir(working_folder) if d.split(os.sep)[-1].isdigit()], reverse=True)
    os.makedirs(log_folder, exist_ok=True)

    logging.basicConfig(level=logging.INFO)
    log_handler = logging.FileHandler(os.path.join(log_folder, f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"),
                                      encoding='utf-8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%H:%M:%S'))
    log_handler.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(log_handler)

    perform_checks()
    try:
        perform_backup()
    except shutil.Error as e:
        logger.error(str(e))
        quit()
