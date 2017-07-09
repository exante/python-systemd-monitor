##########################################################################
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
##########################################################################


import dbus

from systemd_dbus_paths import *


class SystemdUnit(object):
    '''
    systemd unit helper
    '''

    __dbus_interface = None
    __dbus_object = None
    __obj_path = ''
    __properties = dict()

    def __init__(self, obj_path, **kwargs):
        '''
        :param obj_path: path to dbus object, str
        :param kwargs: dictionary of properties from dbus
        '''
        self.__obj_path = obj_path
        self.__properties = dict()
        for name, value in kwargs.items():
            self.__properties[name] = value
        # init dbus session
        self.__init_dbus()

    def __init_dbus(self):
        '''
        init dbus interface
        '''
        system_bus = dbus.SystemBus()
        self.__dbus_obj = system_bus.get_object(
            SYSTEMD_SERVICE, self.__obj_path)
        self.__dbus_interface = dbus.Interface(
            self.__dbus_obj, dbus_interface=UNIT_INTERFACE)

    def get(self, name):
        '''
        get property
        :param name: property name
        :return: property value if any, otherwise return empty string
        '''
        return self.__properties.get(name, '')

    def get_and_update(self, name):
        '''
        get property from dbus and assing in internal storage
        :param name: property name
        :return: property value
        '''
        prop_interface = dbus.Interface(
            self.__dbus_obj, dbus_interface='org.freedesktop.DBus.Properties')
        self.__properties[name] = prop_interface.Get(UNIT_INTERFACE, name)
        return self.__properties[name]

    def reload(self, mode='replace'):
        '''
        reload unit
        :param mode: reload mode, str, default is replace
        :return: job path if any
        '''
        return self.__dbus_interface.Reload(mode)

    def restart(self, mode='replace'):
        '''
        restart unit
        :param mode: restart mode, str, default is replace
        :return: job path if any
        '''
        return self.__dbus_interface.Restart(mode)

    def start(self, mode='replace'):
        '''
        start unit
        :param mode: start mode, str, default is replace
        :return: job path if any
        '''
        return self.__dbus_interface.Start(mode)

    def stop(self, mode='replace'):
        '''
        stop unit
        :param mode: stop mode, str, default is replace
        :return: job path if any
        '''
        return self.__dbus_interface.Stop(mode)

    def __eq__(self, other):
        '''
        comparison method
        :param other: other SystemdUnit instance
        :return: True if instances equal
        '''
        return self.__repr__() == other.__repr__()

    def __hash__(self):
        '''
        make class hashable
        :return: hash of self.__repr__()
        '''
        return hash(self.__repr__())

    def __repr__(self):
        '''
        representation method
        :return: string representation of instance
        '''
        return 'SystemdUnit({}, properties: {})'.format(self.__obj_path, sorted(self.__properties, key=lambda k: k))

    def __str__(self):
        '''
        string conversion method
        :return: string representation of instance
        '''
        return 'SystemdUnit({})'.format(self.__obj_path)
