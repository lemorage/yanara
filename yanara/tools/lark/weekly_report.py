def get_weekly_report_statistics(self: "Agent", which_week: int) -> list[dict]:
    """Get the weekly report statistics for a specific week.

    Args:
        which_week (int): The week number to get the statistics for. Use `datetime.date.today().isocalendar()[1]` to get current week number.

    Returns:
        list[dict]: A list of dictionaries, each containing the processed weekly report statistics.

    Example:
        >>> get_weekly_report_statistics(38)
        [
            {
                "101已售房晚": 6,
                "201已售房晚": 6,
                "202已售房晚": 7,
                "301已售房晚": 7,
                "302已售房晚": 6,
                "401已售房晚": 7,
                "repar": 12870.238095238095,
                "周一日期": "2024-09-16 00:00:00",
                "周日日期": "2024-09-22 00:00:00",
                "周营业额": 540550,
                "平均房价": 13860.25641025641,
                "总儿童数": 0,
                "总晚数": 39,
                "订单数": 16,
                "入住率": "92.86%",
                "第几周": 38,
                "总接待人数": 40,
                "总接待人晚": 100,
            },
        ]
    """
    from datetime import datetime

    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.tools._internal.helpers import process_lark_data
    from yanara.util.date import adjust_timestamp, timestamp_to_datetime

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

    def standardize_report_data(data):
        # Define the key translation and transformation map
        key_map = {
            "総人数": "总接待人数",
            "総人泊数": "总接待人晚",
            "稼働率": ("入住率", lambda v: f"{v * 100:.2f}%"),
            "有効注文数": "订单数",
            "总泊数": "总晚数",
            "売上": "周营业额",
            "周一日期": ("周一日期", lambda v: timestamp_to_datetime(v)),
            "周日日期": ("周日日期", lambda v: timestamp_to_datetime(v)),
        }

        def translate_key_value(key, value):
            """Translate and transform keys and values based on the map."""
            if key in key_map:
                new_key, transform = key_map[key] if isinstance(key_map[key], tuple) else (key_map[key], lambda x: x)
                return new_key, transform(value)
            return key, value

        return [
            {
                new_key: new_value
                for key, value in data[0].items()
                for new_key, new_value in [translate_key_value(key, value)]
            }
        ]

    processed_data = process_lark_data(raw_data)

    # temp solution to process the data
    # TODO: figure out a way to use _process_response_data internally before getting the records
    processed_data[0]["周一日期"] = adjust_timestamp(processed_data[0]["周一日期"], hours=1)
    processed_data[0]["周日日期"] = adjust_timestamp(processed_data[0]["周日日期"], hours=1)

    return standardize_report_data(processed_data)


def weekly_report_typesetting_print(self: "Agent", weekly_report_data: list[dict]) -> str:
    """Print the weekly report typesetting.

    Args:
        weekly_report_data (list[dict]): A list of dictionaries containing the data for the weekly report.
            Currently, it is guaranteed to have only one dictionary in this list to generate the report for one specific week.

    Returns:
        str: The file path to a temporary image file containing the weekly report typesetting.

    Example:
        >>> weekly_report_data = get_weekly_report_statistics(38)
        >>> weekly_report_typesetting_print(weekly_report_data)
        '/var/folders/9n/zrq49fmx27l7237gf4kj001h0000gn/T/tmpb3m53r1t.png'
    """

    import base64
    from datetime import datetime, timezone
    import io
    import tempfile

    from PIL import Image, ImageDraw, ImageFont

    with open("yanara/tools/lark/encoded_font.txt", "r") as encoded_file:
        encoded_font = encoded_file.read()

    font_data = base64.b64decode(encoded_font)
    font_file = io.BytesIO(font_data)

    # Extract data (guaranteed to have only one item)
    weekly_report_data = weekly_report_data[0]

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
        f"第几周: {weekly_report_data['第几周']}",
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
        f"日期: {weekly_report_data['周一日期']} ~ {weekly_report_data['周日日期']}",
        font=font,
        fill="black",
        anchor="mm",
    )

    # Move to next row
    table_y += row_height

    # Define table data
    table_data = [
        [
            f"本周入住率: {weekly_report_data['入住率']}",
            f"周营业额: {weekly_report_data['周营业额']}",
            f"总晚数: {weekly_report_data['总晚数']}",
        ],
        [f"平均房价: {weekly_report_data['平均房价']}", f"Repar: {weekly_report_data['repar']}", ""],
        [f"订单平均金额: 24558", f"订单数: {weekly_report_data['订单数']}", ""],
        [
            f"总接待人数: {weekly_report_data['总接待人数']}",
            f"总接待人晚: {weekly_report_data['总接待人晚']}",
            f"总儿童数: {weekly_report_data['总儿童数']}",
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
        f"101已售{weekly_report_data['101已售房晚']}晚; 201已售{weekly_report_data['201已售房晚']}晚; "
        f"202已售{weekly_report_data['202已售房晚']}晚;\n301已售{weekly_report_data['301已售房晚']}晚; "
        f"302已售{weekly_report_data['302已售房晚']}晚; 401已售{weekly_report_data['401已售房晚']}晚"
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

    # Save the image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        img.save(tmp_file, format="PNG")
        tmp_file_path = tmp_file.name

    return tmp_file_path
