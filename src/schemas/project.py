from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, root_validator, validator
from sqlmodel import SQLModel
from src.core.config import settings
from src.db.models._base_class import DateTimeBase
from src.db.models.layer import ContentBaseAttributes, internal_layer_table_name
from src.schemas.layer import (
    CQLQuery,
    IExternalImageryRead,
    IExternalVectorTileRead,
    IFeatureScenarioRead,
    IFeatureStandardRead,
    IFeatureToolRead,
    ITableRead,
    LayerOtherProperties,
    LayerProperties,
    LayerType,
)
from src.utils import build_where, optional


################################################################################
# Project DTOs
################################################################################
class ProjectContentType(str, Enum):
    layer = "layer"
    report = "report"


class InitialViewState(BaseModel):
    latitude: float = Field(..., description="Latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude", ge=-180, le=180)
    zoom: int = Field(..., description="Zoom level", ge=0, le=20)
    min_zoom: int = Field(..., description="Minimum zoom level", ge=0, le=20)
    max_zoom: int = Field(..., description="Maximum zoom level", ge=0, le=20)
    bearing: int = Field(..., description="Bearing", ge=0, le=360)
    pitch: int = Field(..., description="Pitch", ge=0, le=60)

    @validator("max_zoom")
    def check_max_zoom(cls, max_zoom, values):
        min_zoom = values.get("min_zoom")
        if min_zoom is not None and max_zoom < min_zoom:
            raise ValueError("max_zoom should be greater than or equal to min_zoom")
        return max_zoom

    @validator("min_zoom")
    def check_min_zoom(cls, min_zoom, values):
        max_zoom = values.get("max_zoom")
        if max_zoom is not None and min_zoom > max_zoom:
            raise ValueError("min_zoom should be less than or equal to max_zoom")
        return min_zoom


initial_view_state_example = {
    "latitude": 48.1502132,
    "longitude": 11.5696284,
    "zoom": 12,
    "min_zoom": 0,
    "max_zoom": 20,
    "bearing": 0,
    "pitch": 0,
}


class IProjectCreate(ContentBaseAttributes):
    initial_view_state: InitialViewState = Field(
        ..., description="Initial view state of the project"
    )

class IProjectRead(ContentBaseAttributes, DateTimeBase):
    id: UUID = Field(..., description="Project ID")
    layer_order: list[int] | None = Field(None, description="Layer order in project")


@optional
class IProjectBaseUpdate(ContentBaseAttributes):
    layer_order: list[int] | None = Field(None, description="Layer order in project")


class LayerProjectProperties(LayerProperties):
    layout: dict = Field(
        {"visibility": "visible"},
        description="Layout properties",
    )
    minzoom: int = Field(2, description="Minimum zoom level", ge=0, le=22)
    maxzoom: int = Field(20, description="Maximum zoom level", ge=0, le=22)


class LayerProjectIds(BaseModel):
    id: int = Field(..., description="Layer Project ID")
    layer_id: UUID = Field(..., description="Layer ID")


class IFeatureBaseProject(CQLQuery):
    name: str = Field(..., description="Layer name")
    group: str | None = Field(None, description="Layer group name")
    properties: LayerProjectProperties = Field(
        ...,
        description="Layer properties",
    )

class IFeatureBaseProjectRead(IFeatureBaseProject):
    total_count: int | None = Field(None, description="Total count of features in the layer")
    filtered_count: int | None = Field(
        None, description="Filtered count of features in the layer"
    )
    @property
    def table_name(self):
        return internal_layer_table_name(self)
    @property
    def where_query(self):
        return where_query(self)

def where_query(values: SQLModel | BaseModel):
    table_name = internal_layer_table_name(values)
    # Check if query exists then build where query
    if values.query:
        return build_where(id=values.layer_id, table_name=table_name, query=values.query, attribute_mapping=values.attribute_mapping)
    return None

class IFeatureStandardProjectRead(
    LayerProjectIds, IFeatureStandardRead, IFeatureBaseProjectRead
):
    pass


class IFeatureToolProjectRead(
    LayerProjectIds, IFeatureToolRead, IFeatureBaseProjectRead
):
    pass


class IFeatureScenarioProjectRead(
    LayerProjectIds, IFeatureScenarioRead, IFeatureBaseProjectRead
):
    pass


@optional
class IFeatureStandardProjectUpdate(IFeatureBaseProject):
    pass


@optional
class IFeatureToolProjectUpdate(IFeatureBaseProject):
    pass


@optional
class IFeatureScenarioProjectUpdate(IFeatureBaseProject):
    pass


class ITableProjectRead(LayerProjectIds, ITableRead, CQLQuery):
    group: str = Field(None, description="Layer group name")
    total_count: int | None = Field(None, description="Total count of features in the layer")
    filtered_count: int | None = Field(
        None, description="Filtered count of features in the layer"
    )
    table_name: str | None = Field(None, description="Table name")
    where_query: str | None = Field(None, description="Where query")
    # Compute table_name and where_query
    @property
    def table_name(self):
        return internal_layer_table_name(self)
    @property
    def where_query(self):
        return where_query(self)



@optional
class ITableProjectUpdate(CQLQuery):
    name: str | None = Field(None, description="Layer name")
    group: str | None = Field(None, description="Layer group name")


class IExternalVectorTileProjectRead(LayerProjectIds, IExternalVectorTileRead):
    group: str = Field(None, description="Layer group name")
    properties: LayerProjectProperties = Field(
        ...,
        description="Layer properties",
    )


@optional
class IExternalVectorTileProjectUpdate(BaseModel):
    name: str | None = Field(None, description="Layer name")
    group: str | None = Field(None, description="Layer group name")
    properties: LayerProjectProperties | None = Field(
        None,
        description="Layer properties",
    )


class IExternalImageryProjectRead(LayerProjectIds, IExternalImageryRead):
    group: str = Field(None, description="Layer group name")
    properties: LayerProjectProperties = Field(
        ...,
        description="Layer properties",
    )
    other_properties: LayerOtherProperties = Field(
        ...,
        description="Other properties of the layer",
    )


@optional
class IExternalImageryProjectUpdate(BaseModel):
    name: str | None = Field(None, description="Layer name")
    group: str | None = Field(None, description="Layer group name")
    properties: LayerProjectProperties | None = Field(
        None,
        description="Layer properties",
    )
    other_properties: LayerOtherProperties | None = Field(
        None,
        description="Other properties of the layer",
    )


layer_type_mapping_read = {
    "feature_standard": IFeatureStandardProjectRead,
    "feature_tool": IFeatureToolProjectRead,
    "feature_scenario": IFeatureScenarioProjectRead,
    "table": ITableProjectRead,
    "external_vector_tile": IExternalVectorTileProjectRead,
    "external_imagery": IExternalImageryProjectRead,
}

layer_type_mapping_update = {
    "feature_standard": IFeatureStandardProjectUpdate,
    "feature_tool": IFeatureToolProjectUpdate,
    "feature_scenario": IFeatureScenarioProjectUpdate,
    "table": ITableProjectUpdate,
    "external_vector_tile": IExternalVectorTileProjectUpdate,
    "external_imagery": IExternalImageryProjectUpdate,
}

request_examples = {
    "get": {
        "ids": [
            "39e16c27-2b03-498e-8ccc-68e798c64b8d",
            "e7dcaae4-1750-49b7-89a5-9510bf2761ad",
        ],
    },
    "create": {
        "folder_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d",
        "name": "Project 1",
        "description": "Project 1 description",
        "tags": ["tag1", "tag2"],
        "thumbnail_url": "https://goat-app-assets.s3.eu-central-1.amazonaws.com/logos/goat_green.png",
        "initial_view_state": initial_view_state_example,
    },
    "update": {
        "folder_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d",
        "name": "Project 2",
        "description": "Project 2 description",
        "tags": ["tag1", "tag2"],
        "thumbnail_url": "https://goat-app-assets.s3.eu-central-1.amazonaws.com/logos/goat_green.png",
    },
    "initial_view_state": initial_view_state_example,
    "update_layer": {
        "feature_standard": {
            "summary": "Feature Layer Standard",
            "value": {
                "name": "Feature Layer Standard",
                "group": "Group 1",
                "query": {"op": "=", "args": [{"property": "category"}, "bus_stop"]},
                "properties": {
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "#ff0000",
                    },
                    "layout": {"visibility": "visible"},
                    "minzoom": 0,
                    "maxzoom": 22,
                },
            },
        },
        "feature_tool": {
            "summary": "Feature Layer Tool",
            "value": {
                "name": "Feature Layer Tool",
                "group": "Group 1",
                "properties": {
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "#ff0000",
                    },
                    "layout": {"visibility": "visible"},
                    "minzoom": 0,
                    "maxzoom": 22,
                },
            },
        },
        "feature_scenario": {
            "summary": "Feature Layer Scenario",
            "value": {
                "name": "Feature Layer Scenario",
                "group": "Group 1",
                "properties": {
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "#ff0000",
                    },
                    "layout": {"visibility": "visible"},
                    "minzoom": 0,
                    "maxzoom": 22,
                },
            },
        },
        "table": {
            "summary": "Table Layer",
            "value": {
                "name": "Table Layer",
                "group": "Group 1",
            },
        },
        "external_vector_tile": {
            "summary": "VectorVectorTile Layer",
            "value": {
                "name": "VectorVectorTile Layer",
                "group": "Group 1",
            },
        },
        "external_imagery": {
            "summary": "Imagery Layer",
            "value": {
                "name": "Imagery Layer",
                "group": "Group 1",
            },
        },
    },
}
