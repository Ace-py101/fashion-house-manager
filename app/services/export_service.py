from pathlib import Path


EXPORT_DIRECTORY = Path(
    "generated_documents"
)


EXPORT_DIRECTORY.mkdir(
    exist_ok=True
)


def build_export_path(

    filename

):

    return (

        EXPORT_DIRECTORY

        /

        filename

    )
