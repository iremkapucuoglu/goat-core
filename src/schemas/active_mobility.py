from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, validator

from src.schemas.layer import ToolType
from src.schemas.toolbox_base import IsochroneStartingPointsBase, check_starting_points, input_layer_type_point
from src.schemas.colors import ColorRangeType

class IsochroneStartingPointsActiveMobility(IsochroneStartingPointsBase):
    """Model for the active mobility isochrone starting points."""

    # Check that the starting points for active mobility are below 1000
    check_starting_points = check_starting_points(1000)


class RoutingActiveMobilityType(str, Enum):
    """Routing active mobility type schema."""

    walking = "walking"
    bicycle = "bicycle"
    pedelec = "pedelec"


class TravelTimeCostActiveMobility(BaseModel):
    """Travel time cost schema."""

    max_traveltime: int = Field(
        ...,
        title="Max Travel Time",
        description="The maximum travel time in minutes.",
        ge=1,
        le=45,
    )
    steps: int = Field(
        ...,
        title="Steps",
        description="The number of steps.",
    )
    speed: int = Field(
        ...,
        title="Speed",
        description="The speed in km/h.",
        ge=1,
        le=25,
    )

    # Ensure the number of steps doesn't exceed the maximum traveltime
    @validator("steps", pre=True, always=True)
    def valid_num_steps(cls, v):
        if v > 45:
            raise ValueError(
                "The number of steps must not exceed the maximum traveltime."
            )
        return v


# TODO: Check how to treat miles
class TravelDistanceCostActiveMobility(BaseModel):
    """Travel distance cost schema."""

    max_distance: int = Field(
        ...,
        title="Max Distance",
        description="The maximum distance in meters.",
        ge=50,
        le=20000,
    )
    steps: int = Field(
        ...,
        title="Steps",
        description="The number of steps.",
    )

    # Ensure the number of steps doesn't exceed the maximum distance
    @validator("steps", pre=True, always=True)
    def valid_num_steps(cls, v):
        if v > 20000:
            raise ValueError(
                "The number of steps must not exceed the maximum distance."
            )
        return v


class IsochroneType(str, Enum):
    """Isochrone type schema."""

    polygon = "polygon"
    network = "network"
    rectangular_grid = "rectangular_grid"


class IIsochroneActiveMobility(BaseModel):
    """Model for the active mobility isochrone"""

    starting_points: IsochroneStartingPointsActiveMobility = Field(
        ...,
        title="Starting Points",
        description="The starting points of the isochrone.",
    )
    routing_type: RoutingActiveMobilityType = Field(
        ...,
        title="Routing Type",
        description="The routing type of the isochrone.",
    )
    travel_cost: TravelTimeCostActiveMobility | TravelDistanceCostActiveMobility = (
        Field(
            ...,
            title="Travel Cost",
            description="The travel cost of the isochrone.",
        )
    )
    scenario_id: UUID | None = Field(
        None,
        title="Scenario ID",
        description="The ID of the scenario that is used for the routing.",
    )
    isochrone_type: IsochroneType = Field(
        ...,
        title="Return Type",
        description="The return type of the isochrone.",
    )
    polygon_difference: bool | None = Field(
        None,
        title="Polygon Difference",
        description="If true, the polygons returned will be the geometrical difference of two following calculations.",
    )

    @property
    def tool_type(self):
        return ToolType.isochrone_active_mobility

    @property
    def geofence_table(self):
        mode = ToolType.isochrone_active_mobility.value.replace("isochrone_", "")
        return f"basic.geofence_{mode}"

    @property
    def input_layer_types(self):
        return {"layer_project_id": input_layer_type_point}
    
    @property
    def properties_base(self):
        return {
            "color_range_type": ColorRangeType.sequential,
            "color_field": {"name": "travel_cost", "type": "number"},
            "color_scale": "quantile",
            "breaks": self.travel_cost.steps,
        }



request_examples = {
    "isochrone_active_mobility": {
        "single_point_walking": {
            "summary": "Single point isochrone walking",
            "value": {
                "starting_points": {"latitude": [52.5200], "longitude": [13.4050]},
                "routing_type": "walking",
                "travel_cost": {
                    "max_traveltime": 30,
                    "steps": 10,
                    "speed": 5,
                },
                "isochrone_type": "polygon",
                "polygon_difference": True,
            },
        },
        "single_point_cycling": {
            "summary": "Single point isochrone cycling",
            "value": {
                "starting_points": {"latitude": [52.5200], "longitude": [13.4050]},
                "routing_type": "bicycle",
                "travel_cost": {
                    "max_traveltime": 15,
                    "steps": 5,
                    "speed": 15,
                },
                "isochrone_type": "polygon",
                "polygon_difference": True,
            },
        },
        "single_point_walking_scenario": {
            "summary": "Single point isochrone walking",
            "value": {
                "starting_points": {"latitude": [52.5200], "longitude": [13.4050]},
                "routing_type": "walking",
                "travel_cost": {
                    "max_traveltime": 30,
                    "steps": 10,
                    "speed": 5,
                },
                "scenario_id": "e7dcaae4-1750-49b7-89a5-9510bf2761ad",
                "isochrone_type": "polygon",
                "polygon_difference": True,
            },
        },
        "multi_point_walking": {
            "summary": "Multi point isochrone walking",
            "value": {
                "starting_points": {
                    "latitude": [
                        52.5200,
                        52.5210,
                        52.5220,
                        52.5230,
                        52.5240,
                        52.5250,
                        52.5260,
                        52.5270,
                        52.5280,
                        52.5290,
                    ],
                    "longitude": [
                        13.4050,
                        13.4060,
                        13.4070,
                        13.4080,
                        13.4090,
                        13.4100,
                        13.4110,
                        13.4120,
                        13.4130,
                        13.4140,
                    ],
                },
                "routing_type": "walking",
                "travel_cost": {
                    "max_traveltime": 30,
                    "steps": 10,
                    "speed": 5,
                },
            },
        },
        "multi_point_cycling": {
            "summary": "Multi point isochrone cycling",
            "value": {
                "starting_points": {
                    "latitude": [
                        52.5200,
                        52.5210,
                        52.5220,
                        52.5230,
                        52.5240,
                        52.5250,
                        52.5260,
                        52.5270,
                        52.5280,
                        52.5290,
                    ],
                    "longitude": [
                        13.4050,
                        13.4060,
                        13.4070,
                        13.4080,
                        13.4090,
                        13.4100,
                        13.4110,
                        13.4120,
                        13.4130,
                        13.4140,
                    ],
                },
                "routing_type": "bicycle",
                "travel_cost": {
                    "max_traveltime": 15,
                    "steps": 5,
                    "speed": 15,
                },
            },
        },
        "layer_based_walking": {
            "summary": "Layer based isochrone walking",
            "value": {
                "starting_points": {
                    "layer_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d"  # Sample UUID for the layer
                },
                "routing_type": "walking",
                "travel_cost": {
                    "max_traveltime": 30,
                    "steps": 10,
                    "speed": 5,
                },
            },
        },
    }
}
