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


class SystemdUnitState(object):
    '''
    systemd unit helper
    '''

    __properties = dict()

    def __init__(self, **kwargs):
        '''
        :param pid: unit pid
        '''
        self.__properties = dict()
        for name, value in kwargs.items():
            self.__properties[name] = value

    def get(self, name):
        '''
        get property
        :param name: property name
        :return: property value if any
        '''
        return self.__properties.get(name, '')
