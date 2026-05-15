"""Run Salesforce CLI commands safely for prototype automation."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from typing import Any

DEFAULT_ORG_ALIAS = "genai-dev-de"
SENSITIVE_KEYS = {"accessToken", "refreshToken", "password", "securityToken"}


class SalesforceCliError(Exception):
    """Raised when a Salesforce CLI command fails."""

    def __init__(self, command: Sequence[str], output: object) -> None:
        """
        Store a redacted CLI command failure.

        Args:
            command: The Salesforce CLI command that failed.
            output: Redacted command output or stderr text.
        """
        self.command = list(command)
        self.output = output
        super().__init__(f"Salesforce CLI command failed: {' '.join(command)}")


def redact_secrets(value: object) -> object:
    """
    Redact sensitive values from nested Salesforce CLI output.

    Args:
        value: A JSON-compatible value returned by Salesforce CLI.

    Returns:
        The same structure with sensitive fields replaced.
    """
    if isinstance(value, Mapping):
        return {
            key: "***REDACTED***" if key in SENSITIVE_KEYS else redact_secrets(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value


def run_sf(arguments: Sequence[str]) -> dict[str, Any]:
    """
    Run an `sf` command and parse its JSON output.

    Args:
        arguments: Arguments after the `sf` executable.

    Returns:
        Parsed JSON output from the Salesforce CLI.

    Raises:
        SalesforceCliError: If the command fails or returns invalid JSON.
    """
    command = [resolve_sf_executable(), *arguments]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    raw_output = completed.stdout.strip() or completed.stderr.strip()
    try:
        parsed: object = json.loads(raw_output) if raw_output else {}
    except json.JSONDecodeError as error:
        raise SalesforceCliError(command, raw_output) from error

    redacted = redact_secrets(parsed)
    if completed.returncode != 0:
        raise SalesforceCliError(command, redacted)
    if not isinstance(redacted, dict):
        raise SalesforceCliError(command, redacted)
    return redacted


def resolve_sf_executable() -> str:
    """
    Resolve the Salesforce CLI executable path.

    Returns:
        Path or executable name for Salesforce CLI.

    Raises:
        SalesforceCliError: If Salesforce CLI is not available on PATH.
    """
    executable = shutil.which("sf") or shutil.which("sf.cmd") or shutil.which("sf.exe")
    if executable is None:
        raise SalesforceCliError(["sf"], "Salesforce CLI executable was not found.")
    return executable


def query_records(
    query: str, target_org: str = DEFAULT_ORG_ALIAS
) -> list[dict[str, Any]]:
    """
    Run a SOQL query and return record dictionaries.

    Args:
        query: SOQL query text.
        target_org: Salesforce CLI org alias.

    Returns:
        A list of records from the query result.
    """
    output = run_sf(
        [
            "data",
            "query",
            "--target-org",
            target_org,
            "--query",
            query,
            "--json",
        ]
    )
    result = output.get("result", {})
    if not isinstance(result, dict):
        return []
    records = result.get("records", [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, dict)]


def create_record(
    sobject: str,
    values: Mapping[str, object],
    target_org: str = DEFAULT_ORG_ALIAS,
) -> str:
    """
    Create a Salesforce record and return its ID.

    Args:
        sobject: Salesforce object API name.
        values: Field values for the new record.
        target_org: Salesforce CLI org alias.

    Returns:
        The created record ID.
    """
    output = run_sf(
        [
            "data",
            "create",
            "record",
            "--target-org",
            target_org,
            "--sobject",
            sobject,
            "--values",
            format_values(values),
            "--json",
        ]
    )
    result = output.get("result", {})
    if isinstance(result, dict) and isinstance(result.get("id"), str):
        return result["id"]
    raise SalesforceCliError(["sf", "data", "create", "record", sobject], output)


def update_record(
    sobject: str,
    record_id: str,
    values: Mapping[str, object],
    target_org: str = DEFAULT_ORG_ALIAS,
) -> None:
    """
    Update a Salesforce record by ID.

    Args:
        sobject: Salesforce object API name.
        record_id: Salesforce record ID.
        values: Field values to update.
        target_org: Salesforce CLI org alias.
    """
    run_sf(
        [
            "data",
            "update",
            "record",
            "--target-org",
            target_org,
            "--sobject",
            sobject,
            "--record-id",
            record_id,
            "--values",
            format_values(values),
            "--json",
        ]
    )


def delete_record(
    sobject: str,
    record_id: str,
    target_org: str = DEFAULT_ORG_ALIAS,
) -> None:
    """
    Delete a Salesforce record by ID.

    Args:
        sobject: Salesforce object API name.
        record_id: Salesforce record ID.
        target_org: Salesforce CLI org alias.
    """
    run_sf(
        [
            "data",
            "delete",
            "record",
            "--target-org",
            target_org,
            "--sobject",
            sobject,
            "--record-id",
            record_id,
            "--json",
        ]
    )


def format_values(values: Mapping[str, object]) -> str:
    """
    Format field values for Salesforce CLI data commands.

    Args:
        values: Field values to serialize.

    Returns:
        A Salesforce CLI values string.
    """
    parts: list[str] = []
    for field_name, value in values.items():
        if value is None:
            continue
        parts.append(f"{field_name}={format_value(value)}")
    return " ".join(parts)


def format_value(value: object) -> str:
    """
    Format one Salesforce CLI field value.

    Args:
        value: Field value to serialize.

    Returns:
        A Salesforce CLI-safe field value.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    if not text or any(character.isspace() for character in text):
        return f"'{text.replace("'", "\\'")}'"
    return text


def escape_soql_text(value: str) -> str:
    """
    Escape a string for use in a SOQL single-quoted literal.

    Args:
        value: Raw string value.

    Returns:
        Escaped SOQL string text without surrounding quotes.
    """
    return value.replace("\\", "\\\\").replace("'", "\\'")
