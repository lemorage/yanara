def get_weekly_report_statistics(self: "Agent", which_week: str) -> list[dict]:
    """Get the weekly report statistics for a specific week.

    Args:
        which_week (str): The week number to get the statistics for.

    Returns:
        list[dict]: A list of dictionaries, each containing the processed weekly report statistics.

    Example:
        >>> get_weekly_report_statistics("38")
        [
            {
                "101已售房晚": 6,
                "201已售房晚": 6,
                "202已售房晚": 7,
                "301已售房晚": 7,
                "302已售房晚": 6,
                "401已售房晚": 7,
                "repar": 12870.238095238095,
                "周一日期": 1726412400000,
                "周日日期": 1726930800000,
                "売上": 540550,
                "平均房价": 13860.25641025641,
                "总儿童数": 0,
                "总泊数": 39,
                "有効注文数": 16,
                "稼働率": 0.9285714285714286,
                "第几周": 38,
                "総人数": 40,
                "総人泊数": 100,
            },
        ]
    """
    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.tools._internal.helpers import process_lark_data

    lark_service = LarkTableService("KFo5bqi26a52u2s5toJcrV6tnWb")

    raw_data = lark_service.fetch_records_with_exact_value(
        table_id="tblulMPBjoYKFpDg",
        view_id="vew8UWgWyj",
        field_names=[
            "第几周",
            "周一日期",
            "周日日期",
            "repar",
            "総人数",
            "総人泊数",
            "总儿童数",
            "总泊数",
            "稼働率",
            "売上",
            "平均房价",
            "有効注文数",
            "101已售房晚",
            "201已售房晚",
            "202已售房晚",
            "301已售房晚",
            "302已售房晚",
            "401已售房晚",
        ],
        filter_field_name="第几周",
        filter_value=str(which_week),
    )

    return process_lark_data(raw_data)


def weekly_report_typesetting_print(self: "Agent") -> str:
    """Print the weekly report typesetting.

    Args:
        None

    Returns:
        str: A base64-encoded image of the weekly report typesetting.

    Example:
        >>> weekly_report_typesetting_print()
        'iVBORw0KGgoAAAANSUhEUgAAAXo
        ...
    """

    import base64
    from datetime import datetime, timezone
    import io

    from PIL import Image, ImageDraw, ImageFont

    with open("encoded_font.txt", "r") as encoded_file:
        encoded_font = encoded_file.read()

    font_data = base64.b64decode(encoded_font)
    font_file = io.BytesIO(font_data)

    # Extract data
    item = {
        "第几周": 37,
        "周一日期": 1726412400000,
        "周日日期": 1726930800000,
        "稼働率": 0.76,
        "売上": 451190,
        "repar": 10743,
        "平均房价": 14100,
        "总泊数": 32,
        "有効注文数": 18,
        "総人数": 50,
        "総人泊数": 73,
        "総儿童数": 0,
        "101已售房晚": 6,
        "201已售房晚": 5,
        "202已售房晚": 5,
        "301已售房晚": 3,
        "302已售房晚": 6,
        "401已售房晚": 7,
    }
    week_start = datetime.fromtimestamp(item["周一日期"] / 1000, timezone.utc).strftime("%Y/%m/%d")
    week_end = datetime.fromtimestamp(item["周日日期"] / 1000, timezone.utc).strftime("%Y/%m/%d")

    # Create image
    img_width, img_height = 1200, 800
    img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Font settings
    font = ImageFont.truetype(font_file, 22)

    # Table dimensions
    table_x, table_y = 50, 50
    col_width = (img_width - 100) // 3
    row_height = 60

    # Draw header row
    draw.rectangle(
        [table_x, table_y, table_x + col_width, table_y + row_height],
        outline="black",
        width=2,
    )
    draw.text(
        (table_x + col_width // 2, table_y + row_height // 2),
        f"第几周: {item['第几周']}",
        font=font,
        fill="black",
        anchor="mm",
    )

    draw.rectangle(
        [table_x + col_width, table_y, table_x + col_width * 3, table_y + row_height],
        outline="black",
        width=2,
    )
    draw.text(
        (table_x + col_width * 2, table_y + row_height // 2),
        f"日期: {week_start}~{week_end}",
        font=font,
        fill="black",
        anchor="mm",
    )

    # Move to next row
    table_y += row_height

    # Define table data
    table_data = [
        [
            f"本周入住率: {item['稼働率'] * 100:.0f}%",
            f"周营业额: {item['売上']}",
            f"总晚数: {item['总泊数']}",
        ],
        [f"平均房价: {item['平均房价']}", f"Repar: {item['repar']}", ""],
        [f"订单平均金额: 24558", f"订单数: {item['有効注文数']}", ""],
        [
            f"总接待人数: {item['総人数']}",
            f"总接待人晚: {item['総人泊数']}",
            f"总儿童数: {item['総儿童数']}",
        ],
    ]

    # Draw table rows
    for row in table_data:
        for col_index, cell in enumerate(row):
            x0 = table_x + col_width * col_index
            y0 = table_y
            x1 = x0 + col_width
            y1 = y0 + row_height
            draw.rectangle([x0, y0, x1, y1], outline="black", width=2)
            draw.text(
                (x0 + col_width // 2, y0 + row_height // 2),
                str(cell),
                font=font,
                fill="black",
                anchor="mm",
            )
        table_y += row_height

    # Room sales data (merged cell)
    room_sales_text = (
        f"101已售{item['101已售房晚']}晚; 201已售{item['201已售房晚']}晚; "
        f"202已售{item['202已售房晚']}晚;\n301已售{item['301已售房晚']}晚; "
        f"302已售{item['302已售房晚']}晚; 401已售{item['401已售房晚']}晚"
    )
    draw.rectangle(
        [table_x, table_y, table_x + col_width * 3, table_y + row_height * 3],
        outline="black",
        width=2,
    )
    draw.text(
        (table_x + col_width * 1.5, table_y + row_height + 3),
        room_sales_text,
        font=font,
        fill="black",
        anchor="mm",
    )

    # Save image
    img.save("refined_table.png")
