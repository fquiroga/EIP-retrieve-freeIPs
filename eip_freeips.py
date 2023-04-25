import logging
import json
import argparse
from SOLIDserverRest import SOLIDserverRest
from requests.exceptions import RequestException


def get_space_id(name):
    parameters = {
        "WHERE": "site_name='{}'".format(name),
        "limit": "1"
    }

    rest_answer = SDS_CON.query("ip_site_list", parameters)

    if rest_answer.status_code == 401:
        logging.error("Authentication failed. Check your username and password.")
        return None
    elif rest_answer.status_code != 200:
        logging.error("Error finding space %s: HTTP status %s", name, rest_answer.status_code)
        return None

    rjson = json.loads(rest_answer.content)

    return {
        'id': rjson[0]['site_id']
    }


def get_subnet_v4(name, space_id=None):
    parameters = {
        "WHERE": "subnet_name='{}' and is_terminal='1'".format(name),
        "TAGS": "network.gateway"
    }

    if space_id is not None:
        parameters['WHERE'] = parameters['WHERE'] + " and site_id='{}'".format(int(space_id))

    rest_answer = SDS_CON.query("ip_subnet_list", parameters)

    if rest_answer.status_code != 200:
        logging.error("Error finding subnet %s: HTTP status %s", name, rest_answer.status_code)
        return None

    rjson = json.loads(rest_answer.content)

    return {
        'id': rjson[0]['subnet_id']
    }


def get_next_free_address(subnet_id, number=1):
    parameters = {
        "subnet_id": str(subnet_id),
        "max_find": str(number)
    }

    rest_answer = SDS_CON.query("ip_address_find_free", parameters)

    if rest_answer.status_code == 404:
        logging.error("No free IP addresses found in subnet %s", subnet_id)
        return None
    elif rest_answer.status_code != 200:
        logging.error("Error finding free IP addresses in subnet %s: HTTP status %s", subnet_id, rest_answer.status_code)
        return None

    rjson = json.loads(rest_answer.content)

    result = {
        "free-addresses": []
    }

    for address in rjson:
        result['free-addresses'].append(address['hostaddr'])

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get free IP addresses in a given subnet and space.")
    parser.add_argument('-s', '--subnet_name', required=True, help='Subnet name to search for free IP addresses.')
    parser.add_argument('-p', '--space_id', required=True, help='ID of the space where the subnet is located.')
    parser.add_argument('-c', '--count_ip', required=False, help='Number of free IPs to retrieve.')
    parser.add_argument('-u', '--username', required=True, help='Username for EIP Appliance')
    parser.add_argument('-P', '--password', required=True, help='Password for EIP Appliance')
    parser.add_argument('-H', '--hostname', required=True, help='Hostname of EIP Appliance')

    args = parser.parse_args()
    hostname = args.hostname
    username = args.username
    password = args.password
    subnet_name = args.subnet_name
    space_id = args.space_id
    number = args.count_ip

    try:
        SDS_CON = SOLIDserverRest(hostname)
        SDS_CON.set_ssl_verify(False)
        SDS_CON.use_basicauth_sds(user=username, password=password)

        space_info = get_space_id(space_id)
        if space_info is None:
            logging.error("Space not found. Exiting.")
            exit(1)

        subnet_info = get_subnet_v4(subnet_name, space_info['id'])
        if subnet_info is None:
            logging.error("Subnet not found. Exiting.")
            exit(1)

        if number is not None:
            try:
                number = int(number)
                if number <= 0:
                    raise ValueError
            except ValueError:
                logging.error("Invalid count_ip value. Must be a positive integer.")
                exit(1)
        else:
            number = 100

        free_ips = get_next_free_address(subnet_info['id'], number)
        if free_ips is None:
            logging.error("Failed to get free IP addresses. Exiting.")
            exit(1)

        print(free_ips)
        del(SDS_CON)
        
    except RequestException as e:
        logging.error("Error connecting to SOLIDserver: %s", e)
        exit(1)
