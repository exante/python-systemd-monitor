#################################################################################
# Copyright (c) 2016 EXANTE                                                     #
#                                                                               #
# Permission is hereby granted, free of charge, to any person obtaining a copy  #
# of this software and associated documentation files (the "Software"), to deal #
# in the Software without restriction, including without limitation the rights  #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell     #
# copies of the Software, and to permit persons to whom the Software is         #
# furnished to do so, subject to the following conditions:                      #
#                                                                               #
# The above copyright notice and this permission notice shall be included in    #
# all copies or substantial portions of the Software.                           #
#################################################################################

import copy
import datetime
import json
import logging
import subprocess
import threading
import time

import systemd_dbus_adapter


class JournaldWorker(threading.Thread):
    '''
    journald helper/notifier
    '''

    __cmdline = ['journalctl', '-f', '-o', 'json']
    __lock = None
    __logger = None
    __lst = datetime.datetime.utcnow()
    __should_run = True
    __states = dict()
    __status = False
    __systemd = None

    def __init__(self):
        # thread properties
        threading.Thread.__init__(self)
        self.__lock = threading.Lock()
        self.daemon = True
        # main
        self.__logger = logging.getLogger('systemd-monitor')
        self.__systemd = systemd_dbus_adapter.SystemdDBusAdapter()

    @property
    def last_sync_time(self):
        '''
        :return: last journal update time
        '''
        with self.__lock:
            return copy.deepcopy(self.__lst)

    @property
    def states(self):
        '''
        :return: current states
        '''
        with self.__lock:
            return copy.deepcopy(self.__states)

    @property
    def status(self):
        '''
        :return: current status
        '''
        return self.__status

    def __get_journal(self):
        '''
        get journal stdout
        '''
        process = subprocess.Popen(self.__cmdline, stdout=subprocess.PIPE)
        return iter(process.stdout.readline, '')

    def __load_states(self):
        '''
        initial services load
        '''
        self.__states = self.__systemd.get_all()

    def run(self):
        '''
        run thread
        '''
        self.__load_states()
        while self.__should_run:
            try:
                for line in self.__get_journal():
                    self.__status = True
                    # exit on no actions
                    if not self.__should_run:
                        break
                    # parse line
                    if isinstance(line, bytes):
                        line = line.decode('utf8')
                    data = json.loads(line)
                    # check if it is unit related infomation
                    if 'UNIT' not in data:
                        continue
                    # update internal storage
                    with self.__lock:
                        self.__states[
                            data['UNIT']] = self.__systemd.get(
                            data['UNIT'])
                        self.__lst = datetime.datetime.utcnow()
            except Exception:
                self.__logger.warning('Exception recieved', exc_info=True)
                self.__status = False
            time.sleep(60)

    def stop(self):
        '''
        stop worker
        '''
        with self.__lock:
            self.__should_run = False
