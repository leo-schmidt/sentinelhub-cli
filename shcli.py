import os
from pydantic import ValidationError
from utils.input_validation import (
    AreaOfInterest,
    OutputFormats,
    OutputTypes,
    TimeOfInterest,
)
from shadapter import SentinelHubAdapter
import typer
from PyInquirer import prompt

from oauthlib.oauth2 import InvalidClientError
from typing_extensions import Annotated
from dotenv import load_dotenv

app = typer.Typer()

load_dotenv()


@app.command("request-image")
def request_image(
    aoi: Annotated[
        str,
        typer.Argument(
            help="Area of interest as boundary bbox. Format: x1,y1,x2,y2. Example: 13.325,52.476,13.491,52.561"
        ),
    ],
    toi: Annotated[
        str,
        typer.Argument(
            help="Time of interest as interval. Format: YYYY-MM-DD,YYYY-MM-DD. Example: 2024-10-01,2024-10-30"
        ),
    ],
    output_type: Annotated[
        OutputTypes,
        typer.Option("--type", "-t", help="Image processing type."),
    ] = "visual",
    output_format: Annotated[
        OutputFormats,
        typer.Option("--format", "-f", help="Image output format."),
    ] = "png",
    env: Annotated[
        bool,
        typer.Option(help="Option to read credentials from .env file."),
    ] = False,
):
    """Download the least cloudy Sentinel-2 image."""

    # INPUT VALIDATION
    # aoi check
    aoi = tuple(aoi.split(","))
    try:
        AreaOfInterest(coords=aoi)
    except ValidationError:
        typer.echo("Area of interest validation failed.\nSee --help for input hints.")
        return

    # toi check
    toi = tuple(toi.split(","))
    try:
        TimeOfInterest(times=toi)
    except ValidationError:
        typer.echo("Time of interest validation failed.\nSee --help for input hints.")
        return

    # CREDENTIALS
    if env:
        id = os.environ.get("CLIENT_ID")
        secret = os.environ.get("CLIENT_SECRET")
    else:
        answers = prompt(
            questions=[
                {
                    "name": "id",
                    "message": "Your Sentinel Hub Client ID:",
                    "type": "input",
                },
                {
                    "name": "secret",
                    "message": "Your Sentinel Hub Client Secret:",
                    "type": "password",
                },
            ]
        )

        id = answers["id"]
        secret = answers["secret"]

    # DOWNLOAD
    adapter = SentinelHubAdapter(
        client_id=id,
        client_secret=secret,
    )
    try:
        result = adapter.request_image(
            aoi_coords=aoi,
            time_interval=toi,
            output_type=output_type.value,
            output_format=output_format.value,
        )
    except InvalidClientError:
        typer.echo("Client authentication failed. Check your credentials.")
        return
    except ValueError as e:
        print(e)
        return

    if result:
        typer.echo(
            f"""
            Best image result:
            {result.id}
            Datetime: {result.properties.datetime}
            Cloud cover: {result.properties.eo_cloud_cover}
            """
        )
    else:
        typer.echo("No image found for specified ranges.")


if __name__ == "__main__":
    app()
