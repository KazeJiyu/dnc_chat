# System imports
import argparse
import configparser
import logging
import sys
import os
from typing import Dict

# let python know other modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.dirname(__file__))

# Local imports
from server.dnc.protocol import DncProtocol
from server.tcp import TcpServer
from server.utils.errors import print_err

def setup_logger(set_verbose, log_file):
    """
    Setups the logger so that it logs everything within a log file,
    and eventually prints messages to the console.
    
    Args:
    -----
        set_verbose (bool): `True` if logs should be printed in the console
        log_file (str): the path toward the file in which write logs 
    """
    class OneOf():
        
        def __init__(self, *handled_levels):
            self.__handled_levels = handled_levels
            
        def filter(self, log_record):
            return log_record.levelno in self.__handled_levels
        
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    file_formatter = logging.Formatter('[%(asctime)s] - %(levelname)s : %(message)s')
    stream_formatter = logging.Formatter('[%(asctime)s] %(message)s')
    
    if set_verbose:
        # Prints DEBUG & INFO to stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.addFilter(OneOf(logging.INFO))
        stdout_handler.setFormatter(stream_formatter)
        logger.addHandler(stdout_handler)
        
        # Prints WARNING & ERROR & CRITICAL to stderr
        stderr_handler = logging.StreamHandler()
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.setFormatter(stream_formatter)
        logger.addHandler(stderr_handler)
    
    # Prints everything into log file
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
def parse_arguments() -> Dict[str,object]:
    """
    Parses the command line, setups the logger according to arguments, and then 
    returns the UDP port that can be used by the server.
    
    Return:
    -------
    @rtype: C{Dict[str,object]}
    @return: a dictionary associating the name of the arguments to their value
    
    Note:
    -----
    @note: depending on the command line's arguments, this method may ends the program.
           For example, if the user call python <file_name.py> -h, this method will
           displays the help and then exits.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="Runs a DNC server\n\n"
                                                 "Fore a detailed description of the DNC protocol, please take a look at the corresponding RFC.\n"
                                                 "Use the --rfc option to read it.")
   
    parser.add_argument('port', default=8123, type=int, nargs='?', 
                        help="The number of the port to be used by the server.")
    parser.add_argument('log_file', default='dnc_server.log', nargs='?',
                        help="The name of the file in which logs the requests.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Adding this argument will let the server prints its log on the screen.")
    parser.add_argument('--rfc', action='store_true',
                        help="Prints the RFC concerning the DNC protocol then exit.")
    parser.add_argument('-c', '--conf', nargs='?',
                        help="Specify a .ini file that contains server's configuration.\n"
                             "See below for accepted sections and variables (replace <..> by real values):\n"
                             "[network]\n"
                             "port = <port_number>\n\n"
                             "[log]\n"
                             "verbose = <True/False>\n"
                             "log_file = <file_name>")

    args = vars(parser.parse_args())    
    
    if args['conf']:
        tailor_args_to_config_file(args['conf'], args)

    setup_logger(args['verbose'], args['log_file'])
    
    return args

def tailor_args_to_config_file(config_file, args):
    if not os.path.exists(config_file):
        raise ValueError(f" The config file does not exist: {config_file}")
        
    parser = configparser.ConfigParser()
    parser.read(config_file)
    
    if "network" in parser.sections():
        if "port" in parser["network"]:
            args["port"] = int(parser["network"]["port"])
            
    if "log" in parser.sections():
        if "verbose" in parser["log"]:
            args["verbose"] = True if parser["log"]["verbose"].lower() in ['yes', 'true'] else False
        if "log_file" in parser["log"]:
            args["log_file"] = parser["log"]["log_file"]
        
def print_rfc_content():
    try:
        with open("../rfc.txt") as rfc:
            for line in rfc:
                print(line, end='')
                
    except:
        raise ValueError(" Sorry, unable to found RFC content. Please check:\n" +
                         "      Please check github.com/KazeJiyu/dnc_chat/blob/master/rfc.txt")

if __name__ == '__main__':
    try:
        args = parse_arguments()
    
        if args['rfc']:
            print_rfc_content()
            exit(0)
            
    except Exception as e:
        print_err(e)
        
    else:
        port = args['port']
        
        logging.info("Starting server")

        TcpServer(DncProtocol(), port).run_forever()
    
        logging.info("Server is closed")
