from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import (

    SimpleDocTemplate,

    Paragraph,

    Spacer,

    Table,

    TableStyle

)

from reportlab.lib import colors

from app.services.export_service import (

    build_export_path

)


def create_measurement_pdf(

    measurement,

    customer,

    order

):

    filename = (

        f"{measurement.measurement_id}.pdf"

    )

    pdf_path = build_export_path(

        filename

    )

    document = SimpleDocTemplate(

        str(pdf_path)

    )

    styles = getSampleStyleSheet()

    story = []

    story.append(

        Paragraph(

            "<b>Measurement Sheet</b>",

            styles["Title"]

        )

    )

    story.append(

        Spacer(

            1,

            20

        )

    )

    customer_table = Table([

        [

            "Customer",

            customer.full_name

        ],

        [

            "Customer Code",

            customer.customer_code

        ],

        [

            "Phone",

            customer.phone

        ],

        [

            "Order",

            order.order_id

        ],

        [

            "Garment",

            order.garment_name

        ],

        [

            "Measurement Type",

            measurement.measurement_type

        ],

        [

            "Unit",

            measurement.measurement_unit

        ]

    ])

    customer_table.setStyle(

        TableStyle([

            (

                "GRID",

                (0, 0),

                (-1, -1),

                1,

                colors.black

            ),

            (

                "BACKGROUND",

                (0, 0),

                (0, -1),

                colors.lightgrey

            ),

            (

                "BOTTOMPADDING",

                (0, 0),

                (-1, -1),

                8

            )

        ])

    )

    story.append(

        customer_table

    )

    story.append(

        Spacer(

            1,

            20

        )

    )

    for section, values in (

        measurement.measurement_data.items()

    ):

        story.append(

            Paragraph(

                f"<b>{section}</b>",

                styles["Heading2"]

            )

        )

        rows = [

            [

                "Measurement",

                "Value"

            ]

        ]

        for name, value in (

            values.items()

        ):

            rows.append(

                [

                    name,

                    value or "-"

                ]

            )

        table = Table(

            rows

        )

        table.setStyle(

            TableStyle([

                (

                    "GRID",

                    (0, 0),

                    (-1, -1),

                    1,

                    colors.black

                ),

                (

                    "BACKGROUND",

                    (0, 0),

                    (-1, 0),

                    colors.lightgrey

                )

            ])

        )

        story.append(

            table

        )

        story.append(

            Spacer(

                1,

                15

            )

        )

    document.build(

        story

    )

    return pdf_path
