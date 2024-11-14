import os

from pydantic import ValidationError
import requests
from input_validation import AreaOfInterest, OutputFormats, OutputTypes, TimeOfInterest
from shadapter import SentinelHubAdapter
import typer
from PyInquirer import prompt, print_json
from dotenv import load_dotenv

from oauthlib.oauth2 import BackendApplicationClient, InvalidClientError
from requests_oauthlib import OAuth2Session
from typing_extensions import Annotated


# TODO: use PyInquirer for input types (checkbox, password, etc)
app = typer.Typer()


load_dotenv()


@app.command("authenticate")
def authenticate(
    id: Annotated[str, typer.Argument()],
    secret: Annotated[str, typer.Argument()],
) -> None:
    """Authenticate to Sentinel Hub.

    Args:
        id (Annotated[str, typer.Argument): Client ID
        secret (Annotated[str, typer.Argument): Client Secret
    """
    # client_id = os.environ.get("CLIENT_ID")
    # client_secret = os.environ.get("CLIENT_SECRET")
    client = BackendApplicationClient(client_id=id)
    oauth = OAuth2Session(client=client)
    try:
        oauth.fetch_token(
            token_url="https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token",
            client_secret=secret,
            include_client_id=True,
        )
        typer.echo("Authenticated.")
    except InvalidClientError:
        typer.echo("Wrong credentials. Try again.")


@app.command("request-image")
def request_image(
    # id: Annotated[
    #     str,
    #     typer.Argument(help="Sentinel Hub Client ID."),
    # ] = os.environ.get("CLIENT_ID"),
    # secret: Annotated[
    #     str,
    #     typer.Argument(help="Sentinel Hub Client Secret."),
    # ] = os.environ.get("CLIENT_SECRET"),
    aoi: Annotated[
        tuple[float, float, float, float],
        typer.Argument(help="Area of interest as Bbox."),
    ] = (16.461282, 46.757161, 16.574922, 46.851514),
    toi: Annotated[
        tuple[str, str],
        typer.Argument(help="Time of interest."),
    ] = ["2024-05-01", "2024-05-20"],
    output_type: Annotated[
        OutputTypes,
        typer.Option(help="Image processing type."),
    ] = "visual",
    output_format: Annotated[
        OutputFormats,
        typer.Option(help="Image output format."),
    ] = "png",
):
    """Download the least cloudy Sentinel-2 image."""

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

    # aoi check
    try:
        AreaOfInterest(coords=aoi)
    except ValidationError:
        typer.echo("Area of interest validation failed.\nSee help for input hints.")
        return

    # toi check
    try:
        TimeOfInterest(times=toi)
    except ValidationError:
        typer.echo("Time of interest validation failed.\nSee help for input hints.")
        return

    adapter = SentinelHubAdapter(
        client_id=id,
        client_secret=secret,
    )

    try:
        adapter.request_image(
            aoi_coords=aoi,
            time_interval=toi,
            output_type="ndvi",
            output_format="png",
        )
    except InvalidClientError:
        typer.echo("Client authentication failed. Check your credentials.")
        return

    typer.echo("Downloaded.")


if __name__ == "__main__":
    app()
