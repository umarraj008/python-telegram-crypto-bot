# config_loader.py

import argparse
import json

def parse_args():
    """
    Parses command-line arguments to determine which configuration file to use.

    Returns:
        argparse.Namespace: Parsed arguments with 'test' and 'printer' attributes.
                           If '-test' is specified, the 'test' attribute will be True,
                           indicating that the test configuration file should be used.
                           If '-printer' is specified, the 'printer' attribute will be True.
    """
    parser = argparse.ArgumentParser(description="Load configuration file.")
    parser.add_argument('-test', action='store_true', help="Use test configuration file")
    parser.add_argument('-printer', action='store_true', help="Enable printing mode")
    return parser.parse_args()

def load_config(args):
    """
    Loads configuration settings from a JSON file.

    Chooses between a test configuration file ('testConfig.json') and a production
    configuration file ('config.json') based on the parsed command-line arguments.

    Also checks the '-printer' argument to enable/disable printing in the config.

    Returns:
        dict: -> Configuration settings
    """
    configFile = "tests/testConfig.json" if args.test else "config.json"
    
    # Open the chosen config file (either production or test)
    with open(configFile, 'r') as f:
        config = json.load(f)

    # Add the parsed command-line arguments to the config
    config["test"] = args.test
    config["printer"] = args.printer

    return config