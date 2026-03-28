from neko.utils.logger import get_logger

logger = get_logger()

def register(parser):
    """
    Plugin entry point.
    'parser' is the subparsers object from cli.py.
    """
    hello = parser.add_parser('hello', help='Example Neko Plugin: Hello World')
    hello.add_argument('--name', default='User', help='Name to greet')
    
    # Return the function to be executed
    return run

def run(args):
    """
    Execution logic for the plugin.
    """
    logger.success(f"Hello, {args.name}! Neko Plugin System is working correctly.")
    logger.info("This is an example of a dynamically loaded module.")
