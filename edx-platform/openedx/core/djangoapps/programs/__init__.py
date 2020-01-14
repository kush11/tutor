"""
Platform support for Programs.

This package is a thin wrapper around interactions with the Programs service,
supporting learner- and author-facing features involving that service
if and only if the service is deployed in the Open edX installation.

To ensure maximum separation of concerns, and a minimum of interdependencies,
this package should be kept small, thin, and stateless.
"""
from openedx.core.djangoapps.waffle_utils import (WaffleSwitch, WaffleSwitchNamespace)

PROGRAMS_WAFFLE_SWITCH_NAMESPACE = WaffleSwitchNamespace(name='programs')

# This is meant to be enabled until https://openedx.atlassian.net/browse/LEARNER-5573 needs to be resolved
ALWAYS_CALCULATE_PROGRAM_PRICE_AS_ANONYMOUS_USER = WaffleSwitch(
    PROGRAMS_WAFFLE_SWITCH_NAMESPACE, 'always_calculate_program_price_as_anonymous_user')
