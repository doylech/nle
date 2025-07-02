import numpy as np
from nle import nethack


def get_inventory_from_inv(inv_strs, inv_letters):
    inventory = list()
    for letter, line in zip(inv_letters, inv_strs):
        if np.all(line == 0):
            break
        inventory.append((
            letter.tobytes().decode("utf-8").strip('\x00'),
            line.tobytes().decode("utf-8").strip('\x00')
        ))
    return "\n".join(
        f"{letter}: {line}" for letter, line in inventory
    )


def get_view_from_chars(chars):
    char_lines = [line.tobytes().decode("utf-8") for line in chars]

    nonempty = [i for i, ln in enumerate(char_lines) if ln.strip()]
    if nonempty:
        char_lines = char_lines[nonempty[0]: nonempty[-1] + 1]

    indents = [
        len(ln) - len(ln.lstrip(' '))
        for ln in char_lines if ln.strip()
    ]
    if indents:
        k = min(indents)
        # Chop off k spaces from the left of every line
        char_lines = [ln[k:] for ln in char_lines]

    return "\n".join(char_lines)


def get_stats_from_blstats(blstats):
    """Convert blstats array to readable format without interpretation.
    (Not used currently)
    """

    # Get all NLE_BL_ attributes with their values (indices)
    bl_attrs = {getattr(nethack, attr): attr for attr in vars(nethack)
                if attr.startswith('NLE_BL_')}

    bl_attrs = {k.replace('NLE_BL_', ''): v for k, v in bl_attrs.items()}

    lines = []

    for i, value in enumerate(blstats):
        if i in bl_attrs:
            attr_name = bl_attrs[i]
            lines.append(f"{attr_name}: {value}")
        else:
            lines.append(f"Index {i}: {value}")

    return "\n".join(lines)


def get_stats_from_tty(tty_chars):
    """Extract the bottom two status lines from tty_chars array."""

    # Get the last two rows
    if len(tty_chars.shape) == 2 and tty_chars.shape[0] >= 2:
        last_row = tty_chars[-1]  # Bottom row
        second_last_row = tty_chars[-2]  # Second to bottom row

        # Convert ASCII values to characters and join
        line1 = ''.join(chr(c) for c in second_last_row).rstrip()
        line2 = ''.join(chr(c) for c in last_row).rstrip()

        return f"{line1}\n{line2}"
    else:
        return "Unable to extract status lines - unexpected tty_chars shape"


def generate_structured_text(obs, observation_keys) -> str:
    # Message
    message_index = observation_keys.index("message")
    message = bytes(obs[message_index])
    message_str = message.decode("utf-8").strip('\x00')

    # Inventory
    try:
        inv_strs = obs[observation_keys.index("inv_strs")]
        inv_letters = obs[observation_keys.index("inv_letters")]
        inventory_str = get_inventory_from_inv(inv_strs, inv_letters)

    except ValueError:  # inv_strs/letters not used.
        inventory_str = "No inventory data available."

    # View
    char_str = get_view_from_chars(obs[observation_keys.index("chars")])

    # Stats
    stats_str = get_stats_from_tty(obs[observation_keys.index("tty_chars")])

    structured_text = f"""<message>\n{message_str}\n</message>
<inventory>\n{inventory_str}\n</inventory>
<view>\n{char_str}\n</view>
<stats>\n{stats_str}\n</stats>"""

    return structured_text
