import inspect
import logging
import sys
import time

from rich.logging import RichHandler

logging.basicConfig(level=logging.DEBUG, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])


def entry(fn):
    """Decorator to mark the function that starts a program."""
    wrapped_fn = lambda *args: fn(*args) if inspect.getmodule(fn).__name__ == "__main__" else None

    if wrapped_fn:
        args = sys.argv[1:]
        wrapped_fn(*args)

    return wrapped_fn


def log_function_call(fn):
    """Decorator to log function calls with dynamic logging control."""

    def wrapper(*args, **kwargs):
        enable_logging = kwargs.pop("enable_logging", False)

        if enable_logging:
            # Get the caller function information
            caller = inspect.stack()[1]
            caller_function_name = caller.function
            caller_filename = caller.filename
            caller_line = caller.lineno

            # Get the callee function and module info
            callee_function_name = fn.__name__
            callee_module_name = fn.__module__

            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

            logging.info(f"Caller: {caller_function_name} in {caller_filename}, line {caller_line}")
            logging.info(f"Callee: {callee_function_name} in module {callee_module_name}")
            logging.info(f"Calling {callee_function_name} with args: {args}, kwargs: {kwargs}")

        start_time = time.time()
        result = fn(*args, **kwargs)
        end_time = time.time()

        if enable_logging:
            logging.info(f"{callee_function_name} executed in {end_time - start_time:.4f} seconds")
            logging.info(f"{callee_function_name} returned: {result}")

        return result

    return wrapper
