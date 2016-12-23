# python-systemd-monitor

Library functions to monitor state of systemd spawned units

## Example usage

1. Realtime monitoring

    ```
    import time
    from systemd_monitor.journald_worker import JournaldWorker

    worker = JournaldWorker()
    worker.start()

    while True:
        states = worker.states

        # do what you need with these statuses
        # lets print states for example

        for unit in states:
            print("Unit {}: state {}, substate {}".format(unit, states[unit].get('ActiveState'), states[unit].get('SubState')))
        # SystemdUnitState object is actually a dictionary which contains all properties
        # comes from DBus, see https://www.freedesktop.org/wiki/Software/systemd/dbus/
        # for available properties names

        time.sleep(60)
    ```

2. Get unit properties

    ```
    from systemd_monitor.systemd_dbus_adapter import SystemdDBusAdapter

    dbus = SystemdDBusAdapter()

    # get all units
    all_units = dbus.get_all()
    # get specific unit
    unit = dbus.get('foo.service')
    ```
