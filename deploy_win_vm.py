#!/usr/bin/env python3
"""
Nutanix Windows VM Deployment Script - Phase 1: Resource Selection
This script fetches available clusters, subnets, and images from Nutanix Prism Central 
using v3.1 REST API and allows user to select target resources for VM deployment.
"""

import requests
import urllib3
import getpass
import argparse
import json
import sys
import os
import glob
import base64
from base64 import b64encode
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Disable SSL certificate warnings globally for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class ClusterInfo:
    """Data class to hold cluster information"""
    name: str
    uuid: str


@dataclass
class SubnetInfo:
    """Data class to hold subnet information"""
    name: str
    uuid: str
    vlan_id: str
    cluster_name: str


@dataclass
class ImageInfo:
    """Data class to hold image information"""
    name: str
    uuid: str
    size_bytes: int
    image_type: str


@dataclass
class SysprepInfo:
    """Data class to hold sysprep file information"""
    filename: str
    filepath: str
    size_bytes: int
    

class NutanixAPIClient:
    """
    Nutanix v3.1 REST API client for cluster, subnet, and image operations
    Based on patterns from nutanixdev/code-samples repository
    """
    
    def __init__(self, pc_ip: str, username: str, password: str, port: int = 9440):
        self.pc_ip = pc_ip
        self.username = username
        self.password = password
        self.port = port
        self.base_url = f"https://{self.pc_ip}:{self.port}/api/nutanix/v3"
        
        # Setup HTTP Basic Auth header
        encoded_credentials = b64encode(
            bytes(f"{self.username}:{self.password}", encoding="ascii")
        ).decode("ascii")
        self.auth_header = f"Basic {encoded_credentials}"
        
        # Setup request headers
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.auth_header,
            "cache-control": "no-cache"
        }
        
        # Disable SSL warnings for self-signed certificates
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def get_clusters(self) -> List[ClusterInfo]:
        """
        Fetch all clusters from Prism Central
        Returns list of ClusterInfo objects
        """
        url = f"{self.base_url}/clusters/list"
        payload = {"kind": "cluster"}
        
        try:
            print(f"Connecting to Prism Central at {self.pc_ip}...")
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            
            if response.status_code == 401:
                print("Authentication failed. Please check your credentials.")
                sys.exit(1)
            elif response.status_code != 200:
                print(f"API request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                sys.exit(1)
            
            data = response.json()
            clusters = []
            
            print("Successfully connected to Prism Central!")
            print(f"Found {data['metadata']['total_matches']} clusters")
            
            for cluster in data['entities']:
                # Skip unnamed clusters (typically Prism Central itself)
                if cluster['status']['name'] != "Unnamed":
                    clusters.append(ClusterInfo(
                        name=cluster['status']['name'],
                        uuid=cluster['metadata']['uuid']
                    ))
            
            return clusters
            
        except requests.exceptions.ConnectionError:
            print(f"Failed to connect to {self.pc_ip}. Please check the IP address and network connectivity.")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print("Connection timed out. Please check your network connection.")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def get_subnets(self) -> List[SubnetInfo]:
        """
        Fetch all subnets from Prism Central
        Returns list of SubnetInfo objects
        """
        url = f"{self.base_url}/subnets/list"
        payload = {"kind": "subnet"}
        
        try:
            print(f"Fetching subnets from Prism Central...")
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch subnets. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return []
            
            data = response.json()
            subnets = []
            
            print(f"Found {data['metadata']['total_matches']} subnets")
            
            for subnet in data['entities']:
                try:
                    # Extract subnet information
                    subnet_name = subnet['spec']['name']
                    subnet_uuid = subnet['metadata']['uuid']
                    
                    # Get VLAN ID if available
                    vlan_id = "N/A"
                    if 'vlan_id' in subnet['spec']:
                        vlan_id = str(subnet['spec']['vlan_id'])
                    
                    # Get cluster reference if available
                    cluster_name = "N/A"
                    if 'cluster_reference' in subnet['spec']:
                        cluster_name = subnet['spec']['cluster_reference'].get('name', 'N/A')
                    
                    subnets.append(SubnetInfo(
                        name=subnet_name,
                        uuid=subnet_uuid,
                        vlan_id=vlan_id,
                        cluster_name=cluster_name
                    ))
                except KeyError as e:
                    print(f"Skipping subnet due to missing field: {e}")
                    continue
            
            return subnets
            
        except Exception as e:
            print(f"Error fetching subnets: {e}")
            return []

    def get_images(self) -> List[ImageInfo]:
        """
        Fetch all images from Prism Central
        Returns list of ImageInfo objects
        """
        url = f"{self.base_url}/images/list"
        payload = {"kind": "image"}
        
        try:
            print(f"Fetching images from Prism Central...")
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch images. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return []
            
            data = response.json()
            images = []
            
            print(f"Found {data['metadata']['total_matches']} images")
            
            for image in data['entities']:
                try:
                    # Extract image information
                    image_name = image['spec']['name']
                    image_uuid = image['metadata']['uuid']
                    
                    # Get size in bytes
                    size_bytes = image['status'].get('resources', {}).get('size_bytes', 0)
                    
                    # Get image type
                    image_type = image['status'].get('resources', {}).get('image_type', 'UNKNOWN')
                    
                    images.append(ImageInfo(
                        name=image_name,
                        uuid=image_uuid,
                        size_bytes=size_bytes,
                        image_type=image_type
                    ))
                except KeyError as e:
                    print(f"Skipping image due to missing field: {e}")
                    continue
            
            return images
            
        except Exception as e:
            print(f"Error fetching images: {e}")
            return []


def get_sysprep_files() -> List[SysprepInfo]:
    """
    Search current directory for sysprep XML files
    Returns list of SysprepInfo objects
    """
    sysprep_files = []
    
    # Search for files that start with "sysprep" and end with ".xml"
    pattern = "sysprep*.xml"
    current_dir = os.getcwd()
    
    print(f"Searching for sysprep XML files in: {current_dir}")
    
    # Use glob to find matching files
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        print("No sysprep XML files found in current directory.")
        return []
    
    print(f"Found {len(matching_files)} sysprep XML file(s)")
    
    for filename in matching_files:
        try:
            filepath = os.path.abspath(filename)
            size_bytes = os.path.getsize(filepath)
            
            sysprep_files.append(SysprepInfo(
                filename=filename,
                filepath=filepath,
                size_bytes=size_bytes
            ))
        except OSError as e:
            print(f"Error accessing file {filename}: {e}")
            continue
    
    return sysprep_files


def display_clusters(clusters: List[ClusterInfo]) -> None:
    """Display numbered list of clusters"""
    print("\n" + "="*60)
    print("AVAILABLE CLUSTERS")
    print("="*60)
    
    for i, cluster in enumerate(clusters, 1):
        print(f"{i:2d}. {cluster.name}")
        print(f"     UUID: {cluster.uuid}")
        print()


def display_subnets(subnets: List[SubnetInfo]) -> None:
    """Display numbered list of subnets"""
    print("\n" + "="*60)
    print("AVAILABLE SUBNETS")
    print("="*60)
    
    for i, subnet in enumerate(subnets, 1):
        print(f"{i:2d}. {subnet.name}")
        print(f"     UUID: {subnet.uuid}")
        print(f"     VLAN ID: {subnet.vlan_id}")
        print(f"     Cluster: {subnet.cluster_name}")
        print()


def display_images(images: List[ImageInfo]) -> None:
    """Display numbered list of images"""
    print("\n" + "="*60)
    print("AVAILABLE IMAGES")
    print("="*60)
    
    for i, image in enumerate(images, 1):
        size_gb = round(image.size_bytes / (1024**3), 2) if image.size_bytes > 0 else 0
        print(f"{i:2d}. {image.name}")
        print(f"     UUID: {image.uuid}")
        print(f"     Type: {image.image_type}")
        print(f"     Size: {size_gb} GB")
        print()


def display_sysprep_files(sysprep_files: List[SysprepInfo]) -> None:
    """Display numbered list of sysprep XML files"""
    print("\n" + "="*60)
    print("AVAILABLE SYSPREP XML FILES")
    print("="*60)
    
    for i, sysprep in enumerate(sysprep_files, 1):
        size_kb = round(sysprep.size_bytes / 1024, 2) if sysprep.size_bytes > 0 else 0
        print(f"{i:2d}. {sysprep.filename}")
        print(f"     Path: {sysprep.filepath}")
        print(f"     Size: {size_kb} KB")
        print()


def select_cluster(clusters: List[ClusterInfo]) -> ClusterInfo:
    """
    Allow user to select a cluster from the list
    Returns selected ClusterInfo object
    """
    while True:
        try:
            choice = input(f"Please select a cluster (1-{len(clusters)}): ").strip()
            cluster_num = int(choice)
            
            if 1 <= cluster_num <= len(clusters):
                selected_cluster = clusters[cluster_num - 1]
                print(f"\nSelected cluster: {selected_cluster.name}")
                print(f"UUID: {selected_cluster.uuid}")
                return selected_cluster
            else:
                print(f"Please enter a number between 1 and {len(clusters)}")
                
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)


def select_subnet(subnets: List[SubnetInfo]) -> SubnetInfo:
    """
    Allow user to select a subnet from the list
    Returns selected SubnetInfo object
    """
    while True:
        try:
            choice = input(f"Please select a subnet (1-{len(subnets)}): ").strip()
            subnet_num = int(choice)
            
            if 1 <= subnet_num <= len(subnets):
                selected_subnet = subnets[subnet_num - 1]
                print(f"\nSelected subnet: {selected_subnet.name}")
                print(f"UUID: {selected_subnet.uuid}")
                print(f"VLAN ID: {selected_subnet.vlan_id}")
                return selected_subnet
            else:
                print(f"Please enter a number between 1 and {len(subnets)}")
                
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)


def select_image(images: List[ImageInfo]) -> ImageInfo:
    """
    Allow user to select an image from the list
    Returns selected ImageInfo object
    """
    while True:
        try:
            choice = input(f"Please select an image (1-{len(images)}): ").strip()
            image_num = int(choice)
            
            if 1 <= image_num <= len(images):
                selected_image = images[image_num - 1]
                size_gb = round(selected_image.size_bytes / (1024**3), 2) if selected_image.size_bytes > 0 else 0
                print(f"\nSelected image: {selected_image.name}")
                print(f"UUID: {selected_image.uuid}")
                print(f"Type: {selected_image.image_type}")
                print(f"Size: {size_gb} GB")
                return selected_image
            else:
                print(f"Please enter a number between 1 and {len(images)}")
                
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)


def select_sysprep_file(sysprep_files: List[SysprepInfo]) -> SysprepInfo:
    """
    Allow user to select a sysprep file from the list
    Returns selected SysprepInfo object
    """
    while True:
        try:
            choice = input(f"Please select a sysprep XML file (1-{len(sysprep_files)}): ").strip()
            sysprep_num = int(choice)
            
            if 1 <= sysprep_num <= len(sysprep_files):
                selected_sysprep = sysprep_files[sysprep_num - 1]
                size_kb = round(selected_sysprep.size_bytes / 1024, 2) if selected_sysprep.size_bytes > 0 else 0
                print(f"\nSelected sysprep file: {selected_sysprep.filename}")
                print(f"Path: {selected_sysprep.filepath}")
                print(f"Size: {size_kb} KB")
                return selected_sysprep
            else:
                print(f"Please enter a number between 1 and {len(sysprep_files)}")
                
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)


def save_cluster_config(cluster: ClusterInfo, subnet: SubnetInfo, image: ImageInfo, sysprep: SysprepInfo, pc_ip: str, username: str) -> None:
    """Save selected cluster, subnet, image, and sysprep configuration to file"""
    config = {
        "pc_ip": pc_ip,
        "username": username,
        "target_cluster": f"{cluster.name}={cluster.uuid}",
        "cluster_name": cluster.name,
        "cluster_uuid": cluster.uuid,
        "target_subnet": f"{subnet.name}={subnet.uuid}",
        "subnet_name": subnet.name,
        "subnet_uuid": subnet.uuid,
        "subnet_vlan_id": subnet.vlan_id,
        "target_image": f"{image.name}={image.uuid}",
        "image_name": image.name,
        "image_uuid": image.uuid,
        "image_type": image.image_type,
        "image_size_bytes": image.size_bytes,
        "sysprep_filename": sysprep.filename,
        "sysprep_filepath": sysprep.filepath,
        "sysprep_size_bytes": sysprep.size_bytes
    }
    
    config_file = "deployment_config.json"
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\nDeployment configuration saved to {config_file}")
        print("This file contains all settings needed for VM deployment.")
    except Exception as e:
        print(f"Failed to save configuration: {e}")


def deploy_vm_from_config():
    """
    Deploy VM using the saved deployment configuration and create_vm_SKEL.json template
    """
    # Disable SSL warnings for self-signed certificates
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("\n" + "="*60)
    print("DEPLOYING WINDOWS VM")
    print("="*60)
    
    # Load deployment configuration
    try:
        with open("deployment_config.json", 'r') as f:
            config = json.load(f)
        print("✅ Loaded deployment configuration")
    except FileNotFoundError:
        print("❌ deployment_config.json not found. Please run resource selection first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in deployment_config.json")
        sys.exit(1)
    
    # Load VM creation template
    try:
        with open("create_vm_SKEL.json", 'r') as f:
            vm_template = f.read()
        print("✅ Loaded VM creation template")
    except FileNotFoundError:
        print("❌ create_vm_SKEL.json not found. Please ensure the template file exists.")
        sys.exit(1)
    
    # Prompt for VM name
    while True:
        vm_name = input("\n💻 Enter VM name: ").strip()
        if vm_name:
            # Validate VM name (basic checks)
            if len(vm_name) > 15:
                print("❌ VM name too long (max 15 characters for Windows computer name)")
                continue
            if not all(c.isalnum() or c in '-_' for c in vm_name):
                print("❌ VM name can only contain letters, numbers, hyphens, and underscores")
                continue
            break
        else:
            print("❌ VM name cannot be empty")
    
    # Prompt for Administrator password
    while True:
        vm_password = getpass.getpass("\n🔐 Enter Administrator password: ").strip()
        if vm_password:
            if len(vm_password) < 4:
                print("❌ Password too short (minimum 4 characters)")
                continue
            # Confirm password
            confirm_password = getpass.getpass("🔐 Confirm Administrator password: ").strip()
            if vm_password == confirm_password:
                break
            else:
                print("❌ Passwords do not match. Please try again.")
        else:
            print("❌ Password cannot be empty")
    
    # Read and modify sysprep XML file
    try:
        with open(config['sysprep_filepath'], 'r', encoding='utf-8') as f:
            sysprep_content = f.read()
        
        # Replace ComputerName in sysprep XML with the entered VM name
        import re
        sysprep_content = re.sub(
            r'<ComputerName>.*?</ComputerName>',
            f'<ComputerName>{vm_name}</ComputerName>',
            sysprep_content
        )
        
        # Replace Administrator password in both locations
        sysprep_content = re.sub(
            r'<AdministratorPassword>\s*<Value>.*?</Value>',
            f'<AdministratorPassword>\n              <Value>{vm_password}</Value>',
            sysprep_content,
            flags=re.DOTALL
        )
        
        sysprep_content = re.sub(
            r'<AutoLogon>\s*<Password>\s*<Value>.*?</Value>',
            f'<AutoLogon>\n           <Password>\n              <Value>{vm_password}</Value>',
            sysprep_content,
            flags=re.DOTALL
        )
        
        # Base64 encode the modified sysprep content
        sysprep_encoded = base64.b64encode(sysprep_content.encode('utf-8')).decode('utf-8')
        print(f"✅ Read and encoded sysprep file: {config['sysprep_filename']}")
        print(f"✅ Updated ComputerName in sysprep to: {vm_name}")
        print(f"✅ Updated Administrator password in sysprep")
    except FileNotFoundError:
        print(f"❌ Sysprep file not found: {config['sysprep_filepath']}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading sysprep file: {e}")
        sys.exit(1)
    
    # Replace placeholders in the VM template
    print("\n🔧 Building VM payload...")
    vm_payload = vm_template.replace("XXSUBNETUUIDXX", config['subnet_uuid'])
    vm_payload = vm_payload.replace("XXIMAGEUUIDXX", config['image_uuid'])
    vm_payload = vm_payload.replace("XXCLUSTERUUIDXX", config['cluster_uuid'])
    vm_payload = vm_payload.replace("XXVMNAMEXX", vm_name)
    vm_payload = vm_payload.replace("XXUSERDATAXX", sysprep_encoded)
    
    # Convert string back to JSON
    try:
        vm_json = json.loads(vm_payload)
        print("✅ VM payload built successfully")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON after placeholder replacement")
        sys.exit(1)
    
    # Pretty print the JSON payload
    print(f"\n📄 VM Creation Payload (JSON):")
    print("=" * 60)
    print(json.dumps(vm_json, indent=2, sort_keys=False))
    print("=" * 60)
    
    # Display VM configuration
    print(f"\n📋 VM Configuration:")
    print(f"  Name: {vm_name}")
    print(f"  Cluster: {config['cluster_name']} ({config['cluster_uuid']})")
    print(f"  Subnet: {config['subnet_name']} ({config['subnet_uuid']})")
    print(f"  Image: {config['image_name']} ({config['image_uuid']})")
    print(f"  Sysprep: {config['sysprep_filename']}")
    
    # Get user confirmation
    confirm = input(f"\n🚀 Deploy VM '{vm_name}'? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Deployment cancelled.")
        return
    
    # Get password for API authentication
    password = getpass.getpass(f"Enter password for {config['username']}: ")
    if not password:
        print("Password cannot be empty")
        return
    
    # Setup authentication
    encoded_credentials = b64encode(
        bytes(f"{config['username']}:{password}", encoding="ascii")
    ).decode("ascii")
    auth_header = f"Basic {encoded_credentials}"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": auth_header,
        "cache-control": "no-cache"
    }
    
    # Build API URL - Note: using /vms (plural) not /vm
    api_url = f"https://{config['pc_ip']}:9440/api/nutanix/v3/vms"
    
    # Make the POST API call
    print(f"\n🌐 Making API call to: {api_url}")
    try:
        response = requests.post(
            api_url,
            json=vm_json,
            headers=headers,
            verify=False,
            timeout=60
        )
        
        if response.status_code == 202:
            result = response.json()
            vm_uuid = result.get('metadata', {}).get('uuid')
            task_uuid = result.get('status', {}).get('execution_context', {}).get('task_uuid')
            
            print(f"\n✅ VM creation initiated successfully!")
            print(f"VM UUID: {vm_uuid}")
            if task_uuid:
                print(f"Task UUID: {task_uuid}")
            print(f"Status: {result.get('status', {}).get('state', 'UNKNOWN')}")
            print("\n📊 Check Prism Central for VM creation progress")
            
        else:
            print(f"\n❌ VM creation failed!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Failed to connect to {config['pc_ip']}. Please check network connectivity.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Please try again.")
    except Exception as e:
        print(f"❌ Error making API call: {e}")


def main():
    """Main function"""
    # Setup command line arguments
    parser = argparse.ArgumentParser(
        description="Nutanix Windows VM Deployment Tool"
    )
    parser.add_argument("pc_ip", nargs='?', help="Prism Central IP address or FQDN")
    parser.add_argument("username", nargs='?', help="Prism Central username")
    parser.add_argument("--deploy", action="store_true", 
                       help="Deploy VM using saved configuration (skips resource selection)")
    args = parser.parse_args()
    
    # Check if deploy mode
    if args.deploy:
        # Deploy mode - use saved configuration
        deploy_vm_from_config()
        return
    
    # Resource selection mode - require pc_ip and username
    if not args.pc_ip or not args.username:
        print("Error: pc_ip and username are required for resource selection mode")
        print("Usage:")
        print("  Resource selection: python deploy_win_vm.py <PC_IP> <USERNAME>")
        print("  VM deployment:      python deploy_win_vm.py --deploy")
        sys.exit(1)
    
    # Get password securely
    password = getpass.getpass(f"Enter password for {args.username}: ")
    
    if not password:
        print("Password cannot be empty")
        sys.exit(1)
    
    # Create API client
    client = NutanixAPIClient(args.pc_ip, args.username, password)
    
    # Fetch and select cluster
    clusters = client.get_clusters()
    if not clusters:
        print("No named clusters found. Make sure you have clusters registered with Prism Central.")
        sys.exit(1)
    
    display_clusters(clusters)
    selected_cluster = select_cluster(clusters)
    
    # Fetch and select subnet
    subnets = client.get_subnets()
    if not subnets:
        print("No subnets found. Make sure you have subnets configured in Prism Central.")
        sys.exit(1)
    
    display_subnets(subnets)
    selected_subnet = select_subnet(subnets)
    
    # Fetch and select image
    images = client.get_images()
    if not images:
        print("No images found. Make sure you have images uploaded to Prism Central.")
        sys.exit(1)
    
    display_images(images)
    selected_image = select_image(images)
    
    # Search and select sysprep file
    sysprep_files = get_sysprep_files()
    if not sysprep_files:
        print("No sysprep XML files found. Make sure you have sysprep*.xml files in the current directory.")
        sys.exit(1)
    
    display_sysprep_files(sysprep_files)
    selected_sysprep = select_sysprep_file(sysprep_files)
    
    # Save configuration for next steps
    save_cluster_config(selected_cluster, selected_subnet, selected_image, selected_sysprep, args.pc_ip, args.username)
    
    # Display configuration summary
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY")
    print("="*60)
    print(f"target_cluster = \"{selected_cluster.name}={selected_cluster.uuid}\"")
    print(f"target_subnet  = \"{selected_subnet.name}={selected_subnet.uuid}\"")
    print(f"target_image   = \"{selected_image.name}={selected_image.uuid}\"")
    print(f"sysprep_file   = \"{selected_sysprep.filename}\"")
    print("\n" + "="*60)
    print("DETAILED CONFIGURATION")
    print("="*60)
    print(f"Cluster: {selected_cluster.name} ({selected_cluster.uuid})")
    print(f"Subnet:  {selected_subnet.name} ({selected_subnet.uuid}) - VLAN {selected_subnet.vlan_id}")
    print(f"Image:   {selected_image.name} ({selected_image.uuid})")
    size_gb = round(selected_image.size_bytes / (1024**3), 2) if selected_image.size_bytes > 0 else 0
    print(f"         Type: {selected_image.image_type}, Size: {size_gb} GB")
    sysprep_size_kb = round(selected_sysprep.size_bytes / 1024, 2) if selected_sysprep.size_bytes > 0 else 0
    print(f"Sysprep: {selected_sysprep.filename} ({sysprep_size_kb} KB)")
    print(f"         Path: {selected_sysprep.filepath}")
    print("\nThis configuration is ready for Windows VM deployment!")


if __name__ == "__main__":
    main()