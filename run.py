if __name__ == '__main__':

    import os
    import argparse
    import logging

    logging.basicConfig(format='%(module)s [%(asctime)s]: %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--production', dest='production', default=False,
                        action='store_true', help='Run telegram bot in a production mode')

    cmd_args = vars(parser.parse_args())

    if cmd_args.get('production'):
        os.environ["DEBUG"] = "False"

    from chatbot.app import start_bot

    start_bot()
