import asyncio
import logging
import signal

from rich import print

from yanara.api.wechat_api.wechat_message_manager import WeChatMessageManager
from yanara.util.decorators import entry

####################################################################################################
#                                                                                                  #
#  NOTE: This __main__.py module is for illustration purposes only.                                #
#                                                                                                  #
#  - This script demonstrates the functionality of a WeChat message monitoring loop                #
#    using the `WeChatMessageManager` class.                                                       #
#                                                                                                  #
#  - It is NOT intended for production use.                                                        #
#                                                                                                  #
#  - In real-world applications:                                                                   #
#      1. The `agent_id` should be properly passed instead of using `None`.                        #
#      2. Proper error handling, logging, and configuration management should be implemented.      #
#      3. Secure handling of credentials and environment-specific settings should be ensured.      #
#                                                                                                  #
#  Use this code as a starting point or reference for development, but adapt it to meet the        #
#  requirements of the actual production environment.                                              #
#                                                                                                  #
####################################################################################################


# Monitoring loop to keep pulling messages until the stop signal is received
async def monitor_wechat_messages(agent_id: str, stop_flag: asyncio.Event) -> None:
    """Monitor and process WeChat messages until stop flag is set."""
    print("Monitoring WeChat messages...")
    service = WeChatMessageManager(agent_id)
    while not stop_flag.is_set():
        await service.schedule_pulling_messages()
        await asyncio.sleep(5)
    print("Monitoring stopped.")


# Stop signal handler to stop the loop
def stop_loop(signal_received, frame, stop_flag: asyncio.Event) -> None:
    """Handles the shutdown signal and sets the stop flag."""
    stop_flag.set()
    print("Shutdown signal received. Stopping...")


@entry
def main():
    stop_flag = asyncio.Event()

    # Register the signal handler
    signal.signal(signal.SIGINT, lambda s, f: stop_loop(s, f, stop_flag))
    signal.signal(signal.SIGTERM, lambda s, f: stop_loop(s, f, stop_flag))

    asyncio.run(monitor_wechat_messages(None, stop_flag))
