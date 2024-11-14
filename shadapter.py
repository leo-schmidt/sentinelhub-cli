import os
from typing import List, Literal, Tuple, Union
from sentinelhub import (
    SHConfig,
    DataCollection,
    SentinelHubCatalog,
    SentinelHubRequest,
    BBox,
    bbox_to_dimensions,
    CRS,
    MimeType,
    write_data,
)
from models import SearchResult
from evalscripts import EvalScript


class SentinelHubAdapter:
    def __init__(self, client_id, client_secret):
        self.config = SHConfig()
        self.config.sh_client_id = client_id
        self.config.sh_client_secret = client_secret

    def _search_catalog(
        self,
        aoi_bbox: BBox,
        time_interval: Tuple[str],
    ) -> List[SearchResult]:
        """Uses the SentinelHub Catalog API to search for Sentinel2-L2a images
        in the specified area and time interval.

        Args:
            aoi_bbox (Tuple[float]): Area of interest as Bbox (X1, Y1, X2, Y2)
            time_interval (Tuple[str]): Time interval of interest (Start date, end date)

        Returns:
            List[SearchResult]: List of found images within specified ranges.
        """
        catalog = SentinelHubCatalog(config=self.config)

        search_iterator = catalog.search(
            DataCollection.SENTINEL2_L2A,
            bbox=aoi_bbox,
            time=time_interval,
            fields={
                "include": [
                    "id",
                    "properties.datetime",
                    "properties.eo:cloud_cover",
                    "bbox",
                ],
                "exclude": ["stac_version", "stac_extensions", "links"],
            },
        )

        search_results = [
            SearchResult.model_validate(result) for result in search_iterator
        ]
        return search_results

    def request_image(
        self,
        aoi_coords: Tuple[float],
        time_interval: Tuple[str],
        output_type: Literal["visual", "ndvi"] = "visual",
        output_format: MimeType = "png",
    ) -> Union[SearchResult, None]:
        """Finds the least clouded image and uses the Sentinel Hub Process API
        to download it.

        Args:
            aoi_coords (Tuple[float]): Area of interest (X1, Y1, X2, Y2)
            time_interval (Tuple[str]): Time interval of interest (Start date, end date)
            output_type (Literal["visual", "ndvi"]): Image output type
            output_format (MimeType): Image output format

        Returns:
            str | None: Path to downloaded file.
        """
        aoi_bbox = BBox(bbox=aoi_coords, crs=CRS.WGS84)
        aoi_size = bbox_to_dimensions(
            aoi_bbox,
            resolution=10,  # highest resolution in meters
        )
        # maximum allowable aoi size is 2500x2500 pixels
        if aoi_size[0] >= 2500:
            raise ValueError("Requested image width is too large.")
        if aoi_size[1] >= 2500:
            raise ValueError("Requested image height is too large.")

        # set eval_script
        if output_type == "visual":
            eval_script = EvalScript.VISUAL.value
        elif output_type == "ndvi":
            eval_script = EvalScript.NDVI.value
        else:
            raise ValueError("""Output type not one of ("visual", "ndvi")""")

        # search catalog and get best result (= lowest cloud cover)
        search_results = self._search_catalog(aoi_bbox, time_interval)
        if not search_results:
            return
        best_result = min(search_results)

        # get image and download
        request_img = SentinelHubRequest(
            evalscript=eval_script,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(
                        best_result.properties.datetime,
                        best_result.properties.datetime,
                    ),
                    # other_args={"dataFilter": {"mosaickingOrder": "leastCC"}},
                )
            ],
            responses=[
                SentinelHubRequest.output_response(
                    "default",
                    response_format=output_format,
                )
            ],
            bbox=aoi_bbox,
            size=aoi_size,
            config=self.config,
            data_folder="data",
        )

        image = request_img.get_data(show_progress=True)
        file_name = f"data/{best_result.properties.datetime}_{aoi_coords[0]}_{aoi_coords[1]}_{output_type}.{output_format}"
        write_data(
            filename=file_name,
            data=image[0],
        )
        return best_result  # , file_name


if __name__ == "__main__":
    adapter = SentinelHubAdapter(
        os.environ.get("CLIENT_ID"),
        os.environ.get("CLIENT_SECRET"),
    )
    file = adapter.request_image(
        (15.461282, 46.757161, 15.574922, 46.851514),
        ("2024-05-01", "2024-05-20"),
        "visual",
        "png",
    )
    print(file)
