import time

def timetext(name) -> str:
    return f"{name}_{int(time.time())}.txt"


def date(target) -> str:
    return target.strftime("%d %B %Y, %H:%M")


def responsible(target, reason) -> str:
    """Builds string for supplying reasons when performing actions.

    Args:
        target (str): The target.
        reason (str): The reason.

    Returns:
        str: The built string.
    """    
    responsible = f"[ {target} ]"
    if reason is None:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case, mass=False):
    output = f"**{case}** the user"

    if mass is True:
        output = f"**{case}** the IDs/Users"

    return f"🦊 Successfully {output}"
