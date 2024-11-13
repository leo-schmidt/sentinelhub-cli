from typing import List

from pydantic import BaseModel, Field


# class CrsProperties(BaseModel):
#     name: str


# class CoordinateSystem(BaseModel):
#     type: str
#     properties: CrsProperties


# class Geometry(BaseModel):
#     crs: CoordinateSystem
#     coordinates: List[List[List[List[float]]]]
#     type: str


class ResultProperties(BaseModel):
    datetime: str
    # proj_geometry: Geometry = Field(..., alias='proj:geometry')
    eo_cloud_cover: float = Field(..., alias="eo:cloud_cover")


class SearchResult(BaseModel):
    id: str
    properties: ResultProperties
    bbox: List[float]

    def __gt__(self, other):
        """
        Custom implementation of the "greater than" function.
        Enables comparison of 2 SearchResult's eo_cloud_cover attribute in order to find the one with the least cloud cover.

        Args:
            other (SearchResult): SearchResult object to compare to.

        Returns:
            bool: Whether this object has the higher cloud cover or the other.
        """
        if isinstance(other, SearchResult):
            if self.properties.eo_cloud_cover > other.properties.eo_cloud_cover:
                return True
            elif self.properties.eo_cloud_cover <= other.properties.eo_cloud_cover:
                return False
