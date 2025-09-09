# Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=import-error,no-name-in-module,too-many-positional-arguments,too-many-arguments
"""This module handles downloading RPM files for local repository"""

import subprocess
import os
from ansible.module_utils.local_repo.config import (
    DNF_COMMANDS
)
from multiprocessing import Lock
from ansible.module_utils.local_repo.parse_and_download import write_status_to_file

file_lock = Lock()

def process_rpm(package, repo_store_path, status_file_path, cluster_os_type,
               cluster_os_version, repo_config_value, arc, logger):
    logger.info("#" * 30 + f" {process_rpm.__name__} start " + "#" * 30)
 
    try:
        if repo_config_value == "always":
            rpm_list = list(set(package["rpm_list"]))
            logger.info(f"{package['package']} - List of rpms is {rpm_list}")
 
            rpm_directory = os.path.join(
                repo_store_path, 'offline_repo',
                'cluster', arc.lower(), cluster_os_type, cluster_os_version, 'rpm'
            )
            logger.info(f"rpm_dir {rpm_directory}")
            os.makedirs(rpm_directory, exist_ok=True)
 
            arch_key = "x86_64" if arc.lower() in ("x86_64") else "aarch64"
 
            # First try to download all at once
            dnf_download_command = DNF_COMMANDS[arch_key] + [f'--destdir={rpm_directory}'] + rpm_list
            result = subprocess.run(dnf_download_command, check=False, capture_output=True, text=True)
 
            logger.info(f"Return code {result.returncode}")
            logger.debug(f"STDOUT:\n{result.stdout}")
            logger.debug(f"STDERR:\n{result.stderr}")
 
            stdout_lines = result.stdout.splitlines()
            stderr_lines = result.stderr.splitlines()
 
            downloaded = []
            failed = []
 
            # Detect successes/failures from combined run
            for pkg in rpm_list:
                if any(pkg in line and ".rpm" in line for line in stdout_lines + stderr_lines):
                    downloaded.append(pkg)
                    write_status_to_file(status_file_path, pkg, "rpm", "Success", logger, file_lock)
                else:
                    failed.append(pkg)
 
            # Retry failed ones individually
            if failed:
                logger.warning(f"Retrying failed packages individually: {failed}")
                for pkg in failed[:]:
                    cmd = DNF_COMMANDS[arch_key] + [f'--destdir={rpm_directory}', pkg]
                    retry_res = subprocess.run(cmd, check=False, capture_output=True, text=True)
 
                    if retry_res.returncode == 0 and ".rpm" in retry_res.stdout + retry_res.stderr:
                        downloaded.append(pkg)
                        failed.remove(pkg)
                        write_status_to_file(status_file_path, pkg, "rpm", "Success", logger, file_lock)
                        logger.info(f"Package '{pkg}' downloaded successfully on retry.")
                    else:
                        write_status_to_file(status_file_path, pkg, "rpm", "Failed", logger, file_lock)
                        logger.error(f"Package '{pkg}' still failed after retry.")
 
            # Determine final status
            if not failed:
                status = "Success"
            elif downloaded:
                status = "Partial"
            else:
                status = "Failed"
 
        else:
            status = "Success"
            logger.info("RPM won't be downloaded when repo_config is partial or never")
            for pkg in package["rpm_list"]:
                write_status_to_file(status_file_path, pkg, "rpm", "Success", logger, file_lock)
 
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        status = "Failed"
        for pkg in package.get("rpm_list", []):
            write_status_to_file(status_file_path, pkg, "rpm", "Failed", logger, file_lock)
 
    finally:
        logger.info(f"Overall status for {package['package']}: {status}")
        logger.info("#" * 30 + f" {process_rpm.__name__} end " + "#" * 30)
        return status
