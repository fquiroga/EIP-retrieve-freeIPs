# SOLIDserver IPAM IP Retrieval**

## Description:
This project retrieves a list of free IP addresses in a given subnet and space from SOLIDserver IPAM. The script takes subnet name, space ID, hostname, username, and password as input parameters.

### Dependencies:
- Python 3.6 or later
- SOLIDserverRest package

### Installation:
1. Install the required Python packages using the following command:
   pip install -r requirements.txt

2. Clone or download the project files to your local machine.

### Usage:
To run the script, use the following command:
python eip_freeips.py -s SUBNET_NAME -p SPACE_ID -u USERNAME -P PASSWORD -H HOSTNAME

Replace the following placeholders with your own values:

- SUBNET_NAME: The name of the subnet to search for free IP addresses.
- SPACE_ID: The ID of the space where the subnet is located.
- USERNAME: The username for the EIP appliance.
- PASSWORD: The password for the EIP appliance.
- HOSTNAME: The hostname of the EIP appliance.

### Optional arguments:
-c COUNT_IP: The number of free IP addresses to retrieve. If not specified, the default value is 100.
