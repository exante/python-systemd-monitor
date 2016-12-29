# python-systemd-monitor

Library functions to monitor state of systemd spawned units

## Example usage

1. Realtime monitoring

    ```python
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
            # lets start failed unit
            if state["unit"].get("ActiveState") == "failed":
                print("Unit {} started, job ID {}".format(unit, state["unit"].start()))
        # SystemdUnit object is actually a dictionary which contains all properties
        # comes from DBus, see https://www.freedesktop.org/wiki/Software/systemd/dbus/
        # for available properties names

        time.sleep(60)
    ```

2. Single-thread realtime monitoring

    ```python
    from systemd_monitor.journald_worker import JournaldWorker

    worker = JournaldWorker()

    for unit, state in worker.run_iterate():
        print("Update received for unit {}".format(unit))
    ```

3. Get unit properties

    ```python
    from systemd_monitor.systemd_dbus_adapter import SystemdDBusAdapter

    dbus = SystemdDBusAdapter()

    # get all units
    all_units = dbus.get_units()
    # get specific unit
    unit = dbus.get_unit('foo.service')
    # reload unit
    dbus.reload_unit('foo.service')
    ```
