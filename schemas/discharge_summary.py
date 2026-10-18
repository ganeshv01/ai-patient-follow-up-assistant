from datetime import date
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Medication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    instructions: str = Field(min_length=1)

    @field_validator("name", "instructions")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class DischargeSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str
    document_type: Literal["discharge_summary"] = "discharge_summary"
    discharge_date: date
    diagnosis: str = Field(min_length=1)
    clinical_notes: str = Field(min_length=1)
    medications: list[Medication] = Field(min_length=1)
    required_tests: list[str] = Field(default_factory=list)
    required_tests_status: Literal["specified", "none_required", "unknown"] = "unknown"
    follow_up_date: date | None = None
    follow_up_instructions: str | None = None

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, value: str) -> str:
        value = value.strip()
        if not re.fullmatch(r"P\d{4,}", value):
            raise ValueError("patient_id must look like P1001")
        return value

    @field_validator("diagnosis", "clinical_notes")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @field_validator("required_tests")
    @classmethod
    def validate_required_tests(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value]
        if any(not item for item in cleaned):
            raise ValueError("Required tests cannot contain blank entries")
        return cleaned

    @field_validator("follow_up_instructions")
    @classmethod
    def validate_follow_up_instructions(
        cls, value: str | None
    ) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Instructions must be non-empty or null")
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.follow_up_date is not None
            and self.follow_up_date <= self.discharge_date
        ):
            raise ValueError(
                "follow_up_date must be later than discharge_date"
            )
        return self

    @model_validator(mode="after")
    def validate_required_tests_status(self):
        if (
            self.required_tests_status == "specified"
            and not self.required_tests
        ):
            raise ValueError(
                "At least one test is required when status is 'specified'"
            )

        if (
            self.required_tests_status == "none_required"
            and self.required_tests
        ):
            raise ValueError(
                "Tests must be empty when status is 'none_required'"
            )

        return self

    @property
    def needs_follow_up_clarification(self) -> bool:
        return self.follow_up_date is None
