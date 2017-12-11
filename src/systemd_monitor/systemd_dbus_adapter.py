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
        '''
        '''
        # main
        self.__logger = logging.getLogger('systemd-monitor')
        # init dbus object
        self.__bus = dbus.SystemBus()
        systemd = self.__bus.get_object(SYSTEMD_SERVICE, SYSTEMD_PATH)
        self.__manager = dbus.Interface(
            systemd, dbus_interface=MANAGER_INTERFACE)

    def __get_object(self, unit):
        '''
        get dbus object by unit name
        :param unit: unit name including extension, str
        :return: object path, dbus object
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
        get dbus object properties by unit name
        :param unit: unit name including extension, str
        :return: object path, properties interface
        '''
        path, obj = self.__get_object(unit)
        return path, dbus.Interface(
            obj, dbus_interface='org.freedesktop.DBus.Properties')

    def __get_unit_interface(self, unit):
        '''
        get unit interface by unit name
        :param unit: unit name including extension, str
        :return: systemd dbus interface name
        '''
        extension = unit.split(
            '.')[-1] if unit.find('.') > -1 else unit.split('_2e')[-1]
        return '{}.{}{}'.format(SYSTEMD_SERVICE, extension[
                                0].upper(), extension[1:])

    def get_units(self):
        '''
        get all units with states
        :return: units dictionary, keys are unit name, value are SystemdUnit
        '''
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
        return dict((unit[0], self.get_unit(unit[6]))
                    for unit in self.__manager.ListUnits()
                    # dunno actually wtf, but okay
                    if not unit[6] in ('org.freedesktop.systemd1.Busname'))

    def get_unit(self, unit):
        '''
        get properties by unit
        :param unit: unit name including extension, str
        :return: SystemdUnit object
        '''
        # generic properties
        path, service = self.__get_properties(unit)
        properties = service.GetAll(UNIT_INTERFACE)
        # type defined properties
        interface = self.__get_unit_interface(unit)
        properties.update(service.GetAll(interface))
        return systemd_unit.SystemdUnit(path, **properties)

    def reload_unit(self, unit, mode='replace'):
        '''
        reload specific unit
        :param unit: unit name including extension, str
        :param mode: reload mode, str, default is replace
        :return:job path if any
        '''
        return self.__manager.ReloadUnit(unit, mode)

    def restart_unit(self, unit, mode='replace'):
        '''
        restart specific unit
        :param unit: unit name including extension, str
        :param mode: restart mode, str, default is replace
        :return:job path if any
        '''
        return self.__manager.RestartUnit(unit, mode)

    def start_unit(self, unit, mode='replace'):
        '''
        start specific unit
        :param unit: unit name including extension, str
        :param mode: start mode, str, default is replace
        :return:job path if any
        '''
        return self.__manager.StartUnit(unit, mode)

    def stop_unit(self, unit, mode='replace'):
        '''
        stop specific unit
        :param unit: unit name including extension, str
        :param mode: stop mode, str, default is replace
        :return:job path if any
        '''
        return self.__manager.StopUnit(unit, mode)

    def __eq__(self, other):
        '''
        comparison method
        :param other: other SystemdDBusAdapter instance
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
        return 'SystemdDBusAdapter()'

    def __str__(self):
        '''
        string conversion method
        :return: string representation of instance
        '''
        return 'SystemdDBusAdapter()'
