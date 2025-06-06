from __future__ import absolute_import, annotations

import re

import pint

from kslurm.exceptions import ValidationError

ureg = pint.UnitRegistry()


def time(time: str):
    if ":" in time:
        if "-" in time:
            days, hhmm = time.split("-")
            hours, min = hhmm.split(":")
        else:
            days = "0"
            hours, min = time.split(":")
    else:
        raise TypeError(
            f'Invalid format for time: "{time}"\n'
            f"Must be as [xx-]xx:xx or x where x is a number"
        )
    return int(min) + int(hours) * 60 + int(days) * 60 * 24


def mem(mem: str):
    if not (match := re.match(r"^([0-9]+[GMKgmk][Ii]?)[bB]?$", mem)):
        raise ValidationError(
            "Memory is not formatted correctly. Must be xxx(G|M)[B], e.g. 32G, 4000MB, "
            "etc"
        )
    return int(
        ureg(
            (match.group(1) + "B")
            .upper()
            .replace("K", "k")
            .replace("I", "i")
            .replace("ki", "Ki")
        )
        .to("megabyte")  # type: ignore
        .m
    )


def gpu(raw: str):
    if raw == "gpu":
        return "1"

    rhs = raw.split("=", 1)[1]

    if rhs.isdigit():
        return rhs

    if ":" in rhs:
        typ, cnt = rhs.split(":", 1)
        if cnt.isdigit() and int(cnt) >= 1:
            return f"{typ}:{cnt}"
        else:
            return f"{typ}:1"

    return f"{rhs}:1"
