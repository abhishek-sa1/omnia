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

# pylint: disable=import-error,no-name-in-module,line-too-long

import os
import shutil
from ansible.module_utils.basic import AnsibleModule


def find_cuda_rpm_folder(cuda_tmp_path):
    """Search for the 'cuda' folder in the extracted structure."""
    for root, dirs, _ in os.walk(os.path.join(cuda_tmp_path, "var")):
        if "cuda" in dirs:
            return os.path.join(root, "cuda")
    return None


def find_rpm_files(directory):
    """Recursively find all .rpm files under the given directory."""
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files if file.endswith(".rpm")
    ]


def copy_files(file_list, dest_dir):
    """Copy each file from file_list to dest_dir."""
    for file in file_list:
        shutil.copy(file, dest_dir)


def setup_directory(module, path, permission):
    """Create or reset a directory with the specified permissions."""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    module.run_command(["chmod", permission, path])


def extract_rpm(module, src_rpm, dest_dir, fail_msg):
    """Extract the RPM using rpm2cpio + cpio."""
    cmd = f"set -o pipefail && cd {dest_dir} && rpm2cpio {src_rpm} | cpio -idm"
    rc, out, err = module.run_command(["bash", "-c", cmd])
    if rc != 0:
        module.fail_json(msg=fail_msg, stderr=err)


def create_repo(module, repo_dir):
    """Initialize a yum repo in the specified directory."""
    rc, out, err = module.run_command(["createrepo", repo_dir])
    if rc != 0:
        module.fail_json(msg="Failed to create repository.", stderr=err)


def main():
    """Perform the main tasks."""
    module_args = {
        "cuda_tmp_path": {"type": "str", "required": True},
        "cuda_core_path": {"type": "str", "required": True},
        "cuda_toolkit_path": {"type": "str", "required": True},
        "repo_permission": {"type": "str", "required": True},
        "invalid_cuda_rpm_fail_msg": {"type": "str", "required": True}
    }

    module = AnsibleModule(argument_spec=module_args)

    params = module.params
    tmp_path = params["cuda_tmp_path"]
    core_path = params["cuda_core_path"]
    rpm_path = params["cuda_toolkit_path"]
    permission = params["repo_permission"]
    fail_msg = params["invalid_cuda_rpm_fail_msg"]

    try:
        setup_directory(module, tmp_path, permission)
        setup_directory(module, core_path, permission)
        extract_rpm(module, rpm_path, tmp_path, fail_msg)

        rpm_dir = find_cuda_rpm_folder(tmp_path)
        if not rpm_dir:
            module.warn("CUDA RPM folder not found.")
            module.exit_json(changed=False, msg="CUDA RPM folder not found.")

        rpm_files = find_rpm_files(rpm_dir)
        copy_files(rpm_files, core_path)
        create_repo(module, core_path)

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)

    module.exit_json(changed=True, msg="CUDA RPM files copied to CUDA core repository.")


if __name__ == "__main__":
    main()
