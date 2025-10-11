# Nutanix Windows VM Deployment Tool

This tool provides a complete solution for deploying Windows VMs to Nutanix AHV clusters via Prism Central using the Nutanix v3.1 REST API. The script operates in two modes:

1. **Resource Selection Mode** - Interactive selection of deployment resources
2. **VM Deployment Mode** - Automated VM creation using saved configuration

## Overview

The `deploy_win_vm.py` script supports the complete VM deployment workflow:

### Phase 1: Resource Selection (Default Mode)
- Connects to Nutanix Prism Central via REST API
- Displays all available resources with interactive selection:
  - **Clusters** - Target AHV clusters for VM deployment
  - **Subnets** - Available network subnets for VM connectivity  
  - **Images** - Available disk images for VM creation
  - **Sysprep Files** - Local sysprep XML files for Windows customization
- Saves configuration to `deployment_config.json` for next phase

### Phase 2: VM Deployment (--deploy flag)
- Loads saved resource configuration
- Prompts for VM name and Administrator password
- Reads and customizes sysprep XML with VM-specific details
- Creates VM payload from `create_vm_SKEL.json` template
- Deploys VM via Prism Central API
- Returns VM UUID and deployment status

### Prerequisites
- Python 3.7+ with virtual environment activated
- Network connectivity to Nutanix Prism Central
- Valid Prism Central credentials

### Required Python Packages
- requests>=2.25.1
- urllib3>=1.26.0

### Usage

## Resource Selection Mode

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

## VM Deployment Mode

1. **Deploy VM using saved configuration**:
   ```powershell
   python deploy_win_vm.py --deploy
   ```

2. **Enter VM details** when prompted:
   - VM name (max 15 characters, alphanumeric plus hyphens/underscores)
   - Administrator password (minimum 4 characters)
   - Confirm password

3. **Confirm deployment** - Review configuration and confirm VM creation

4. **Enter Prism Central password** for API authentication

The script will:
- Customize the sysprep XML with your VM name and password
- Create the VM payload from the template
- Deploy the VM via REST API
- Display the VM UUID and task UUID for monitoring

## VM Specifications

When deployed, VMs are created with the following default specifications (defined in `create_vm_SKEL.json`):

- **Memory**: 8,096 MB (8 GB)
- **CPUs**: 1 socket × 4 cores (4 vCPUs total)
- **Power State**: ON (VM starts automatically)
- **Disk**: Uses selected image as boot disk on SCSI adapter
- **Network**: Connected to selected subnet
- **Customization**: Sysprep applied with custom computer name and Administrator password

## Required Files

The deployment process requires these files in the current directory:

- **`create_vm_SKEL.json`** - VM creation template with placeholders
- **`sysprep*.xml`** - Windows sysprep customization files
- **`deployment_config.json`** - Generated during resource selection phase

### VM Template Placeholders

The `create_vm_SKEL.json` template uses these placeholders that are automatically replaced:

- `XXVMNAMEXX` - Replaced with entered VM name
- `XXSUBNETUUIDXX` - Replaced with selected subnet UUID
- `XXIMAGEUUIDXX` - Replaced with selected image UUID
- `XXCLUSTERUUIDXX` - Replaced with selected cluster UUID
- `XXUSERDATAXX` - Replaced with Base64-encoded sysprep XML content

## Sample Output

### Resource Selection Phase
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

[... subnet and image selection ...]

Deployment configuration saved to deployment_config.json
This file contains all settings needed for VM deployment.

============================================================
CONFIGURATION SUMMARY
============================================================
target_cluster = "NTNX-Cluster-02=00061663-4a18-7c31-185b-ac1f6b6029e2"
target_subnet  = "Production-Network=12345678-1234-5678-9abc-123456789012"
target_image   = "Windows-Server-2022=abcd1234-5678-90ef-ghij-klmn12345678"
sysprep_file   = "sysprep_windows_server.xml"
```

### VM Deployment Phase
```
============================================================
DEPLOYING WINDOWS VM
============================================================
✅ Loaded deployment configuration
✅ Loaded VM creation template

💻 Enter VM name: WIN-WEB-01

🔐 Enter Administrator password: [hidden]
🔐 Confirm Administrator password: [hidden]

✅ Read and encoded sysprep file: sysprep-win2019-AAA.xml
✅ Updated ComputerName in sysprep to: WIN-WEB-01
✅ Updated Administrator password in sysprep

🔧 Building VM payload...
✅ VM payload built successfully

📋 VM Configuration:
  Name: WIN-WEB-01
  Cluster: NTNX-Cluster-02 (00061663-4a18-7c31-185b-ac1f6b6029e2)
  Subnet: Production-Network (12345678-1234-5678-9abc-123456789012)
  Image: Windows-Server-2022 (abcd1234-5678-90ef-ghij-klmn12345678)
  Sysprep: sysprep-win2019-AAA.xml

🚀 Deploy VM 'WIN-WEB-01'? (y/N): y

🌐 Making API call to: https://10.1.1.100:9440/api/nutanix/v3/vms

✅ VM creation initiated successfully!
VM UUID: def12345-6789-0abc-def1-234567890abc
Task UUID: ghi67890-abcd-ef12-3456-7890abcdef12
Status: PENDING

📊 Check Prism Central for VM creation progress
```

## Generated Files

### deployment_config.json
Contains the complete selected resource configuration for VM deployment. Generated during resource selection phase.

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

## Sysprep File Requirements

Sysprep XML files must:
- Be placed in the current directory
- Have filenames starting with "sysprep" and ending with ".xml"
- Contain `<ComputerName>` and `<AdministratorPassword>` elements
- Examples: `sysprep-win2019-AAA.xml`, `sysprep-win2022-prod.xml`, `sysprep_windows_server.xml`

The script automatically updates these elements in the sysprep file:
- `<ComputerName>` - Set to the entered VM name
- `<AdministratorPassword><Value>` - Set to the entered password
- `<AutoLogon><Password><Value>` - Set to the entered password

## API Endpoints Used

### Resource Selection Phase
- **GET https://pc_ip:9440/api/nutanix/v3/clusters/list**
  - Payload: `{"kind": "cluster"}`
  - Purpose: Retrieve all available AHV clusters
- **GET https://pc_ip:9440/api/nutanix/v3/subnets/list**
  - Payload: `{"kind": "subnet"}`
  - Purpose: Retrieve all available network subnets
- **GET https://pc_ip:9440/api/nutanix/v3/images/list**
  - Payload: `{"kind": "image"}`
  - Purpose: Retrieve all available disk images

### VM Deployment Phase
- **POST https://pc_ip:9440/api/nutanix/v3/vms**
  - Payload: Complete VM specification in JSON format
  - Purpose: Create new VM with specified configuration
  - Returns: VM UUID and task UUID for monitoring

### Authentication
- **Method**: HTTP Basic Authentication
- **Header**: `Authorization: Basic <base64-encoded-credentials>`
- **SSL**: Certificate verification disabled for self-signed certificates

## Error Handling

The script handles common scenarios:

### Resource Selection Phase
- Invalid credentials (401 authentication errors)
- Network connectivity issues to Prism Central
- API response errors and timeouts
- Empty resource lists (no clusters, subnets, or images)
- Invalid user input during resource selection
- Missing or inaccessible sysprep files

### VM Deployment Phase  
- Missing or invalid `deployment_config.json` file
- Missing `create_vm_SKEL.json` template
- Invalid VM name format (length and character validation)
- Password validation and confirmation
- Sysprep file read/write errors
- JSON parsing errors in templates
- API deployment failures with detailed error messages

## Security Notes

- **Password Security**: Passwords are entered securely using `getpass` (hidden input)
- **SSL Certificates**: SSL certificate verification is disabled for self-signed certificates
- **Credential Storage**: Prism Central credentials are not stored in any files
- **Sysprep Security**: Administrator passwords are embedded in sysprep and Base64-encoded
- **API Security**: Uses HTTP Basic Authentication over HTTPS

## Workflow Summary

### Complete Deployment Process
1. **Run resource selection**: `python deploy_win_vm.py <PC_IP> <USERNAME>`
   - Select target cluster, subnet, image, and sysprep file
   - Configuration saved to `deployment_config.json`

2. **Run VM deployment**: `python deploy_win_vm.py --deploy`
   - Enter VM name and Administrator password
   - VM created with custom sysprep configuration
   - Returns VM UUID and task UUID for monitoring

3. **Monitor progress**: Check Prism Central for VM creation status
   - Use returned task UUID to track deployment progress
   - VM will be powered on automatically after creation

## Next Steps

After successful deployment:
- VM will be created in the selected cluster
- VM will be connected to the selected subnet  
- VM will boot from the selected image
- Sysprep will run on first boot with custom configuration
- Monitor VM creation progress in Prism Central
- Connect to VM after Windows setup completes

This provides a complete automated solution for deploying customized Windows VMs to Nutanix AHV clusters.