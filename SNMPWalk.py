


"""
SNMP Walk Application
A simple Python application for performing SNMP walks on network devices.
"""

import argparse
import sys
# from pysnmp.hlapi import (nextCmd, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, SnmpEngine)
from pysnmp.hlapi.v3arch.asyncio import *
#from pysnmp.hlapi.v1arch.asyncio import *
from pysnmp.error import PySnmpError
import ipaddress


class SNMPWalker:
    def __init__(self, target, community='public', port=161, version='2c'):
        self.target = target
        self.community = community
        self.port = int(port)
        self.version = version
        
        # Validate IP address
        try:
            ipaddress.ip_address(target)
        except ValueError:
            # If not a valid IP, assume it's a hostname
            pass
    
    def walk(self, oid='1.3.6.1.2.1', max_results=None):
        """
        Perform SNMP walk operation
        
        Args:
            oid (str): Starting OID for the walk
            max_results (int): Maximum number of results to return
        
        Returns:
            list: List of tuples containing (oid, value, value_type)
        """
        results = []
        count = 0
        
        try:
            # Determine SNMP version
            if self.version.lower() == '1':
                snmp_version = 0
            elif self.version.lower() in ['2c', '2']:
                snmp_version = 1
            else:
                raise ValueError(f"Unsupported SNMP version: {self.version}")
            
            # Perform SNMP walk
            for (errorIndication, errorStatus, errorIndex, varBinds) in next_cmd(
                SnmpEngine(),
                CommunityData(self.community, mpModel=snmp_version),
                UdpTransportTarget((self.target, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
                ignoreNonIncreasingOid=True
            ):
                
                if errorIndication:
                    raise PySnmpError(f"SNMP error: {errorIndication}")
                    
                if errorStatus:
                    raise PySnmpError(f"SNMP error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
                
                for varBind in varBinds:
                    oid_str = str(varBind[0])
                    value = varBind[1]
                    value_type = type(value).__name__
                    
                    results.append((oid_str, str(value), value_type))
                    count += 1
                    
                    if max_results and count >= max_results:
                        return results
                        
        except Exception as e:
            raise PySnmpError(f"Failed to perform SNMP walk: {str(e)}")
        
        return results
    
    def get_single(self, oid):
        """
        Perform single SNMP GET operation
        
        Args:
            oid (str): OID to retrieve
            
        Returns:
            tuple: (oid, value, value_type)
        """
        try:
            # Determine SNMP version
            if self.version.lower() == '1':
                snmp_version = 0
            elif self.version.lower() in ['2c', '2']:
                snmp_version = 1
            else:
                raise ValueError(f"Unsupported SNMP version: {self.version}")
            
            for (errorIndication, errorStatus, errorIndex, varBinds) in get_cmd(
                SnmpEngine(),
                CommunityData(self.community, mpModel=snmp_version),
                UdpTransportTarget((self.target, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            ):
                
                if errorIndication:
                    raise PySnmpError(f"SNMP error: {errorIndication}")
                    
                if errorStatus:
                    raise PySnmpError(f"SNMP error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
                
                for varBind in varBinds:
                    oid_str = str(varBind[0])
                    value = varBind[1]
                    value_type = type(value).__name__
                    
                    return (oid_str, str(value), value_type)
                    
        except Exception as e:
            raise PySnmpError(f"Failed to perform SNMP get: {str(e)}")


def format_output(results, format_type='table'):
    """Format the SNMP results for display"""
    if not results:
        print("No results found.")
        return
    
    if format_type == 'table':
        print(f"{'OID':<50} {'Value':<30} {'Type':<15}")
        print("-" * 95)
        for oid, value, value_type in results:
            # Truncate long values for table format
            display_value = value[:27] + "..." if len(value) > 30 else value
            print(f"{oid:<50} {display_value:<30} {value_type:<15}")
    
    elif format_type == 'detailed':
        for i, (oid, value, value_type) in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  OID:   {oid}")
            print(f"  Value: {value}")
            print(f"  Type:  {value_type}")
    
    elif format_type == 'simple':
        for oid, value, _ in results:
            print(f"{oid} = {value}")


def main():
    parser = argparse.ArgumentParser(
        description='SNMP Walk Application - Perform SNMP walks and gets on network devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -t 192.168.1.1                          # Basic walk with default community
  %(prog)s -t 192.168.1.1 -c private               # Walk with custom community
  %(prog)s -t 192.168.1.1 -o 1.3.6.1.2.1.1         # Walk starting from system MIB
  %(prog)s -t 192.168.1.1 -g 1.3.6.1.2.1.1.1.0     # Single GET operation
  %(prog)s -t 192.168.1.1 -v 1                     # Use SNMP v1
  %(prog)s -t 192.168.1.1 -f detailed -m 50        # Detailed format, max 50 results

Common OIDs:
  1.3.6.1.2.1.1    - System information
  1.3.6.1.2.1.2    - Interfaces
  1.3.6.1.2.1.4    - IP information
  1.3.6.1.2.1.6    - TCP information
        """
    )
    
    parser.add_argument('-t', '--target', required=True,
                       help='Target IP address or hostname')
    
    parser.add_argument('-c', '--community', default='public',
                       help='SNMP community string (default: public)')
    
    parser.add_argument('-p', '--port', default=161, type=int,
                       help='SNMP port (default: 161)')
    
    parser.add_argument('-v', '--version', default='2c', choices=['1', '2c', '2'],
                       help='SNMP version (default: 2c)')
    
    parser.add_argument('-o', '--oid', default='1.3.6.1.2.1',
                       help='Starting OID for walk (default: 1.3.6.1.2.1)')
    
    parser.add_argument('-g', '--get',
                       help='Perform single GET instead of walk for specified OID')
    
    parser.add_argument('-m', '--max-results', type=int,
                       help='Maximum number of results to display')
    
    parser.add_argument('-f', '--format', default='table', 
                       choices=['table', 'detailed', 'simple'],
                       help='Output format (default: table)')
    
    parser.add_argument('--timeout', type=int, default=5,
                       help='SNMP timeout in seconds (default: 5)')
    
    args = parser.parse_args()
    
    try:
        # Create SNMP walker instance
        walker = SNMPWalker(
            target=args.target,
            community=args.community,
            port=args.port,
            version=args.version
        )
        
        print(f"SNMP Walk Application")
        print(f"Target: {args.target}:{args.port}")
        print(f"Community: {args.community}")
        print(f"Version: {args.version}")
        print("-" * 50)
        
        if args.get:
            # Perform single GET
            print(f"Performing SNMP GET for OID: {args.get}")
            result = walker.get_single(args.get)
            if result:
                format_output([result], args.format)
            else:
                print("No result returned.")
        else:
            # Perform SNMP walk
            print(f"Performing SNMP walk starting from OID: {args.oid}")
            if args.max_results:
                print(f"Maximum results: {args.max_results}")
            
            results = walker.walk(args.oid, args.max_results)
            
            print(f"\nFound {len(results)} results:")
            format_output(results, args.format)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
