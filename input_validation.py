import datetime
from enum import Enum
from typing import Tuple
from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated


class OutputTypes(Enum):
    VISUAL = "visual"
    NDVI = "ndvi"


class OutputFormats(Enum):
    PNG = "png"
    TIFF = "tiff"


def check_x_coords(x: int):
    assert -180 <= x <= 180
    return x


def check_y_coords(y: int):
    assert -90 <= y <= 90
    return y


CoordX = Annotated[float, AfterValidator(check_x_coords)]
CoordY = Annotated[float, AfterValidator(check_y_coords)]


class AreaOfInterest(BaseModel):
    coords: Tuple[CoordX, CoordY, CoordX, CoordY]


def check_date_format(date: str):
    assert datetime.date.fromisoformat(date)
    return date


Time = Annotated[str, AfterValidator(check_date_format)]


class TimeOfInterest(BaseModel):
    times: Tuple[Time, Time]
