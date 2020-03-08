# Small FastAPI application that handles parsing

# Logging
import logging
import daiquiri
import sys

# Import schemas
from endpoints import app, 

# Set up daiquiri
daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)

# Log both to stdout and as JSON in a file called /dev/null. (Requires
# `python-json-logger`)
daiquiri.setup(level=logging.INFO, outputs=(
    daiquiri.output.Stream(sys.stdout),
    daiquiri.output.File("sleepsimR_log.json",
                         formatter=daiquiri.formatter.JSON_FORMATTER),
    ))
# Emit
logger.info("Started simulation API ...")

# Take requests
logger.info("Finished setting up the retina. Ready to accept requests ...")



