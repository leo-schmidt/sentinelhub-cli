import os
from models import SearchResult
from evalscripts import EvalScripts

from sentinelhub import (
    SHConfig,
    DataCollection,
    SentinelHubCatalog,
    SentinelHubRequest,
    BBox,
    # bbox_to_dimensions,
    CRS,
    MimeType,
)


class SentinelHubAdapter:
    def __init__(self, client_id, client_secret):
        self.config = SHConfig()
        self.config.sh_client_id = client_id
        self.config.sh_client_secret = client_secret

    def _search_catalog(self, aoi_bbox, time_interval) -> SearchResult:
        catalog = SentinelHubCatalog(config=self.config)

        search_iterator = catalog.search(
            DataCollection.SENTINEL2_L2A,  # https://sentiwiki.copernicus.eu/web/s2-applications
            bbox=aoi_bbox,
            time=time_interval,
            fields={
                "include": [
                    "id",
                    "properties.datetime",
                    # "properties.proj:geometry",
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
        aoi_coords,
        time_interval,
        output_type,
        output_format,
    ) -> None:
        aoi_bbox = BBox(bbox=aoi_coords, crs=CRS.WGS84)
        search_results = self._search_catalog(aoi_bbox, time_interval)
        best_result = min(search_results)
        result_bbox = BBox(bbox=best_result.bbox, crs=CRS.WGS84)

        if output_type == "visual":
            eval_script = EvalScripts.VISUAL.value
        if output_type == "ndvi":
            eval_script = EvalScripts.NDVI.value
        if output_format == "png":
            response_format = MimeType.PNG
        if output_format == "tiff":
            response_format = MimeType.TIFF

        request_img = SentinelHubRequest(
            evalscript=eval_script,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=time_interval,
                    other_args={"dataFilter": {"mosaickingOrder": "leastCC"}},
                )
            ],
            responses=[
                SentinelHubRequest.output_response(
                    "default",
                    response_format=response_format,
                )
            ],
            bbox=result_bbox,
            size=(250, 250),  # TODO: change to max resolution (2500x2500)
            # size=bbox_to_dimensions(
            #     result_bbox,
            #     resolution=1,
            # ),  # TODO: how to get the best resolution?
            # resolution=1,
            config=self.config,
            data_folder="data/",
        )

        request_img.get_data(save_data=True, show_progress=True)


if __name__ == "__main__":
    adapter = SentinelHubAdapter(
        os.environ.get("CLIENT_ID"),
        os.environ.get("CLIENT_SECRET"),
    )
    adapter.request_image(
        aoi_coords=[16.461282, 46.757161, 16.574922, 46.851514],
        time_interval=("2022-05-01", "2022-05-20"),
        output_type="ndvi",
        output_format="png",
    )
