import loguru
import sys

log = loguru.logger
log.remove()
log.add(
    sys.stdout,
    colorize=True,
    format="<m>{time:HH:mm:ss} [{level}]</m> <c>{module}:{function}:{line} | </c><level>{message}</level>",
)
