#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika, sys, os, subprocess
from pathlib import Path
import argparse
from argparse import ArgumentParser

def parse_arguments(args):
    """
    Parse the arguments provided in the command line
    :param args: list of arguments
    :type args: list
    :return: argument object
    :rtype: ArgumentParser
    """
    parser = argparse.ArgumentParser(description="Configure your Stratos client")

    parser.add_argument('--platform', '-x', dest="platform", help='Operating System', default='linux',
                        choices=['linux', 'macos', 'win'])
    parser.add_argument('--path', '-p', dest="path_prefix", help='Path prefix', default='')
    parser.add_argument('--queue', '-q', dest="queue", help='AMPQ queue', default='test_queue')

    return parser.parse_args(args)

class StratosClient:
    __platform = None
    __path_prefix = None
    __queue = None
    __command = None

    def __init__(self, args=sys.argv[1:]):
        self.__args = parse_arguments(args)
        self.__platform = self.__args.platform
        self.__path_prefix = self.__args.path_prefix
        self.__queue = self.__args.queue
        self.__command = 'xdg-open'
        if self.__platform == 'macos':
            self.__command = 'open'

    def construct_path(self, path_str):
        if path_str is None:
            return ""
        path_to_file = path_str.strip('"').split("/")
        path_to_file = list(filter(None, path_to_file))
        path_to_file = '/'.join(path_to_file)
        # NOTE: We assume that the root of BOX will live
        #       under the /home/user path
        if self.__path_prefix == '':
            path = Path.home().joinpath(path_to_file)
        else:
            path = Path(self.__path_prefix).joinpath(path_to_file)

        return path

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        cpath = self.construct_path(body.decode())
        print(" [x] path %r" % cpath)
        open_file = subprocess.run([self.__command, cpath])
        print("The exit code was: %d" % open_file.returncode)

    def consume(self):
        parameters = pika.URLParameters(
            'amqps://yhodmfkl:8w6Ya_AtDP5dW6daK83BZUGpbHNEICUA@chimpanzee.rmq.cloudamqp.com/yhodmfkl')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare or bind to the queue
        channel.queue_declare(self.__queue, durable=True)
        channel.basic_consume(queue=self.__queue,
                              on_message_callback=self.callback,
                              auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()


if __name__ == '__main__':
    consumer = StratosClient()
    try:
        consumer.consume()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
