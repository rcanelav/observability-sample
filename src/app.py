# These are the necessary import declarations
from opentelemetry import trace
from opentelemetry import metrics

from random import randint
from flask import Flask, request
import logging

# Acquire a tracer
tracer = trace.get_tracer("diceroller.tracer")
# Acquire a meter.
meter = metrics.get_meter("diceroller.meter")

# Now create a counter instrument to make measurements with
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create metric to track how much time takes to roll the dice
request_duration_meter = metrics.get_meter("request_duration_meter")
request_duration_histogram = request_duration_meter.create_histogram(
    name="request_duration_ms",
    description="The distribution of the request durations",
    unit="ms",
)

@app.route("/rolldice")
def roll_dice():
    import time
    # This records the time taken to roll the dice
    start_time = time.time()
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("roll") as roll_span:
        player = request.args.get('player', default=None, type=str)
        result = str(roll())
        roll_span.set_attribute("roll.value", result)
        # This adds 1 to the counter for the given roll value
        roll_counter.add(1, {"roll.value": result})
        
        end_time = time.time()
        duration = end_time - start_time
        # Record the time taken to roll the dice
        request_duration_histogram.record(duration, {"route": "(GET) /rolldice - BY RAMON"})
        logger.info("################## -Request duration: %s", duration)
        logger.debug(" ----------------- Rolling the dice: %s", result)
        if player:
            logger.warn("{} is rolling the dice: {}", player, result)
        else:
            logger.warn("Anonymous player is rolling the dice: %s", result)
        return result
    



def roll():
    return randint(1, 6)
