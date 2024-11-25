import asyncio
import logging
import signal

from rich import print

from yanara.api.wechat_api.wechat_message_manager import WeChatMessageManager
from yanara.util.decorators import entry


# Monitoring loop to keep pulling messages until the stop signal is received
async def monitor_wechat_messages(stop_flag: asyncio.Event) -> None:
    """Monitor and process WeChat messages until stop flag is set."""
    print("Monitoring WeChat messages...")
    service = WeChatMessageManager(None)
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

    asyncio.run(monitor_wechat_messages(stop_flag))
