from scenarios.aghrab import SCENARIO as AGHRAB_SCENARIO
from scenarios.bazpors import SCENARIOS as BAZPORS_SCENARIOS
from scenarios.mozakere import SCENARIO as MOZAKERE_SCENARIO

SCENARIOS = {
    **BAZPORS_SCENARIOS,
    "mozakere": MOZAKERE_SCENARIO,
    "aghrab": AGHRAB_SCENARIO,
}
