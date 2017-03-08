# System imports
import argparse
import sys
from typing import Tuple  
    
def parse_arguments() -> Tuple[str,int]:
    parser = argparse.ArgumentParser(description="Runs a DNC client")
    parser.add_argument('ip', default='127.0.0.1', nargs='?', 
                        help="The ip address of the DNC server to contact")
    parser.add_argument('port', default='8123', nargs='?', type=int,
                        help="The name of the file in which logs the requests")

    args = vars(parser.parse_args())
    return args['ip'], args['port']

if __name__ == '__main__':
    args = parse_arguments()
    
    # ... Runs DNC client
