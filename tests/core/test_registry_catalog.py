# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from detime.registry import MethodRegistry
from detime.schemas import MethodMetadataModel, MethodRegistryPayloadModel


REQUIRED_FIELDS = {
    "family",
    "maturity",
    "claim_scope",
    "implementation",
    "dependency_tier",
    "multivariate_support",
    "native_backed",
    "min_length",
    "summary",
    "recommended_for",
    "typical_failure_modes",
    "references",
    "package_links",
    "parameter_docs",
    "output_components",
    "example_config",
}


def test_registry_catalog_contract_is_complete() -> None:
    catalog = MethodRegistry.list_catalog()
    assert catalog

    for entry in catalog:
        assert REQUIRED_FIELDS.issubset(entry.keys())
        validated = MethodMetadataModel.model_validate(entry)
        assert validated.name == entry["name"]


def test_registry_catalog_covers_maintained_wrapper_and_optional_paths() -> None:
    ssa = MethodRegistry.get_metadata("SSA")
    stl = MethodRegistry.get_metadata("STL")
    mvmd = MethodRegistry.get_metadata("MVMD")

    assert ssa["maturity"] == "maintained"
    assert ssa["claim_scope"] == "maintained"
    assert ssa["references"]
    assert any(param["name"] == "window" for param in ssa["parameter_docs"])
    assert "trend" in ssa["output_components"]
    assert ssa["example_config"]["method"] == "SSA"
    assert stl["implementation"] == "wrapper"
    assert stl["package_links"]
    stl_params = {param["name"] for param in stl["parameter_docs"]}
    assert {
        "period",
        "seasonal",
        "trend",
        "low_pass",
        "seasonal_deg",
        "trend_deg",
        "low_pass_deg",
        "robust",
        "seasonal_jump",
        "trend_jump",
        "low_pass_jump",
    } == stl_params
    mstl_params = {
        param["name"] for param in MethodRegistry.get_metadata("MSTL")["parameter_docs"]
    }
    assert {"periods", "windows", "lmbda", "iterate", "stl_kwargs"} == mstl_params
    assert mvmd["dependency_tier"] == "optional-backend"
    assert mvmd["optional_dependencies"] == ["PySDKit"]
    assert mvmd["claim_scope"] == "integration"

    for method in ("EMD", "CEEMDAN"):
        metadata = MethodRegistry.get_metadata(method)
        assert metadata["implementation"] == "wrapper"
        assert metadata["dependency_tier"] == "optional-backend"
        assert metadata["optional_dependencies"] == ["PyEMD"]
        assert metadata["claim_scope"] == "integration"

    autoformer = MethodRegistry.get_metadata("AUTOFORMER_BLOCK")
    assert autoformer["claim_scope"] == "experimental-operator"
    assert autoformer["alias_of"] == "MOVING_AVERAGE_DECOMPOSITION_BLOCK"


def test_registry_payload_model_roundtrip() -> None:
    payload = MethodRegistryPayloadModel(
        package="detime",
        version="0.1.3",
        contract_version="0.1",
        methods=[MethodMetadataModel.model_validate(entry) for entry in MethodRegistry.list_catalog()],
    )
    assert payload.package == "detime"
    assert payload.contract_version == "0.1"
    assert payload.methods
