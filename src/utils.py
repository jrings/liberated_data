import loguru
import os
import sys

log = loguru.logger
log.remove()
log.add(
    sys.stdout,
    level=os.environ.get("LOG_LEVEL", "DEBUG"),
    colorize=True,
    format="<m>{time:HH:mm:ss} [{level}]</m> <c>{module}:{function}:{line} | </c><level>{message}</level>",
)

def tonum(x):
    try:
        return float(x)
    except:
        return float("nan")