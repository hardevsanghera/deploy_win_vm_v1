# Nutanix Windows VM Deployment Tool

This tool helps deploy Windows VMs to Nutanix AHV clusters via Prism Central using the Nutanix v3.1 REST API.

## Phase 1: Resource Selection

### Overview
The `deploy_win_vm.py` script connects to Nutanix Prism Central and displays all available:
- **Clusters** - Target AHV clusters for VM deployment
- **Subnets** - Available network subnets for VM connectivity  
- **Images** - Available disk images for VM creation
- **Sysprep Files** - Local sysprep XML files for Windows customization

The script allows you to interactively select the required resources for VM deployment.

### Prerequisites
- Python 3.7+ with virtual environment activated
- Network connectivity to Nutanix Prism Central
- Valid Prism Central credentials

### Required Python Packages
- requests>=2.25.1
- urllib3>=1.26.0

### Usage

1. **Activate your virtual environment** (if not already active):
   ```powershell
   .\env\Scripts\Activate.ps1
   ```

2. **Run the resource selector script**:
   ```powershell
   python deploy_win_vm.py <PC_IP> <USERNAME>
   ```
   
   Example:
   ```powershell
   python deploy_win_vm.py 10.1.1.100 admin
   ```

3. **Enter your password** when prompted (input will be hidden)

4. **Select resources** from the numbered lists displayed:
   - Choose a target cluster
   - Choose a network subnet
   - Choose a disk image
   - Choose a sysprep XML file

### Prerequisites for Sysprep Files
- Place sysprep XML files in the current directory
- Files must start with "sysprep" and end with ".xml"
- Examples: `sysprep_windows_server.xml`, `sysprep-win2019-prod.xml`

### Sample Output
```
Connecting to Prism Central at 10.1.1.100...
Successfully connected to Prism Central!
Found 3 clusters

============================================================
AVAILABLE CLUSTERS
============================================================
 1. NTNX-Cluster-01
     UUID: 00061663-4a18-7c31-185b-ac1f6b6029e1

 2. NTNX-Cluster-02
     UUID: 00061663-4a18-7c31-185b-ac1f6b6029e2

Please select a cluster (1-2): 2

Selected cluster: NTNX-Cluster-02
UUID: 00061663-4a18-7c31-185b-ac1f6b6029e2

Fetching subnets from Prism Central...
Found 4 subnets

============================================================
AVAILABLE SUBNETS
============================================================
 1. Production-Network
     UUID: 12345678-1234-5678-9abc-123456789012
     VLAN ID: 100
     Cluster: NTNX-Cluster-02

 2. Management-Network
     UUID: 87654321-4321-8765-cba9-210987654321
     VLAN ID: 200
     Cluster: NTNX-Cluster-01

Please select a subnet (1-2): 1

Selected subnet: Production-Network
UUID: 12345678-1234-5678-9abc-123456789012
VLAN ID: 100

Fetching images from Prism Central...
Found 6 images

============================================================
AVAILABLE IMAGES
============================================================
 1. Windows-Server-2022
     UUID: abcd1234-5678-90ef-ghij-klmn12345678
     Type: DISK_IMAGE
     Size: 15.5 GB

 2. CentOS-7-Template
     UUID: efgh5678-90ab-cdef-1234-567890abcdef
     Type: DISK_IMAGE
     Size: 8.2 GB

Please select an image (1-2): 1

Selected image: Windows-Server-2022
UUID: abcd1234-5678-90ef-ghij-klmn12345678
Type: DISK_IMAGE
Size: 15.5 GB

Searching for sysprep XML files in: C:\Users\hardev.sanghera\Documents\v3\deploy_win_vm
Found 3 sysprep XML file(s)

============================================================
AVAILABLE SYSPREP XML FILES
============================================================
 1. sysprep-win2019-AAA.xml
     Path: C:\Users\hardev.sanghera\Documents\v3\deploy_win_vm\sysprep-win2019-AAA.xml
     Size: 2.5 KB

 2. sysprep-win2019-BBB.xml
     Path: C:\Users\hardev.sanghera\Documents\v3\deploy_win_vm\sysprep-win2019-BBB.xml
     Size: 3.1 KB

 3. sysprep_windows_server.xml
     Path: C:\Users\hardev.sanghera\Documents\v3\deploy_win_vm\sysprep_windows_server.xml
     Size: 1.8 KB

Please select a sysprep XML file (1-3): 3

Selected sysprep file: sysprep_windows_server.xml
Path: C:\Users\hardev.sanghera\Documents\v3\deploy_win_vm\sysprep_windows_server.xml
Size: 1.8 KB

Deployment configuration saved to deployment_config.json
This file contains all settings needed for VM deployment.

============================================================
CONFIGURATION SUMMARY
============================================================
target_cluster = "NTNX-Cluster-02=00061663-4a18-7c31-185b-ac1f6b6029e2"
target_subnet  = "Production-Network=12345678-1234-5678-9abc-123456789012"
target_image   = "Windows-Server-2022=abcd1234-5678-90ef-ghij-klmn12345678"
sysprep_file   = "sysprep_windows_server.xml"

============================================================
DETAILED CONFIGURATION
============================================================
Cluster: NTNX-Cluster-02 (00061663-4a18-7c31-185b-ac1f6b6029e2)
Subnet:  Production-Network (12345678-1234-5678-9abc-123456789012) - VLAN 100
Image:   Windows-Server-2022 (abcd1234-5678-90ef-ghij-klmn12345678)
         Type: DISK_IMAGE, Size: 15.5 GB
Sysprep: sysprep_windows_server.xml (1.8 KB)
         Path: C:\Users\hardev.sanghera\Documents\v3\deploy_win_vm\sysprep_windows_server.xml

This configuration is ready for Windows VM deployment!
```

### Generated Files
- **deployment_config.json**: Contains the complete selected resource configuration for VM deployment

### Configuration File Format
```json
{
  "pc_ip": "10.1.1.100",
  "username": "admin",
  "target_cluster": "NTNX-Cluster-02=00061663-4a18-7c31-185b-ac1f6b6029e2",
  "cluster_name": "NTNX-Cluster-02",
  "cluster_uuid": "00061663-4a18-7c31-185b-ac1f6b6029e2",
  "target_subnet": "Production-Network=12345678-1234-5678-9abc-123456789012",
  "subnet_name": "Production-Network",
  "subnet_uuid": "12345678-1234-5678-9abc-123456789012",
  "subnet_vlan_id": "100",
  "target_image": "Windows-Server-2022=abcd1234-5678-90ef-ghij-klmn12345678",
  "image_name": "Windows-Server-2022",
  "image_uuid": "abcd1234-5678-90ef-ghij-klmn12345678",
  "image_type": "DISK_IMAGE",
  "image_size_bytes": 16642998272,
  "sysprep_filename": "sysprep_windows_server.xml",
  "sysprep_filepath": "C:\\Users\\hardev.sanghera\\Documents\\v3\\deploy_win_vm\\sysprep_windows_server.xml",
  "sysprep_size_bytes": 1847
}
```

### API Endpoints Used
- **GET https://pc_ip:9440/api/nutanix/v3/clusters/list**
  - Payload: `{"kind": "cluster"}`
- **GET https://pc_ip:9440/api/nutanix/v3/subnets/list**
  - Payload: `{"kind": "subnet"}`
- **GET https://pc_ip:9440/api/nutanix/v3/images/list**
  - Payload: `{"kind": "image"}`
- Authentication: HTTP Basic Auth

### Error Handling
The script handles common scenarios:
- Invalid credentials (401 authentication errors)
- Network connectivity issues
- API response errors
- Invalid user input during resource selection
- Missing or empty resource lists

### Security Notes
- Passwords are entered securely using `getpass` (hidden input)
- SSL certificate verification is disabled for self-signed certificates
- Credentials are not stored in any files

## Next Steps
After running this script successfully, you'll have:
1. Selected target cluster, subnet, and image with their UUIDs
2. A complete deployment configuration file
3. The resource variables in the required format: `"resource_name=UUID"`

This provides all the foundation resources needed for deploying Windows VMs to your selected Nutanix AHV cluster.