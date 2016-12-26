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

import copy
import dbus
import logging
# for name encoding
try:
    from urllib.parse import quote_plus as EncodeString
except ImportError:
    from urllib import quote_plus as EncodeString

from systemd_dbus_paths import *
import systemd_unit


class SystemdDBusAdapter(object):
    '''
    systemd dbus adapter
    '''

    __bus = None
    __logger = None
    __manager = None

    def __init__(self):
        # main
        self.__logger = logging.getLogger('systemd-monitor')
        # init dbus object
        self.__bus = dbus.SystemBus()
        systemd = self.__bus.get_object(SYSTEMD_SERVICE, SYSTEMD_PATH)
        self.__manager = dbus.Interface(
            systemd, dbus_interface=MANAGER_INTERFACE)

    def __define_type(self, unit):
        '''
        define type by unit name
        :param unit: unit name
        :return: systemd dbus interface name
        '''
        extension = unit.split(
            '.')[-1] if unit.find('.') > -1 else unit.split('_2e')[-1]
        return 'org.freedesktop.systemd1.{}{}'.format(
            extension[0].upper(), extension[1:])

    def __get_object(self, unit):
        '''
        get dbus object by name
        :param unit: unit name
        :return: dbus object
        '''
        if not unit.startswith('/'):
            # initial string encoding
            unit = EncodeString(unit).lower().replace('%', '_')
            # replace other characters now
            unit = unit.replace('.', '_2e').replace('-', '_2d')
            # and prepend path
            unit = '{}/{}'.format(UNIT_PATH, unit)
        return unit, self.__bus.get_object(SYSTEMD_SERVICE, unit)

    def __get_properties(self, unit):
        '''
        get object properties by name
        :param unit: unit name
        :return: properties interface
        '''
        path, obj = self.__get_object(unit)
        return path, dbus.Interface(
            obj, dbus_interface='org.freedesktop.DBus.Properties')

    def get_all(self):
        '''
        get all services with states
        :return: services dictionary
        '''
        states = dict()
        units = self.__manager.ListUnits()
        for unit in units:
            # from https://www.freedesktop.org/wiki/Software/systemd/dbus/
            # The primary unit name as string
            # The human readable description string
            # The load state (i.e. whether the unit file has been loaded successfully)
            # The active state (i.e. whether the unit is currently started or not)
            # The sub state (a more fine-grained version of the active state that is specific to the unit type, which the active state is not)
            # A unit that is being followed in its state by this unit, if there is any, otherwise the empty string.
            # The unit object path
            # If there is a job queued for the job unit the numeric job id, 0 otherwise
            # The job type as string
            # The job object path
            states[unit[0]] = self.get(unit[6])
        return states

    def get(self, unit):
        '''
        get properties
        :param unit: unit name including extension
        :return: SystemdUnit object
        '''
        # generic properties
        path, service = self.__get_properties(unit)
        properties = service.GetAll(UNIT_INTERFACE)
        # type defined properties
        interface = self.__define_type(unit)
        properties.update(service.GetAll(interface))
        return systemd_unit.SystemdUnit(path, **properties)

    def reload_unit(self, unit, mode='replace'):
        '''
        reload specific unit
        :param unit: unit name
        :param mode: reload mode, default is replace
        :return:job path if any
        '''
        return self.__manager.ReloadUnit(unit, mode)

    def restart_unit(self, unit, mode='replace'):
        '''
        restart specific unit
        :param unit: unit name
        :param mode: restart mode, default is replace
        :return:job path if any
        '''
        return self.__manager.RestartUnit(unit, mode)

    def start_unit(self, unit, mode='replace'):
        '''
        start specific unit
        :param unit: unit name
        :param mode: start mode, default is replace
        :return:job path if any
        '''
        return self.__manager.StartUnit(unit, mode)

    def stop_unit(self, unit, mode='replace'):
        '''
        stop specific unit
        :param unit: unit name
        :param mode: stop mode, default is replace
        :return:job path if any
        '''
        return self.__manager.StopUnit(unit, mode)
