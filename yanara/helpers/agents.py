from letta import ChatMemory

from yanara.globals import client
from yanara.personae.finalization_agent import FINALIZATION_AGENT_PERSONA_TEMPLATE
from yanara.personae.room_booking_agent import ROOM_BOOKING_AGENT_PERSONA_TEMPLATE
from yanara.tools.lark.finalize_order import finalize_order_for_room_booking
from yanara.tools.lark.room_lookup import lookup_room_availability_by_date
from yanara.tools.lark.staging_order import create_a_staging_order_for_booking_a_room


def create_room_booking_agent():
    """
    Creates and initializes a room booking agent with the necessary tools and memory.

    This agent assists guests with room booking inquiries. It utilizes:
    - `create_a_staging_order_for_booking_a_room`: A tool for recording bookings after collecting the necessary details.
    - `lookup_room_availability_by_date`: A tool for checking room availability on specified dates.

    Returns:
        The newly created agent instance.
    """
    staging_order_tool = next(
        (tool for tool in client.list_tools() if tool.name == "create_a_staging_order_for_booking_a_room"),
        client.create_tool(create_a_staging_order_for_booking_a_room),
    )
    room_lookup_tool = next(
        (tool for tool in client.list_tools() if tool.name == "lookup_room_availability_by_date"),
        client.create_tool(lookup_room_availability_by_date),
    )

    room_booking_agent_persona = ROOM_BOOKING_AGENT_PERSONA_TEMPLATE.format(
        staging_order=staging_order_tool.name, room_lookup=room_lookup_tool.name
    )

    return client.create_agent(
        name="room_booking_agent",
        tool_ids=[staging_order_tool.id, room_lookup_tool.id],
        memory=ChatMemory(human="My name is Sarah", persona=room_booking_agent_persona),
    )


def create_room_booking_finalization_agent():
    """
    Creates and initializes an agent for finalizing room booking orders.

    This agent uses the `finalize_order_for_room_booking` tool to complete
    the booking process after all necessary order details have been collected.

    Returns:
        The newly created agent instance.
    """
    finalize_order_tool = next(
        (tool for tool in client.list_tools() if tool.name == "finalize_order_for_room_booking"),
        client.create_tool(finalize_order_for_room_booking),
    )

    finalization_agent_persona = FINALIZATION_AGENT_PERSONA_TEMPLATE.format(tool_name=finalize_order_tool.name)

    return client.create_agent(
        name="room_booking_finalization_agent",
        tool_ids=[finalize_order_tool.id],
        memory=ChatMemory(
            human="My name is Sarah",
            persona=finalization_agent_persona,
        ),
    )
