# Standard library imports
from enum import Enum
from typing import List
from uuid import UUID, uuid4

# Third party imports
from pydantic import BaseModel, Field, HttpUrl, ValidationError, validator
from pyproj import CRS
from pyproj.exceptions import CRSError

# Local application imports
from src.db.models._base_class import DateTimeBase, content_base_example
from src.db.models.layer import (
    ExternalImageryDataType,
    ExternalVectorTileDataType,
    FeatureGeometryType,
    FeatureLayerExportType,
    FeatureType,
    GeospatialAttributes,
    LayerBase,
    LayerType,
    ScenarioType,
    TableLayerExportType,
    ToolType,
    layer_base_example,
)
from src.schemas.common import CQLQuery
from src.schemas.job import Msg
from src.utils import optional


class MaxFileSizeType(int, Enum):
    """Max file size types in bytes."""

    geojson = 300000000
    csv = 100000000
    xlsx = 100000000
    gpkg = 300000000
    kml = 300000000
    zip = 300000000


class SupportedOgrGeomType(Enum):
    Point = "point"
    Multi_Point = "point"
    Line_String = "line"
    Multi_Line_String = "line"
    Polygon = "polygon"
    Multi_Polygon = "polygon"


class UserDataGeomType(Enum):
    point = "point"
    line = "line"
    polygon = "polygon"
    no_geometry = "no_geometry"


class OgrPostgresType(str, Enum):
    Integer = "integer"
    Integer64 = "bigint"
    Real = "float"
    String = "text"
    Date = "timestamp"
    Time = "timestamp"
    DateTime = "timestamp"


class OgrDriverType(str, Enum):
    """OGR driver types."""

    geojson = "GeoJSON"
    csv = "CSV"  # Using XLSX driver for CSV files as the file is converted to XLSX to keep data types
    xlsx = "XLSX"
    gpkg = "GPKG"
    kml = "KML"
    shp = "ESRI Shapefile"  # Using SHP driver for ZIP files as the file is converted to SHP to keep data types
    zip = "ESRI Shapefile"  # Using SHP driver for ZIP files as the file is converted to SHP to keep data types


class NumberColumnsPerType(int, Enum):
    """Number of columns per type."""

    integer = 25
    bigint = 5
    float = 25
    text = 25
    timestamp = 3
    arrfloat = 3
    arrint = 3
    arrtext = 3
    jsonb = 10
    boolean = 10


class IFileUploadMetadata(BaseModel):
    data_types: dict = Field(..., description="Data types of the columns")
    layer_type: LayerType = Field(..., description="Layer type")
    file_ending: str = Field(..., description="File ending", max_length=500)
    file_size: int = Field(..., description="File size")
    file_path: str = Field(..., description="File path", max_length=500)
    dataset_id: UUID = Field(..., description="Dataset ID")
    msg: Msg = Field(..., description="Response Message")


class ComputeBreakOperation(Enum):
    """Allowed operations on numeric columns."""

    quantile = "quantile"
    standard_deviation = "standard_deviation"
    equal_interval = "equal_interval"
    heads_and_tails = "heads_and_tails"


class AreaStatisticsOperation(Enum):
    """Allowed operations on polygon geometries."""

    sum = "sum"
    mean = "mean"
    min = "min"
    max = "max"


class UserDataTable(str, Enum):
    """Created user tables"""

    point = "point"
    line = "line"
    polygon = "polygon"
    no_geometry = "no_geometry"


class LayerReadBaseAttributes(BaseModel):
    id: UUID = Field(..., description="Content ID of the layer", alias="id")
    user_id: UUID = Field(..., description="User ID of the owner")
    type: LayerType = Field(..., description="Layer type")


class LayerProperties(BaseModel):
    """Base model for layer properties."""

    type: str = Field(..., description="Mapbox style type", max_length=500)
    paint: dict = Field(..., description="Paint of the mapbox style of the layer")


################################################################################
# Feature Layer DTOs
################################################################################


class FeatureReadBaseAttributes(
    LayerReadBaseAttributes, LayerBase, GeospatialAttributes
):
    """Base model for feature layer reads."""

    feature_layer_type: "FeatureType" = Field(..., description="Feature layer type")
    feature_layer_geometry_type: "FeatureGeometryType" = Field(
        ..., description="Feature layer geometry type"
    )
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")
    size: int = Field(..., description="Size of the layer in bytes")
    properties: dict = Field(..., description="Layer properties.")


class FeatureUpdateBase(LayerBase, GeospatialAttributes):
    """Base model for feature layer updates."""

    properties: dict | None = Field(None, description="Layer properties.")


feature_layer_update_base_example = {
    "properties": [
        "match",
        ["get", "category"],
        ["forest"],
        "hsl(137, 37%, 30%)",
        ["park"],
        "hsl(135, 100%, 100%)",
        "#000000",
    ],
    "size": 1000,
}


# Feature Layer Standard
class IInternalLayerCreate(LayerBase):
    id: UUID = Field(
        default_factory=uuid4, description="Content ID of the layer", alias="id"
    )
    dataset_id: UUID = Field(..., description="Dataset ID")


class IFeatureLayerToolCreate(BaseModel):
    id: UUID = Field(
        default_factory=uuid4, description="Content ID of the layer", alias="id"
    )
    name: str = Field(..., description="Layer name", max_length=500)
    feature_layer_geometry_type: FeatureGeometryType = Field(
        ..., description="Feature layer geometry type"
    )
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")
    tool_type: ToolType = Field(..., description="Tool type")
    job_id: UUID = Field(..., description="Job ID")


class IFeatureStandardCreateAdditionalAttributes(BaseModel):
    """Model for second internal validation with extended attributes."""

    user_id: UUID = Field(..., description="User ID of the owner")
    type: LayerType = Field(..., description="Layer type")
    feature_layer_type: FeatureType = Field(..., description="Feature layer type")
    feature_layer_geometry_type: FeatureGeometryType = Field(
        ..., description="Feature layer geometry type"
    )
    properties: dict = Field(..., description="Layer properties.")
    extent: str = Field(
        ..., description="Geographical Extent of the layer", max_length=500
    )
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")


class IFeatureStandardRead(FeatureReadBaseAttributes, DateTimeBase):
    pass


@optional
class IFeatureStandardUpdate(FeatureUpdateBase):
    pass


# Feature Layer Tool
class FeatureToolAttributesBase(BaseModel):
    """Base model for additional attributes feature layer tool."""

    tool_type: ToolType = Field(..., description="Tool type")


feature_layer_tool_attributes_example = {
    "tool_type": "isochrone",
}


class IFeatureToolCreate(LayerBase, FeatureToolAttributesBase):
    """Model to create feature layer tool."""

    pass


class IFeatureToolRead(
    FeatureReadBaseAttributes, FeatureToolAttributesBase, DateTimeBase
):
    """Model to read a feature layer tool."""

    pass


@optional
class IFeatureToolUpdate(FeatureUpdateBase):
    """Model to update a feature layer tool."""

    pass


# Feature Layer Scenario
class FeatureScenarioAttributesBase(BaseModel):
    """Base model for additional attributes feature layer scenario."""

    scenario_id: UUID = Field(..., description="Scenario ID of the scenario layer.")
    scenario_type: ScenarioType = Field(..., description="Scenario type")


feature_layer_scenario_attributes_example = {
    "scenario_id": "60a42459-11c8-4cd7-91f1-091d0e05a4a3",
    "scenario_type": "point",
}


class IFeatureScenarioCreate(LayerBase, FeatureScenarioAttributesBase):
    """Model to create feature layer scenario."""

    pass


class IFeatureScenarioRead(
    FeatureReadBaseAttributes, FeatureScenarioAttributesBase, DateTimeBase
):
    """Model to read a feature layer scenario."""

    pass


@optional
class IFeatureScenarioUpdate(FeatureUpdateBase):
    """Model to update a feature layer scenario."""

    pass


################################################################################
# Imagery Layer DTOs
################################################################################


class LayerOtherProperties(BaseModel):
    """Model for external imagery layer properties."""

    layers: List[str] = Field(..., description="List of layers to be displayed")
    width: int = Field(..., description="Width of the WMS image")
    height: int = Field(..., description="Height of the WMS image")
    srs: str = Field(..., description="SRS of the WMS image", max_length=50)
    legend_urls: List[HttpUrl] | None = Field(None, description="Layer legend URLs")


class ExternalImageryAttributesBase(BaseModel):
    """Base model for additional attributes imagery layer."""

    url: HttpUrl = Field(..., description="Layer URL")
    data_type: ExternalImageryDataType = Field(..., description="Content data type")
    properties: dict = Field(..., description="Layer properties.")
    other_properties: LayerOtherProperties = Field(
        ..., description="Additional layer properties."
    )


imagery_layer_attributes_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetCapabilities&service=WMS",
    "data_type": "wms",
    "properties": {
        "type": "raster",
        "paint": {"raster-opacity": 1},
    },
    "other_properties": {
        "layers": ["Actueel_ortho25"],
        "width": 256,
        "height": 256,
        "srs": "EPSG:3857",
        "legend_urls": [
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
        ],
    },
}


class IExternalImageryCreate(
    LayerBase, GeospatialAttributes, ExternalImageryAttributesBase
):
    """Model to create a imagery layer."""

    type: LayerType = Field(..., description="Layer type")


class IExternalImageryRead(
    LayerReadBaseAttributes,
    LayerBase,
    GeospatialAttributes,
    ExternalImageryAttributesBase,
    DateTimeBase,
):
    """Model to read a imagery layer."""

    pass


@optional
class IExternalImageryUpdate(LayerBase, GeospatialAttributes):
    """Model to update a imagery layer."""

    url: HttpUrl | None = Field(None, description="Layer URL")
    properties: dict | None = Field(None, description="Layer properties.")
    other_properties: LayerOtherProperties | None = Field(
        None, description="Additional layer properties."
    )


imagery_layer_update_base_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetCapabilities&service=WMS",
    "properties": {
        "type": "raster",
        "paint": {"raster-opacity": 0.5},
        "layers": ["Actueel_ortho25"],
        "width": 256,
        "height": 256,
        "srs": "EPSG:3857",
        "legend_urls": [
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
        ],
    },
}

################################################################################
# VectorTile Layer DTOs
################################################################################


class ExternalVectorTileAttributesBase(BaseModel):
    """Base model for additional attributes tile layer."""

    url: HttpUrl = Field(..., description="Layer URL")
    data_type: ExternalVectorTileDataType = Field(..., description="Content data type")
    properties: dict | None = Field(None, description="Layer properties.")


tile_layer_attributes_example = {
    "url": "https://goat.plan4better.de/api/v1/layers/tiles/accidents_pedestrians/12/2179/1420.pbf",
    "data_type": "mvt",
    "properties": {
        "type": "fill",
        "paint": {"fill-color": "#00ffff"},
    },
}


class IExternalVectorTileCreate(
    LayerBase, GeospatialAttributes, ExternalVectorTileAttributesBase
):
    """Model to create a tile layer."""

    type: LayerType = Field(..., description="Layer type")


class IExternalVectorTileRead(
    LayerReadBaseAttributes,
    LayerBase,
    GeospatialAttributes,
    ExternalVectorTileAttributesBase,
    DateTimeBase,
):
    """Model to read a tile layer."""

    pass


@optional
class IExternalVectorTileUpdate(LayerBase, GeospatialAttributes):
    """Model to update a tile layer."""

    url: HttpUrl | None = Field(None, description="Layer URL")


tile_layer_update_example = {
    "url": "https://goat.plan4better.de/api/v1/layers/tiles/accidents_pedestrians/12/2179/1420.pbf",
    "properties": {
        "type": "fill",
        "paint": {"fill-color": "#ff0000"},
    },
}

################################################################################
# Table Layer DTOs
################################################################################


class ITableCreateAdditionalAttributes(BaseModel):
    """Model for second internal validation with extended attributes."""

    user_id: UUID = Field(..., description="User ID of the owner")
    type: LayerType = Field(..., description="Layer type")
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")


class ITableRead(LayerBase, LayerReadBaseAttributes, DateTimeBase):
    """Model to read a table layer."""

    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")


@optional
class ITableUpdate(LayerBase):
    """Model to update a table layer."""

    pass


def get_layer_class(class_type: str, layer_creator_class: dict, **kwargs):
    try:
        layer_type = kwargs["type"]
    except KeyError:
        raise ValidationError("Layer type is required")

    layer_class = layer_creator_class[layer_type]
    if layer_type == "feature":
        try:
            feature_layer_type = kwargs["feature_layer_type"]
        except KeyError:
            raise ValidationError("Feature layer type is required")

        layer_class = layer_class[feature_layer_type]

    layer_class_name = layer_class.__name__
    if class_type == "create":
        layer_class_name = layer_class_name.replace("Read", "Create")
    elif class_type == "update":
        layer_class_name = layer_class_name.replace("Read", "Update")
    elif class_type == "read":
        pass
    else:
        raise ValueError(f"Layer class type ({class_type}) is invalid")

    return globals()[layer_class_name]


layer_creator_class = {
    "internal": {
        "table": ITableRead,
        "feature": {
            "standard": IFeatureStandardRead,
            "tool": IFeatureToolRead,
            "scenario": IFeatureScenarioRead,
        },
    },
    "external": {
        "external_imagery": IExternalImageryRead,
        "external_vector_tile": IExternalVectorTileRead,
    },
}


layer_update_class = {
    "internal": {
        "table": ITableUpdate,
        "feature": {
            "standard": IFeatureStandardUpdate,
            "tool": IFeatureToolUpdate,
            "scenario": IFeatureScenarioUpdate,
        },
    },
    "external": {
        "external_imagery": IExternalImageryUpdate,
        "external_vector_tile": IExternalVectorTileUpdate,
    },
}


# Write function to get the correct class
def get_layer_schema(
    class_mapping: dict, layer_type: LayerType, feature_layer_type: FeatureType = None
):
    # Check if layer is external
    if layer_type in class_mapping["external"]:
        return class_mapping["external"][layer_type]
    # Check if layer is internal
    elif layer_type in class_mapping["internal"]:
        # Check if layer is feature
        if feature_layer_type:
            return class_mapping["internal"][layer_type][feature_layer_type]
        else:
            return class_mapping["internal"][layer_type]
    else:
        raise ValueError(f"Layer type ({layer_type}) is invalid")


class ILayerExternalCreate(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_create_class = get_layer_class(
            "create", layer_creator_class["external"], **kwargs
        )
        return layer_create_class(**kwargs)


class ILayerRead(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_read_class = get_layer_class(
            "read",
            {**layer_creator_class["internal"], **layer_creator_class["external"]},
            **kwargs,
        )
        return layer_read_class(**kwargs)


class ILayerUpdate(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_update_class = get_layer_class(
            "update",
            {**layer_creator_class["internal"], **layer_creator_class["external"]},
            **kwargs,
        )
        return layer_update_class(**kwargs)


class IUniqueValue(BaseModel):
    """Model for unique values."""

    value: str = Field(..., description="Unique value")
    count: int = Field(..., description="Number of occurrences")


class IValidateJobId(BaseModel):
    """Model to import a file object."""

    validate_job_id: UUID = Field(..., description="Upload job ID")


class IInternalLayerExport(CQLQuery):
    """Layer export input schema."""

    id: UUID = Field(..., description="Layer ID")
    file_type: FeatureLayerExportType | TableLayerExportType = Field(
        ..., description="File type"
    )
    file_name: str = Field(
        ..., description="File name of the exported file.", max_length=500
    )
    crs: str | None = Field(
        None, description="CRS of the exported file.", max_length=20
    )

    # Check if crs is valid
    @validator("crs")
    def validate_crs(cls, crs):
        # Validate the provided CRS
        try:
            CRS(crs)
        except CRSError as e:
            raise ValidationError(f"Invalid CRS: {e}")
        return crs

    # Check that projection is EPSG:4326 for KML
    @validator("crs")
    def validate_crs_kml(cls, crs, values):
        if values["file_type"] == FeatureLayerExportType.kml:
            if crs != "EPSG:4326":
                raise ValidationError("KML export only supports EPSG:4326 projection.")
        return crs


request_examples = {
    "get": {
        "ids": [
            "e7dcaae4-1750-49b7-89a5-9510bf2761ad",
            "e7dcaae4-1750-49b7-89a5-9510bf2761ad",
        ],
    },
    "create_internal": {
        "table": {
            "summary": "Table Layer",
            "value": {
                "dataset_id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                **content_base_example,
                **layer_base_example,
            },
        },
        "feature_layer_standard": {
            "summary": "Layer Standard",
            "value": {
                "dataset_id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                **content_base_example,
                **layer_base_example,
            },
        },
    },
    "export_internal": {
        "table": {
            "summary": "Table Layer",
            "value": {
                "id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                "file_type": "csv",
                "file_name": "test",
                "crs": "EPSG:3857",
                "query": {"op": "=", "args": [{"property": "category"}, "bus_stop"]},
            },
        },
        "feature_layer_standard": {
            "summary": "Layer Standard",
            "value": {
                "id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                "file_type": "csv",
                "file_name": "test",
            },
        },
    },
    "create_external": {
        "external_imagery": {
            "summary": "Imagery Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                **imagery_layer_attributes_example,
                "type": "external_imagery",
                "extent": "MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))",
            },
        },
        "external_vector_tile": {
            "summary": "VectorTile Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                **tile_layer_attributes_example,
                "type": "external_vector_tile",
                "extent": "MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))",
            },
        },
    },
    "update": {
        "table": {
            "summary": "Table Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
            },
        },
    },
}
