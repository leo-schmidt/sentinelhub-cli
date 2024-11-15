from pydantic import ValidationError
from utils.models import SearchResult
from utils.input_validation import AreaOfInterest, TimeOfInterest
import unittest
import pytest


class TestSearchResult(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        results = [
            {
                "id": "S2B_MSIL2A_1",
                "bbox": [14.0, 45.0, 16.0, 47.0],
                "properties": {
                    "datetime": "2022-05-20T10:07:48Z",
                    "eo:cloud_cover": 7.00,
                },
            },
            {
                "id": "S2B_MSIL2A_2",
                "bbox": [14.0, 45.0, 16.0, 47.0],
                "properties": {
                    "datetime": "2022-05-21T10:07:48Z",
                    "eo:cloud_cover": 12.00,
                },
            },
            {
                "id": "S2B_MSIL2A_3",
                "bbox": [14.0, 45.0, 16.0, 47.0],
                "properties": {
                    "datetime": "2022-05-22T10:07:48Z",
                    "eo:cloud_cover": 0.30,
                },
            },
        ]
        self.search_results = [SearchResult.model_validate(r) for r in results]

    def test_greater_than(self):
        best_result = min(self.search_results)
        self.assertEqual(best_result, self.search_results[2])


class TestAreaOfInterest(unittest.TestCase):
    def test_correct_aoi(self):
        aoi = "14.0,45.0,16.0,47.0"
        aoi = tuple(aoi.split(","))
        assert AreaOfInterest(coords=aoi)

    def test_wrong_longitude(self):
        aoi = "200.0,45.0,16.0,47.0"
        aoi = tuple(aoi.split(","))
        self.assertRaises(ValidationError, AreaOfInterest, coords=aoi)

    def test_wrong_latitude(self):
        aoi = "14.0,45.0,16.0,-100.0"
        aoi = tuple(aoi.split(","))
        self.assertRaises(ValidationError, AreaOfInterest, coords=aoi)


class TestTimeOfInterest(unittest.TestCase):
    def test_correct_toi(self):
        toi = "2024-01-01,2024-02-01"
        toi = tuple(toi.split(","))
        assert TimeOfInterest(times=toi)

    def test_wrong_toi(self):
        toi = "2024-01-01,test"
        toi = tuple(toi.split(","))
        self.assertRaises(ValidationError, TimeOfInterest, times=toi)
