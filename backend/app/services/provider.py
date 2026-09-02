from dataclasses import dataclass


@dataclass
class ModelSelection:
    provider: str
    model: str


def default_model_selection() -> ModelSelection:
    # Provider abstraction placeholder: future providers can be configured without
    # changing proposal orchestration flow.
    return ModelSelection(provider="local-template", model="deterministic-v1")
