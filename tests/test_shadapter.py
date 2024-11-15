from shadapter import SentinelHubAdapter
import unittest
import pytest


class TestSHAdapter(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.adapter = SentinelHubAdapter("", "")

    def test_request_image_bbox(self):
        with self.assertRaises(ValueError) as ctx:
            self.adapter.request_image(
                aoi_coords=(12, 46, 13, 46.1),
                time_interval=("2024-01-01", "2024-01-01"),
            )
        self.assertTrue("Requested image width is too large." in str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.adapter.request_image(
                aoi_coords=(12, 46, 12.1, 47),
                time_interval=("2024-01-01", "2024-01-01"),
            )
        self.assertTrue("Requested image height is too large." in str(ctx.exception))

    def test_request_image_output_type(self):
        with self.assertRaises(ValueError) as ctx:
            self.adapter.request_image(
                aoi_coords=(12, 46, 12.1, 46.1),
                time_interval=("2024-01-01", "2024-01-01"),
                output_type="test",
            )
        self.assertTrue(
            """Output type not one of ("visual", "ndvi")""" in str(ctx.exception)
        )
