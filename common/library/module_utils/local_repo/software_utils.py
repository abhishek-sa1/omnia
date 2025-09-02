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
# pylint: disable=import-error,no-name-in-module

from collections import defaultdict
import os
import json
import csv
import yaml
from jinja2 import Template
import requests
from ansible.module_utils.local_repo.common_functions import is_encrypted, process_file
# Import default variables from config.py
from ansible.module_utils.local_repo.config import (
    PACKAGE_TYPES,
    CSV_COLUMNS,
    SOFTWARE_CONFIG_SUBDIR,
    DEFAULT_STATUS_FILENAME,
    RPM_LABEL_TEMPLATE,
    OMNIA_REPO_KEY,
    RHEL_OS_URL,
    SOFTWARES_KEY,
    USER_REPO_URL,
    REPO_CONFIG
)


def load_json(file_path):
    """
    Load JSON data from a file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The loaded JSON data.

    Raises:
        FileNotFoundError: If the file is not found.
        ValueError: If the JSON parsing fails.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: Failed to parse JSON in file '{file_path}'.")


def load_yaml(file_path):
    """
    Load YAML data from a file.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The loaded YAML data.

    Raises:
        FileNotFoundError: If the file is not found.
        yaml.YAMLError: If the YAML parsing fails.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def validate_repo_mappings(yaml_data, json_data):
    """
    Validates the repository mappings in the given JSON data against the YAML data.

    Args:
        yaml_data (dict): The YAML data containing the repository mappings.
        json_data (str): The path to the JSON file or the JSON data
        containing the package information.

    Returns:
        list: A list of error messages for invalid repository mappings.
    """
    user_repos = yaml_data.get("user_repo_url") or []
    omnia_repos = yaml_data.get("omnia_repo_url_rhel") or []

    valid_repos = [repo["name"] for repo in (user_repos + omnia_repos)]
    valid_repos.extend(['baseos', 'appstream', 'codeready-builder'])
    data = load_json(json_data)

    errors = []
    for section, section_data in data.items():
        if isinstance(section_data, dict):
            for cluster_name, cluster_data in section_data.items():
                for package in cluster_data:
                    if package.get("type") == 'rpm':
                        repo_name = package.get("repo_name")
                        if repo_name not in valid_repos:
                            error_msg = (
                                f"Error: Repository '{repo_name}' for "
                                f"package '{package['package']}' "
                                f"in subgroup '{section}' is not found in local_repo_config.yml"
                            )
                            errors.append(error_msg)
    return errors


def get_json_file_path(software_name, cluster_os_type, cluster_os_version, user_json_path):
    """
    Generate the file path for a JSON file based on the provided software name,
     cluster OS type, cluster OS version, and user JSON path.

    Parameters:
        software_name (str): The name of the software.
        cluster_os_type (str): The type of the cluster operating system.
        cluster_os_version (str): The version of the cluster operating system.
        user_json_path (str): The path to the user JSON file.

    Returns:
        str or None: The file path for the JSON file if it exists, otherwise None.
    """
    base_path = os.path.dirname(os.path.abspath(user_json_path))
    json_path = os.path.join(
        base_path,
        f'{SOFTWARE_CONFIG_SUBDIR}/{cluster_os_type}/{cluster_os_version}/{software_name}.json')
    if os.path.exists(json_path):
        return json_path
    return None


def get_csv_file_path(software_name, user_csv_dir):
    """
    Generates the absolute path of the CSV file based on the software name
    and the user-provided CSV directory.

    Parameters:
        software_name (str): The name of the software.
        user_csv_dir (str): The directory path where the CSV file is located.

    Returns:
        str: The absolute path of the CSV file if it exists, otherwise None.
    """
    status_csv_file_path = os.path.join(
        user_csv_dir, software_name, DEFAULT_STATUS_FILENAME)
    return status_csv_file_path


def is_remote_url_reachable(remote_url, timeout=10, client_cert=None, client_key=None, ca_cert=None):
    """
    Check if a remote URL is reachable with or without SSL client certs.
    If SSL certs are provided, the function will attempt to use them; otherwise,
    it defaults to a standard HTTP request.
    Args:
        remote_url (str): The URL to check for reachability.
        timeout (int, optional): The maximum number of seconds to wait for a response.
        Defaults to 10.
        client_cert (str, optional): Path to the client certificate file. Defaults to None.
        client_key (str, optional): Path to the client key file. Defaults to None.
        ca_cert (str, optional): Path to the CA certificate file. Defaults to None.
    Returns:
        bool: True if the URL is reachable (HTTP status 200), False otherwise.
    """
    try:
        # Check if SSL certs are provided and handle accordingly
        if client_cert and client_key and ca_cert:
            response = requests.get(
                remote_url,
                cert=(client_cert, client_key),
                verify=ca_cert,
                timeout=timeout
            )
        else:
            # Proceed with a regular HTTP request if no SSL certs are provided
            response = requests.get(remote_url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def transform_package_dict(data):
    """
    Transforms a dictionary of packages into a new dictionary.
    Args:
        data (dict): A dictionary of packages, where each key is a string and
                     each value is a list of dictionaries. Each dictionary in
                     the list represents a package and contains the following
                     keys: "type" (a string) and "package" (a string).
    Returns:
        dict: A new dictionary where each key is a string and each value is
              a list of dictionaries. Each dictionary in the list represents
              a package and contains the following keys: "type" (a string),
              "package" (a string), and "rpm_list" (a list of strings) if the
              package type is "rpm".
    """
    result = {}
    rpm_packages = defaultdict(list)

    for key, items in data.items():
        transformed_items = []

        for item in items:
            if item.get("type") == "rpm":
                rpm_packages[key].append(item["package"])
            elif item.get("type") == "rpm_list":
                rpm_packages[key].extend(item["package_list"])

            else:
                transformed_items.append(item)

        if rpm_packages[key]:
            transformed_items.append({
                "package": RPM_LABEL_TEMPLATE.format(key=key),
                "rpm_list": rpm_packages[key],
                "type": "rpm"
            })

        result[key] = transformed_items

    return result


def parse_repo_urls(repo_config, local_repo_config_path, version_variables, vault_key_path):
    """
    Parses the repository URLs from the given local repository configuration file.
    Args:
        repo_config (str): Repo configuration
        local_repo_config_path (str): The path to the local repository configuration file.
        version_variables (dict): A dictionary of version variables.
        vault_key_path: Ansible vault key path
    Returns:
        tuple: A tuple where the first element is either the parsed repository URLs as a JSON string
               (on success) or the rendered URL (if unreachable),
                and the second element is a boolean
               indicating success (True) or failure (False).
        str: The parsed repository URLs as a JSON string.
    """
    local_yaml = load_yaml(local_repo_config_path)
    repo_entries = local_yaml.get(OMNIA_REPO_KEY, [])
    rhel_repo_entry = local_yaml.get(RHEL_OS_URL, [])
    user_repo_entry = local_yaml.get(USER_REPO_URL, [])
    parsed_repos = []
    vault_key_path = os.path.join(
        vault_key_path, ".local_repo_credentials_key")
    if user_repo_entry:
        for url_ in user_repo_entry:
            name = url_.get("name", "unknown")
            url = url_.get("url", "")
            gpgkey = url_.get("gpgkey")
            ca_cert = url_.get("sslcacert", "")
            client_key = url_.get("sslclientkey", "")
            client_cert = url_.get("sslclientcert", "")
            policy_given = url_.get("policy", repo_config)
            policy = REPO_CONFIG.get(policy_given)
            for path in [ca_cert, client_key, client_cert]:
                mode = "decrypt"
                if path and is_encrypted(path):
                    result, message = process_file(path, vault_key_path, mode)
                    if result is False:
                        return f"Error during decrypt for user repository path:{path}", False

            if not is_remote_url_reachable(url, client_cert=client_cert,
                                           client_key=client_key, ca_cert=ca_cert):
                return url, False

            parsed_repos.append({
                "package": name,
                "url": url,
                "gpgkey": gpgkey if gpgkey else "null",
                "version": "null",
                "ca_cert": ca_cert,
                "client_key": client_key,
                "client_cert": client_cert,
                "policy": policy
            })

    for url_ in rhel_repo_entry:
        name = url_.get("name", "unknown")
        url = url_.get("url", "")
        gpgkey = url_.get("gpgkey")
        policy_given = url_.get("policy", repo_config)
        policy = REPO_CONFIG.get(policy_given)
        if not is_remote_url_reachable(url):
            return url, False

        parsed_repos.append({
            "package": name,
            "url": url,
            "gpgkey": gpgkey if gpgkey else "null",
            "version": "null",
            "policy": policy
        })

    for repo in repo_entries:
        name = repo.get("name", "unknown")
        url = repo.get("url", "")
        gpgkey = repo.get("gpgkey")
        version = version_variables.get(f"{name}_version")
        policy_given = repo.get("policy", repo_config)
        policy = REPO_CONFIG.get(policy_given)
        try:
            rendered_url = Template(url).render(version_variables)
        except Exception as e:
            print(f"Warning: Error rendering URL {url} - {str(e)}")
            rendered_url = url  # Fallback to original URL

        # To handle special case when software_config.json does not contain these
        if name in ["amdgpu", "rocm", "beegfs"] and (version is None or version == "null"):
            continue

        # Edge case for oneapi, snoopy, nvidia-repo
        elif not is_remote_url_reachable(rendered_url) and name not in ["oneapi", "snoopy", "nvidia-repo"]:
            return rendered_url, False

        parsed_repos.append({
            "package": name,
            "url": rendered_url,
            "gpgkey": gpgkey if gpgkey else "null",
            "version": version if version else "null",
            "policy": policy
        })

    return json.dumps(parsed_repos), True


def set_version_variables(user_data, software_names, cluster_os_version):
    """
    Generates a dictionary of version variables from the user data.
    Args:
        user_data (dict): The user data containing the software information.
        software_names (list): The list of software names to extract versions for.
        cluster_os_version (str): The version of the cluster operating system.
    Returns:
        dict: A dictionary of version variables, where the keys are the software names
              and the values are the corresponding versions.
    """
    version_variables = {}

    for software in user_data.get(SOFTWARES_KEY, []):
        name = software.get('name')
        if name in software_names and 'version' in software:
            version_variables[f"{name}_version"] = software['version']

    for key in software_names:
        for item in user_data.get(key, []):
            name = item.get('name')
            if 'version' in item:
                version_variables[f"{name}_version"] = item['version']

    version_variables["cluster_os_version"] = cluster_os_version
    return version_variables


def get_subgroup_dict(user_data):
    """
    Returns a tuple containing a dictionary mapping software names to subgroup lists,
    and a list of software names.
    """
    subgroup_dict = {}
    software_names = []

    for sw in user_data.get(SOFTWARES_KEY, []):
        software_name = sw['name']
        software_names.append(software_name)
        subgroups = [sw['name']] + [item['name']
                                    for item in user_data.get(software_name, [])]
        subgroup_dict[software_name] = subgroups if isinstance(
            user_data.get(software_name), list) else [sw['name']]
    return subgroup_dict, software_names


def get_csv_software(file_name):
    """
    Retrieves a list of software names from a CSV file.

    Parameters:
        file_name (str): The name of the CSV file.

    Returns:
        list: A list of software names.
    """
    csv_software = []

    if not os.path.isfile(file_name):
        return csv_software

    with open(file_name, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        csv_software = [row.get(CSV_COLUMNS["column1"], "").strip()
                        for row in reader]
    return csv_software


def get_failed_software(file_name):
    """
    Retrieves a list of failed software from a CSV file.

    Parameters:
        file_name (str): The name of the CSV file.

    Returns:
        list: A list of software names that failed.
    """
    failed_software = []

    if not os.path.isfile(file_name):
        return failed_software

    with open(file_name, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        failed_software = [
            str(row.get(CSV_COLUMNS["column1"]) or "").strip()
            for row in reader
            if str(row.get(CSV_COLUMNS["column2"]) or "").strip().lower() in ["", "failed"]
        ]

    return failed_software


def parse_json_data(file_path, package_types, failed_list=None, subgroup_list=None):
    """
    Retrieves a filtered list of items from a JSON file.

    Parameters:
        file_path (str): The path to the JSON file.
        package_types (list): A list of package types to filter.
        failed_list (list, optional): A list of failed packages. Defaults to None.
        subgroup_list (list, optional): A list of subgroups to filter. Defaults to None.

    Returns:
        list: The filtered list of items.
    """
    data = load_json(file_path)
    filtered_list = []

    for key, package in data.items():
        if subgroup_list is None or key in subgroup_list:
            for value in package.values():
                for item in value:
                    # Get package name
                    pkg_name = item.get("package")

                    # Construct possible match keys based on available fields
                    match_keys = {pkg_name}  # Base case: package name only

                    if "tag" in item and item["tag"]:
                        # Add package:tag
                        match_keys.add(f"{pkg_name}:{item['tag']}")

                    if "digest" in item and item["digest"]:
                        # Add package:digest
                        match_keys.add(f"{pkg_name}:{item['digest']}")

                    # Apply filtering
                    if item.get("type") in package_types and (failed_list is None or any(match in failed_list for match in match_keys)):
                        filtered_list.append(item)

    return filtered_list


def check_csv_existence(path):
    """
    Checks if a CSV file exists at the given path.

    Parameters:
        path (str): The path to the CSV file.

    Returns:
        bool: True if the CSV file exists, False otherwise.
    """
    return os.path.isfile(path)


def process_software(software, fresh_installation, json_path, csv_path, subgroup_list):
    """
    Processes the given software by parsing JSON data and returning a filtered list of items.

    Parameters:
        software (str): The name of the software.
        fresh_installation (bool): Indicates whether it is a fresh installation.
        json_path (str): The path to the JSON file.
        csv_path (str): The path to the CSV file.
        subgroup_list (list, optional): A list of subgroups to filter. Defaults to None.

    Returns:
        list: The filtered list of items.
    """
    failed_packages = None if fresh_installation else get_failed_software(
        csv_path)
    rpm_package_type = ['rpm']
    rpm_tasks = []
    if failed_packages is not None and any("RPMs" in software for software in failed_packages):
        rpm_tasks = parse_json_data(
            json_path, rpm_package_type, None, subgroup_list)

    combined = parse_json_data(
        json_path, PACKAGE_TYPES, failed_packages, subgroup_list) + rpm_tasks
    return combined, failed_packages


def get_software_names(data_path):
    """
    Retrieves a list of software names from a given data file.

    Parameters:
        data_path (str): The path to the data file.

    Returns:
        list: A list of software names.
    """
    data = load_json(data_path)
    return [software['name'] for software in data.get(SOFTWARES_KEY, [])]
