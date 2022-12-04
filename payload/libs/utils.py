# Utilities for endpoints

import sh

def cust():
    """Returns the endpoint customer identifier string.

    :returns: Customer ID.
    """

    return sh.cat("/run/payload-runtime/cust.cfg").strip()

def site():
    """Returns the endpoint site identifier string.

    :returns: Site ID.
    """

    return sh.cat("/run/payload-runtime/site.cfg").strip()

def serial():
    """Returns the endpoint serial number.

    :returns: Serial Number.
    """

    return sh.cat("/run/payload-runtime/serial.cfg").strip()

def reboots():
    """Returns the number of reboots.

    This number is updated by the /bin/updater service that is
    supplied by the IOT framework.

    :returns: Number of reboots.
    """

    return sh.cat("/home/iot/firmware-reboots.cfg").strip()

def settings_version():
    """Returns the current endpoint settings version.

    This number is updated by /bin/updater
    that is supplied by the IOT framework. The number reported
    may not be the real latest version in the cloud, as the
    endpoint's internet connection may be offline.

    :returns: Settings version.
    """

    return sh.cat("/run/settings/version.cfg").strip()

def payload_version():
    """Returns the current endpoint payload version.

    This number is updated by the /bin/updater
    that is supplied by the IOT framework. The number reported
    may not be the real latest version in the cloud, as the
    endpoint's internet connection may be offline.

    :returns: Payload version.
    """
    return sh.cat("/home/iot/payload/version.cfg").strip()


