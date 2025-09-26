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
# pylint: disable=import-error,no-name-in-module,too-many-arguments,unused-argument
"""
This module contains functions for validating common configuration files.
"""
import json
import os
import yaml
import ipaddress
import subprocess
from collections import Counter
from ast import literal_eval
import ansible.module_utils.input_validation.common_utils.data_fetch as fetch
from ansible.module_utils.input_validation.validation_flows import csi_driver_validation
import ansible.module_utils.input_validation.common_utils.data_validation as validate

from ansible.module_utils.input_validation.common_utils import (
    validation_utils,
    config,
    en_us_validation_msg,
    data_verification
)

from ansible.module_utils.input_validation.validation_flows import scheduler_validation
from ansible.module_utils.local_repo.software_utils import (
    load_json,
    load_yaml,
    get_subgroup_dict,
    get_software_names,
    get_json_file_path
)

file_names = config.files
create_error_msg = validation_utils.create_error_msg
create_file_path = validation_utils.create_file_path
contains_software = validation_utils.contains_software
check_mandatory_fields = validation_utils.check_mandatory_fields
flatten_sub_groups = validation_utils.flatten_sub_groups
file_exists = data_verification.file_exists


def validate_software_config(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the software configuration.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.
    """
    errors = []
    cluster_os_type = data["cluster_os_type"]
    cluster_os_version = data["cluster_os_version"]
    os_version_ranges = config.os_version_ranges

    if cluster_os_type.lower() in os_version_ranges:
        version_range = os_version_ranges[cluster_os_type.lower()]
        if cluster_os_type.lower() in ["rhel", "rocky"]:
            if float(cluster_os_version) != float(version_range[0]):
                errors.append(
                    create_error_msg(
                        "cluster_os_version",
                        cluster_os_version,
                        en_us_validation_msg.os_version_fail_msg(
                            cluster_os_type, version_range[0], None
                        ),
                    )
                )
        elif cluster_os_type.lower() == "ubuntu":
            if cluster_os_version not in version_range:
                errors.append(
                    create_error_msg(
                        "cluster_os_version",
                        cluster_os_version,
                        en_us_validation_msg.os_version_fail_msg(
                            cluster_os_type, version_range[0], version_range[1]
                        ),
                    )
                )

    #software groups and subgroups l2 validation
    # Check for the additional software field
    if "additional_software" in data:
        # Run schema validation and call validate_additional_software()
        schema_base_file_path = os.path.join(module_utils_base,'input_validation','schema')
        passwords_set = config.passwords_set
        extensions = config.extensions
        fname = "additional_software"
        schema_file_path = schema_base_file_path + "/" + fname + extensions['json']
        json_files = fetch.files_recursively(omnia_base_dir + "/" + project_name, extensions['json'])
        json_files_dic = {}

        for file_path in json_files:
            json_files_dic.update({fetch.file_name_from_path(file_path): file_path})
        new_file_path = json_files_dic.get("additional_software.json", None)

        # Validate the schema of the input file (L1)
        validation_status = {"Passed": [], "Failed": []}
        vstatus = []
        project_data = {project_name: {"status": [], "tag": "additional_software"}}
        validation_status.update(project_data)
        schema_status = validate.schema({
                            "input_file_path": new_file_path,
                            "schema_file_path": schema_file_path,
                            "passwords_set": passwords_set,
                            "omnia_base_dir": omnia_base_dir,
                            "project_name": project_name,
                            "logger": logger,
                            "module": module,
                        })
        vstatus.append(schema_status)

        # Append the validation status for the input file
        if schema_status:
            validation_status["Passed"].append(new_file_path)
        else:
            validation_status["Failed"].append(new_file_path)

        if False in vstatus:
            log_file_name = os.path.join(
                config.input_validator_log_path, f"validation_omnia_{project_name}.log")
            message = (f"Input validation failed for: {project_name} - additional_software.json"
               f"Look at the logs for more details: filename={log_file_name}")

            module.fail_json(
                msg=message,
                log_file_name=log_file_name,
                passed_files=validation_status["Passed"],
                failed_files=validation_status["Failed"]
            )

        # Check for the addtional_software.json file exist
        if new_file_path is None or not file_exists(new_file_path, module, logger):
            logger.info("The additional_software.json does not exist...")
            errors.append(
                create_error_msg(
                    "additional_software.json",
                    new_file_path,
                    en_us_validation_msg.MISSING_ADDITIONAL_SOFTWARE_JSON_FILE))
            return errors
        additional_software_data = None
        with open(json_files_dic["additional_software.json"], "r", encoding="utf-8") as schema_file:
            additional_software_data = json.load(schema_file)

        additional_software_errors = validate_additional_software(
            new_file_path, additional_software_data,
            logger, module, omnia_base_dir, module_utils_base, project_name)
        errors.extend(additional_software_errors)

    # create the subgroups and softwares dictionary with version details
    subgroup_dict, _ = get_subgroup_dict(data)
    # check if the corresponding json files for softwares and subgroups exists in config folder
    validation_results = []
    failures = []
    fail_data = []

    # Ensure "default_packages" is present in software_config.json
    software_names = [pkg.get('name') for pkg in data.get('softwares', [])]
    if "default_packages" not in software_names:
        errors.append(
            create_error_msg(
                "Validation Error: ",
                "default_packages",
                "is mandatory in softwares_config.json but is missing."
            )
        )

    # Ensure software names are unique in ['softwares']
    sw_duplicates = [sw_name for sw_name, count in Counter(software_names).items() if count > 1]
    if sw_duplicates:
        errors.append(
            create_error_msg(
                "Validation Error: ",
                "Duplicate software names found:",
                f"{', '.join(sw_duplicates)}"
            )
        )

    for software_pkg in data['softwares']:
        software = software_pkg['name']
        arch_list = software_pkg.get('arch')
        json_paths = []
        for arch in arch_list:
            json_paths.append(get_json_file_path(
                software, cluster_os_type, cluster_os_version, input_file_path, arch))
        for json_path in json_paths:
            # Check if json_path is None or if the JSON syntax is invalid
            if not json_path:
                errors.append(
                    create_error_msg(
                        "Validation Error: ", software,
                        f"is present in software_config.json. JSON file not found: {software}.json"
                    )
                )
            else:
                try:
                    subgroup_softwares = subgroup_dict.get(software, None)
                    json_data = load_json(json_path)
                    for subgroup_software in subgroup_softwares:
                        _, fail_data = validation_utils.validate_softwaresubgroup_entries(
                            subgroup_software, json_path, json_data, validation_results, failures
                        )

                except (FileNotFoundError, json.JSONDecodeError) as e:
                    errors.append(
                        create_error_msg("Error opening or reading JSON file:", json_path, str(e))
                    )

    if fail_data:
        errors.append(
            create_error_msg(
                "Software config subgroup validation failed for",
                fail_data,
                "Please resolve the issues first before proceeding.",
            )
        )

    return errors

def is_version_valid(actual_version, expected):
    if isinstance(expected, list):
        return actual_version in expected
    return actual_version == expected

def validate_versions(data, expected):
    mismatches = []
    # Validate top-level 'softwares'
    for sw in data.get("softwares", []):
        name = sw.get("name")
        version = sw.get("version")
        expected_version = expected.get(name)

        if expected_version:
            if not version:
                mismatches.append(f"{name} is missing a version")
            elif not is_version_valid(version, expected_version):
                mismatches.append(f"{name} version mismatch: expected {expected_version}, got {version}")

    # Validate subgroup software (e.g. "amdgpu": [{...}])
    for parent_key, children in data.items():
        if parent_key == "softwares" or not isinstance(children, list):
            continue

        for sub_sw in children:
            name = sub_sw.get("name")
            version = sub_sw.get("version")
            expected_version = expected.get(name)

            # Skip if version is not provided
            if expected_version and version:
                if not is_version_valid(version, expected_version):
                    mismatches.append(
                        f"{name} version mismatch in {parent_key}: expected {expected_version}, got {version}"
                    )

    return mismatches


def validate_openldap_input_params(authentication_type, mandatory_fields, data, errors, _logger):

    """
    Validates the input parameters for the OpenLDAP authentication.

    Args:
        authentication_type (str): Type of authentication.
        mandatory_fields (list): List of mandatory fields required for validation.
        data (dict): Input data containing the parameters to be validated.
        errors (list): List to store error messages.
        logger (object): Logger object for logging information.

    Notes:
        - The function checks if all mandatory fields are present in the input data.
        - It validates the `ldap_connection_type` field to ensure it is one of the supported types.
        - It also validates the certificate paths for TLS connections.
        - If any validation fails, an error message is appended to the `errors` list.

    Validation Rules:
        - All mandatory fields should be present in the input data.
        - The `ldap_connection_type` field should be one of the supported types
        (defined in `config.supported_ldap_connection_type`).
        - The certificate paths for TLS connections should be valid and existing files.

    Returns:
        None
    """

    check_mandatory_fields(mandatory_fields, data, errors)

    # validate ldap_connection_type
    ldap_connection_type = data.get("ldap_connection_type","").upper()
    if ldap_connection_type and ldap_connection_type not in config.supported_ldap_connection_type:
        errors.append(
            create_error_msg(authentication_type,
                            "software",
                            en_us_validation_msg.LDAP_CONNECTION_TYPE_FAIL_MSG)
        )

    certificates = {
        "tls_ca_certificate": data.get("tls_ca_certificate", ""),
        "tls_certificate": data.get("tls_certificate", ""),
        "tls_certificate_key": data.get("tls_certificate_key",""),
    }

    for cert_name, cert_value in certificates.items():
        if cert_value and not validation_utils.verify_path(cert_value):
            errors.append(
                create_error_msg(cert_name,
                                cert_value,
                                en_us_validation_msg.LDAP_CERT_PATH_FAIL_MSG)
            )

def validate_freeapi_input_params(authentication_type, mandatory_fields, data, errors, logger):

    """
    Validates the input parameters for the Free API.

    Args:
        authentication_type (str): Type of authentication.
        mandatory_fields (list): List of mandatory fields required for validation.
        data (dict): Input data containing the parameters to be validated.
        errors (list): List to store error messages.
        logger (object): Logger object for logging information.

    Notes:
        - The function checks if all mandatory fields are present in the input data.
        - It validates the `realm_name` field to ensure it contains a dot (`.`) character.
        - If any validation fails, an error message is appended to the `errors` list.

    Returns:
        None
    """

    check_mandatory_fields(mandatory_fields, data, errors)
    # validate realm_name
    realm_name = data.get("realm_name", "")
    if realm_name and "." not in realm_name:
        errors.append(
            create_error_msg("realm_name",
                            realm_name,
                            en_us_validation_msg.REALM_NAME_FAIL_MSG)
        )

def validate_security_config(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the security configuration.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.
    """
    errors = []
    software_config_json = create_file_path(
        input_file_path, file_names["software_config"]
    )
    software_list = get_software_names(software_config_json)
    authentication_type = ""
    required = {"openldap"}

    matches = [value for value in required if value in software_list]
    if matches:
        authentication_type = matches[0]
        logger.info(f"{authentication_type}: "
                    f"{en_us_validation_msg.AUTHENTICATION_SYSTEM_SUCCESS_MSG}")
    else:
        logger.warn(f"{en_us_validation_msg.AUTHENTICATION_SYSTEM_FAIL_MSG}")

    if authentication_type == "openldap":
        mandatory_fields = [
            "domain_name",
            "ldap_connection_type",
            "openldap_organization",
            "openldap_organizational_unit",
        ]
        validate_openldap_input_params(authentication_type, mandatory_fields, data, errors, logger)

    return errors


def validate_network_config(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the network configuration.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.
    """
    errors = []
    mlnx_ofed_offline_path = data["mlnx_ofed_offline_path"]
    if mlnx_ofed_offline_path and not validation_utils.verify_path(mlnx_ofed_offline_path):
        errors.append(
            create_error_msg(
                "mlnx_ofed_offline_path",
                mlnx_ofed_offline_path,
                en_us_validation_msg.FILE_PATH_FAIL_MSG,
            )
        )

    return errors

def get_matching_clusters_for_nfs(nfs_name, omnia_config):
    """
    Returns a dict of matching clusters for the given NFS name.
    """
    matching_clusters = {}

    # Service k8s
    for svc in omnia_config.get("service_k8s_cluster", []):
        if (
            svc.get("nfs_storage_name") == nfs_name
            and svc.get("deployment") is True
        ):
            matching_clusters["service_k8s_cluster"] = svc

    # Slurm
    for slurm in omnia_config.get("slurm_cluster", []):
        if slurm.get("nfs_storage_name") == nfs_name:
            matching_clusters["slurm_cluster"] = slurm

    return matching_clusters

def validate_storage_config(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the storage configuration.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.
    """
    errors = []
    software_config_file_path = create_file_path(input_file_path, file_names["software_config"])
    omnia_config_file_path = create_file_path(input_file_path, file_names["omnia_config"])

    #read contents of omnia_config file in a variable
    omnia_config_json = validation_utils.load_yaml_as_json(
        omnia_config_file_path, omnia_base_dir, project_name, logger, module
    )

    software_config_json = None
    with open(software_config_file_path, "r", encoding="utf-8") as schema_file:
        software_config_json = json.load(schema_file)
    softwares = software_config_json["softwares"]

    allowed_options = {"nosuid", "rw", "sync", "hard", "intr"}

    for nfs_client_params in data["nfs_client_params"]:
        client_mount_options = nfs_client_params["client_mount_options"]
        client_mount_options_set = set(client_mount_options.split(","))

        if not (client_mount_options_set.issubset(allowed_options)):
            errors.append(
                create_error_msg(
                    "client_mount_options",
                    client_mount_options,
                    en_us_validation_msg.CLIENT_MOUNT_OPTIONS_FAIL_MSG,
                )
            )

        nfs_strg_name = nfs_client_params["nfs_name"]
        matching_clusters = get_matching_clusters_for_nfs(nfs_strg_name, omnia_config_json)

        if not matching_clusters:
            errors.append(
                create_error_msg(
                    "For the mentioned",
                    nfs_strg_name,
                    f"in storage_config.yml, no matching cluster found in omnia_config.yml "
                    f"with deployment enabled for NFS '{nfs_strg_name}'."
                )
            )
    return errors


def validate_roce_plugin_config(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the RoCE plugin configuration.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.
    """
    errors = []
    return errors

def validate_allowed_services(data, errors, logger):

    """
    Validates the restrict_softwares field in the input data against a list of allowed services.

    Args:
        data (dict): The input data containing the restrict_softwares field.
        errors (list): A list to store error messages encountered during validation.
        logger (Logger): A logger instance for logging purposes.

    Returns:
        None

    Notes:
        The allowed services are: telnet, lpd, bluetooth, rlogin, and rexec.
        If a restrict_software is not in the allowed services list,
        an error message is appended to the errors list.

    Raises:
        None
    """
    restrict_program_support = data.get("restrict_program_support", False)
    if restrict_program_support:
        # validate allowed services
        allowed_services = ["telnet", "lpd", "bluetooth", "rlogin", "rexec"]
        restrict_softwares = data["restrict_softwares"].split(",")
        for software in restrict_softwares:
            if software not in allowed_services:
                errors.append(
                    create_error_msg(
                        "restrict_softwares",
                        data["restrict_softwares"],
                        en_us_validation_msg.restrict_softwares_fail_msg(software),
                    )
                )

def validate_alert_email_address(data, errors, logger):
    """
    Validates the alert email address provided in the input data.

    Args:
        data (dict): Input data containing the alert email address.
        errors (list): List to store error messages.
        logger (object): Logger object for logging warnings.

    Returns:
        list: List of validated alert email addresses.

    Notes:
        - If the alert email address is empty, a warning message is logged.
        - Each email address is checked for maximum length and presence of a search key.
        - Error messages are appended to the `errors` list for invalid email addresses.
    """
    alert_email_address = data.get("alert_email_address", "")
    alert_email_address_list = []

    if not alert_email_address:
        logger.warn(en_us_validation_msg.ALERT_EMAIL_WARNING_MSG)
    else:
        alert_email_address_list = alert_email_address.split(",")

    for email_id in alert_email_address_list:
        if len(email_id) > config.EMAIL_MAX_LENGTH or config.EMAIL_SEARCH_KEY not in email_id:
            errors.append(
                create_error_msg(
                    "email_id",
                    email_id,
                    en_us_validation_msg.ALERT_EMAIL_FAIL_MSG
                )
            )
    return alert_email_address_list

def validate_smtp_server(data, errors, logger):

    """
    Validates the SMTP server configuration provided in the input data.

    Args:
        data (dict): Input data containing the SMTP server configuration.
        errors (list): List to store error messages.
        logger (object): Logger object for logging information.

    Notes:
        - The function checks if the SMTP server configuration is a single, non-empty dictionary.
        - It verifies that the configuration contains the required fields:
        host, port, and sender address.
        - If the configuration is invalid or missing required fields,
        an error message is appended to the `errors` list.

    Returns:
        None
    """

    smtp_server = data.get("smtp_server","")
    logger.info(f"smpt server info info {smtp_server}")
    if len(smtp_server) != 1 or len(smtp_server) < 0:
        errors.append(
            create_error_msg(
                "smpt_server",
                smtp_server,
                en_us_validation_msg.SMTP_SERVER_FAIL_MSG
            )
        )

    if len(smtp_server) == 1:
        host = smtp_server[0].get("host","")
        port = smtp_server[0].get("port","")
        sender_address = smtp_server[0].get("sender_address","")

        if not host or not port or not sender_address:
            errors.append(
                create_error_msg(
                        "smpt_server",
                        smtp_server,
                        en_us_validation_msg.SMTP_SERVER_FAIL_MSG
                )
            )

def validate_login_node_security_config(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the login node security configuration.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.
    """
    errors = []

    software_config_json = create_file_path(
        input_file_path, file_names["software_config"]
    )

    software_list = get_software_names(software_config_json)

    enable_secure_login_node = False

    if "secure_login_node" in software_list:
        enable_secure_login_node = True

    if enable_secure_login_node:
        logger.info("secure_login_node is enabled")
        alert_email_address_list = validate_alert_email_address(data, errors, logger)
        if len(alert_email_address_list) > 0:
            validate_smtp_server(data, errors, logger)
        validate_allowed_services(data, errors, logger)
    return errors

def validate_server_spec(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the server specification.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.
    """
    errors = []
    server_groups = data["Categories"]
    server_spec_nicnetworks = []
    network_spec_networks = []

    # Early return if Categories are None or empty
    if server_groups is None:
        return errors

    network_spec_file_path = create_file_path(input_file_path, file_names["network_spec"])
    network_spec_json = validation_utils.load_yaml_as_json(
        network_spec_file_path, omnia_base_dir, project_name, logger, module
    )

    for server in server_groups:
        for _, value in server.items():
            for item in value:
                # Handle network specifications
                if "network" in item:
                    for network in item["network"]:
                        for network_key, network_value in network.items():
                            # Collecting the nicnetwork
                            server_spec_nicnetworks.append(network_value["nicnetwork"])
                            # Validating nicdevices if present
                            if "nicdevices" in network_value:
                                if not network_key.startswith(network_value.get("nicdevices")):
                                    errors.append(
                                        create_error_msg(
                                            f"{network_key}",
                                            None,
                                            en_us_validation_msg.server_spec_network_key_fail_msg(
                                                network_value["nicdevices"]
                                            ),
                                        )
                                    )

    # Collecting network_spec nicnetwork names
    for _, network in network_spec_json.items():
        for nw in network:
            for name, value in nw.items():
                network_spec_networks.append(name)

    # Validating that all server nicnetworks exist in network_spec.yml
    for item in server_spec_nicnetworks:
        if item not in network_spec_networks:
            errors.append(
                create_error_msg(
                    f'nicnetwork: "{item}"',
                    None,
                    en_us_validation_msg.SERVER_SPEC_NICNETWORKS_FAIL_MSG,
                )
            )

    return errors


def get_admin_networks(
    input_file_path, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Retrieves the admin network from the network specification.

    Args:
        input_file_path (str): The path to the input file.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        dict: A dictionary containing the admin network.
    """
    network_spec_file_path = create_file_path(input_file_path, file_names["network_spec"])
    network_spec_json = validation_utils.load_yaml_as_json(
        network_spec_file_path, omnia_base_dir, project_name, logger, module
    )
    admin_networks = {}

    for network in network_spec_json["Networks"]:
        for key, value in network.items():
            if key in ["admin_network"]:
                dynamic_range = value.get("dynamic_range", "N/A")
                admin_networks[key] = {
                    "dynamic_range": dynamic_range,
                    "primary_oim_admin_ip": value.get("primary_oim_admin_ip")
                }
    return admin_networks

def is_ip_in_range(ip_str, ip_range_str):
    """
    Checks if the given IP address is inside the given IP range.
    The range format should be: "start_ip-end_ip"
    """
    try:
        ip = ipaddress.IPv4Address(ip_str)
        start_ip_str, end_ip_str = ip_range_str.strip().split("-")
        start_ip = ipaddress.IPv4Address(start_ip_str)
        end_ip = ipaddress.IPv4Address(end_ip_str)
        return start_ip <= ip <= end_ip
    except ValueError:
        return False


def validate_k8s(data, admin_networks, softwares, ha_config, tag_names, errors, 
                 st_config, module, input_file_path):
    """
    Validates Kubernetes cluster configurations.

    Parameters:
        data (dict): A dictionary containing Kubernetes cluster configurations.
        admin_networks (dict): A dictionary containing admin network information.
        softwares (list): A list of software name sin software_config.
        errors (list): A list to store error messages.
    """
    admin_dynamic_range = admin_networks["admin_network"]["dynamic_range"]
    primary_oim_admin_ip = admin_networks["admin_network"]["primary_oim_admin_ip"]

    # service_k8s_cluster = data["service_k8s_cluster"]
    cluster_set = {}

    if "service_k8s" in softwares and "service_k8s" in tag_names:
        cluster_set["service_k8s_cluster"] = data.get(
            "service_k8s_cluster", [])

    for k8s_cluster_type, k8s_clusters in cluster_set.items():
        deployments_list = [k.get('deployment', False) for k in k8s_clusters]
        true_count = deployments_list.count(True)

        if true_count > 1:
            errors.append(create_error_msg(
                f"{k8s_cluster_type} Multiple cluster", true_count,
                "There are multiple deployment values as True in the "
                "service_k8s_cluster and compute_k8s_cluster"))
        if not true_count:
            errors.append(create_error_msg(
                "No cluster deployment is true", true_count,
                "There should be atleast one cluster deployment set to True"))
        for kluster in k8s_clusters:
            cluster_name = kluster.get("cluster_name")
            deployment = kluster.get("deployment")
            if deployment:
                nfs_names = [st.get('nfs_name') for st in st_config.get('nfs_client_params')]
                k8s_nfs = kluster.get("nfs_storage_name")
                if not k8s_nfs:
                    errors.append(
                        create_error_msg(
                            f"Cluster - {cluster_name}",
                            "nfs_storage_name not provided",
                            f"nfs_storage_name not found in service_k8s_cluster {cluster_name}"
                        )
                    )
                if k8s_nfs not in nfs_names:
                    errors.append(
                        create_error_msg(
                            f"Cluster - {cluster_name} - nfs_storage_name not found",
                            k8s_nfs,
                            f"{k8s_nfs} not found in storage_config.yml"
                        ))
                if cluster_name not in ha_config.get(k8s_cluster_type+"_ha", []):
                    errors.append(
                        create_error_msg(
                            f"Cluster - {cluster_name} - not found in high_availability_config.yml",
                            cluster_name,
                            f"{cluster_name} not found in high_availability_config.yml"
                        ))
                pod_external_ip_range = kluster.get("pod_external_ip_range")
                if not pod_external_ip_range or str(pod_external_ip_range).strip() == "":
                    errors.append(
                        create_error_msg(
                            "Pod External IP Range -",
                            pod_external_ip_range,
                            f"For Cluster with name - {cluster_name} - "
                            "The pod external IP range is not provided in omnia_config.yml"))
                else:
                    does_overlap = is_ip_in_range(
                        primary_oim_admin_ip, pod_external_ip_range)
                    if does_overlap:
                        errors.append(
                            create_error_msg(
                                "Ip Overlap:",
                                does_overlap,
                                f"For Cluster with name - {cluster_name} - "
                                "The pod external IP range provided in omnia_config.yml overlaps "
                                "with the admin ip defined in network_spec.yml"))
                k8s_service_addresses = kluster.get("k8s_service_addresses")
                k8s_pod_network_cidr = kluster.get("k8s_pod_network_cidr")
                # k8s_offline_install = kluster.get("k8s_offline_install")
                ip_ranges = [
                    admin_dynamic_range,
                    k8s_service_addresses,
                    k8s_pod_network_cidr]
                does_overlap, _ = validation_utils.check_overlap(ip_ranges)
                if does_overlap:
                    errors.append(
                        create_error_msg(
                            "IP overlap -",
                            None,
                           en_us_validation_msg.IP_OVERLAP_FAIL_MSG))

                #csi validation
                if (
                      "csi_driver_powerscale" in softwares
                      and ("service_k8s" in softwares)
                    ):

                    csi_secret_file_path = kluster.get("csi_powerscale_driver_secret_file_path")
                    csi_values_file_path = kluster.get("csi_powerscale_driver_values_file_path")
                    
                    # Validate secret file path
                    if not csi_secret_file_path or \
                    not csi_secret_file_path.strip() or \
                    not os.path.exists(csi_secret_file_path.strip()):
                        errors.append(
                            create_error_msg(
                                "csi_powerscale_driver_secret_file_path",
                                csi_secret_file_path,
                                en_us_validation_msg.CSI_DRIVER_SECRET_FAIL_MSG,
                            )
                        )
                    else:
                        # If secret path is valid, ensure values path is also valid
                        if not csi_values_file_path or \
                        not csi_values_file_path.strip() or \
                        not os.path.exists(csi_values_file_path.strip()):
                            errors.append(
                                create_error_msg(
                                    "csi_powerscale_driver_values_file_path",
                                    csi_values_file_path,
                                    en_us_validation_msg.CSI_DRIVER_VALUES_FAIL_MSG,
                                )
                            )
                        csi_driver_validation.validate_powerscale_secret_and_values_file(csi_secret_file_path,csi_values_file_path, errors, input_file_path)

def validate_omnia_config(
        input_file_path,
        data,
        logger,
        module,
        omnia_base_dir,
        module_utils_base,
        project_name):
    """
    Validates the L2 logic of the omnia_config.yml file.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (object): The logger to be used.
        module (object): The module to be used.
        omnia_base_dir (str): The base directory of Omnia.
        module_utils_base (str): The base directory of module_utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors.
    """
    errors = []
    tag_names = module.params["tag_names"]

    software_config_file_path = create_file_path(
        input_file_path, file_names["software_config"])
    with open(software_config_file_path, "r", encoding="utf-8") as f:
        software_config_json = json.load(f)
    softwares = software_config_json["softwares"]
    sw_list = [k['name'] for k in softwares]

    storage_config = create_file_path(
        input_file_path, file_names["storage_config"])
    with open(storage_config, "r", encoding="utf-8") as f:
        st_config = yaml.safe_load(f)

    if ("service_k8s" in sw_list) and \
        ("service_k8s" in tag_names):
        admin_networks = get_admin_networks(
            input_file_path, logger, module, omnia_base_dir, module_utils_base, project_name)
        ha_config_path = create_file_path(
            input_file_path, file_names["high_availability_config"])
        with open(ha_config_path, "r", encoding="utf-8") as f:
            ha_config = yaml.safe_load(f)
        for k in ["service_k8s_cluster_ha"]:
            ha_config[k] = [xha["cluster_name"] for xha in ha_config.get(k, [])]
        validate_k8s(data, admin_networks, sw_list, ha_config, tag_names,
                        errors, st_config, module, input_file_path)
    # slurm L2
    if (("slurm" in sw_list or "slurm_custom" in sw_list) and "slurm" in tag_names):     
        slurm_nfs = [clst.get('nfs_storage_name') for clst in data.get('slurm_cluster')]
        nfs_names = [st.get('nfs_name') for st in st_config.get('nfs_client_params')]

        diff_set = set(slurm_nfs).difference(set(nfs_names))
        if diff_set:
            errors.append(
                create_error_msg(
                    input_file_path,
                    "slurm NFS not provided",
                    f"NFS name {', '.join(diff_set)} required for slurm is not defined in {storage_config}"
                    ))
    return errors

def check_is_service_cluster_functional_groups_defined(
    errors, input_file_path, omnia_base_dir, project_name, logger, module
):
    """
    Checks if 'service_kube_node_x86_64' is configured in the functional_groups_config.yml file,
    and ensures its cluster_name does not overlap with any Slurm role.

    Args:
        errors (list): A list to store error messages.
        input_file_path (str): The path to the input file.
        omnia_base_dir (str): The base directory for Omnia.
        project_name (str): The name of the project.
        logger (object): A logger object for logging messages.
        module (object): A module object for logging messages.

    Returns:
        True if 'service_kube_node_x86_64' is defined and valid, else False
    """
    functional_groups_config_file_path = create_file_path(
        input_file_path, file_names["functional_groups_config"]
    )
    functional_groups_config_json = validation_utils.load_yaml_as_json(
        functional_groups_config_file_path, omnia_base_dir, project_name, logger, module
    )
    functional_groups = functional_groups_config_json.get("functional_groups", [])

    kube_cluster = None
    slurm_clusters = set()

    for group in functional_groups:
        name = group.get("name", "")
        cluster = group.get("cluster_name", "")

        # Capture kube service cluster
        if name == "service_kube_node_x86_64":
            kube_cluster = cluster

        # Collect slurm clusters
        if name in [
            "slurm_control_node_x86_64",
            "slurm_node_x86_64",
            "slurm_node_aarch64",
        ]:
            if cluster:
                slurm_clusters.add(cluster)

    if kube_cluster:
        if kube_cluster in slurm_clusters:
            errors.append(
                create_error_msg(
                    "functional_groups_config.yml",
                    kube_cluster,
                    en_us_validation_msg.SLURM_KUBE_CLUSTER_OVERLAP_MSG.format(
                        cluster=kube_cluster
                    ),
                )
            )
            return False
        return True

    return False

def validate_telemetry_config(
    input_file_path,
    data,
    logger,
    module,
    omnia_base_dir,
    _module_utils_base,
    project_name
):

    """
    Validates the telemetry configuration data.

    This function checks the telemetry configuration data for validity and consistency.
    It verifies that the iDRAC telemetry support and federated iDRAC telemetry collection
    settings are correctly configured.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The telemetry configuration data.
        logger (object): The logger object.
        module (object): The module object.
        omnia_base_dir (str): The base directory of the Omnia project.
        _module_utils_base (str): The base directory of the module utilities.
        project_name (str): The name of the project.

    Returns:
        None

    Raises:
        None

    """
    errors = []

    idrac_telemetry_support = data.get("idrac_telemetry_support")
    is_service_cluster_defined = check_is_service_cluster_functional_groups_defined(errors,
                                input_file_path,
                                omnia_base_dir,
                                project_name,
                                logger,
                                module)
    if idrac_telemetry_support and not is_service_cluster_defined:
        errors.append(create_error_msg(
            "idrac_telemetry_support can be",
            idrac_telemetry_support,
            en_us_validation_msg.TELEMETRY_SERVICE_CLUSTER_ENTRY_MISSING_ROLES_CONFIG_MSG
            )    
        )
    return errors

def validate_additional_software(
    input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name
):
    """
    Validates the additional software configuration.

    Args:
        input_file_path (str): The path to the input file.
        data (dict): The data to be validated.
        logger (Logger): A logger instance.
        module (Module): A module instance.
        omnia_base_dir (str): The base directory of the Omnia configuration.
        module_utils_base (str): The base directory of the module utils.
        project_name (str): The name of the project.

    Returns:
        list: A list of errors encountered during validation.

    """
    errors = []
    # Get all keys in the data
    raw_subgroups = list(data.keys())
    flattened_sub_groups = set(flatten_sub_groups(list(data.keys())))

    # Check if additional_software is not given in the config
    if "additional_software" not in flattened_sub_groups:
        errors.append(
            create_error_msg(
                "additional_software.json", None, en_us_validation_msg.ADDITIONAL_SOFTWARE_FAIL_MSG
            )
        )
        return errors

    # Get the roles config file
    config_file_path = omnia_base_dir.replace("../", "")
    roles_config_file_path = create_file_path(config_file_path, file_names["roles_config"])

    roles_config_json = validation_utils.load_yaml_as_json(
        roles_config_file_path, omnia_base_dir, project_name, logger, module
    )
    valid_roles = roles_config_json["Roles"]

    # Set of unique role names
    available_roles_and_groups = set(role["name"] for role in roles_config_json["Roles"])
    available_roles_and_groups.add("additional_software")

    # Add the set of all unique group names
    available_roles_and_groups.update(group for role in valid_roles for group in role["groups"])

    # Check if a role or group name is present in the roles config file
    for sub_group in flattened_sub_groups:
        if sub_group not in available_roles_and_groups:
            errors.append(
                create_error_msg(
                    "additional_software.json",
                    None,
                    en_us_validation_msg.ADDITIONAL_SOFTWARE_SUBGROUP_FAIL_MSG.format(sub_group),
                )
            )

    # Validate subgroups defined for additional_software in software_config.json
    # also present in additioanl_software.json
    software_config_file_path = create_file_path(config_file_path, file_names["software_config"])
    software_config_json = json.load(open(software_config_file_path, "r"))

    # check if additional_software is present in software_config.json
    if "addtional_software" not in software_config_json:
        logger.warn("The additional_software field is not present in software_config.json")
        software_config_json["additional_software"] = []

    sub_groups_in_software_config = list(
        sub_group["name"] for sub_group in software_config_json["additional_software"]
    )

    # Check for the additional_software key in software_config.json
    for sub_group in sub_groups_in_software_config:
        if sub_group not in raw_subgroups:
            errors.append(
                create_error_msg(
                    "software_config.json",
                    None,
                    en_us_validation_msg.MISSING_IN_ADDITIONAL_SOFTWARE_MSG.format(sub_group),
                )
            )
    return errors
