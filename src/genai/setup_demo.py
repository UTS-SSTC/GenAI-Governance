"""Create demo users and seed records for the Salesforce prototype."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from genai.salesforce_cli import (
    DEFAULT_ORG_ALIAS,
    SalesforceCliError,
    create_record,
    delete_record,
    escape_soql_text,
    query_records,
    update_record,
)

DEMO_EMAIL = "qianfuvpro@qq.com"
USERNAME_SUFFIX = "576765349-a2"
BUSINESS_UNIT_NAME = "AI Governance Demo Unit"
CLOUD_MODEL_NAME = "Azure OpenAI Demo Model"
SCENARIO_MARKER = "[A2 Demo Scenario]"

DEMO_USERS = [
    {
        "profile": "Business User",
        "username": f"business.user.{USERNAME_SUFFIX}@example.com",
        "alias": "bususer",
        "last_name": "Business User",
    },
    {
        "profile": "Governance Officer",
        "username": f"governance.officer.{USERNAME_SUFFIX}@example.com",
        "alias": "govoff",
        "last_name": "Governance Officer",
    },
    {
        "profile": "Cloud Admin",
        "username": f"cloud.admin.{USERNAME_SUFFIX}@example.com",
        "alias": "cldadmin",
        "last_name": "Cloud Admin",
    },
]

BUSINESS_UNITS: list[dict[str, object]] = [
    {
        "Name": BUSINESS_UNIT_NAME,
        "Department_Type__c": "IT",
        "Manager_Email__c": DEMO_EMAIL,
        "Budget_Limit__c": 5000,
    },
    {
        "Name": "Finance Analytics Unit",
        "Department_Type__c": "Finance",
        "Manager_Email__c": DEMO_EMAIL,
        "Budget_Limit__c": 8000,
    },
    {
        "Name": "Marketing Content Unit",
        "Department_Type__c": "Marketing",
        "Manager_Email__c": DEMO_EMAIL,
        "Budget_Limit__c": 3000,
    },
    {
        "Name": "People Operations Unit",
        "Department_Type__c": "HR",
        "Manager_Email__c": DEMO_EMAIL,
        "Budget_Limit__c": 2000,
    },
    {
        "Name": "Cloud Platform Unit",
        "Department_Type__c": "Operations",
        "Manager_Email__c": DEMO_EMAIL,
        "Budget_Limit__c": 15000,
    },
]

CLOUD_MODELS: list[dict[str, object]] = [
    {
        "Name": CLOUD_MODEL_NAME,
        "Cloud_Provider__c": "Azure",
        "Service_Type__c": "Document Analysis",
        "Data_Residency_Region__c": "Australia",
        "Estimated_Cost_Per_1K_Tokens__c": 0.01,
        "Status__c": "Available",
    },
    {
        "Name": "AWS Bedrock Text Generation",
        "Cloud_Provider__c": "AWS",
        "Service_Type__c": "Text Generation",
        "Data_Residency_Region__c": "US",
        "Estimated_Cost_Per_1K_Tokens__c": 0.012,
        "Status__c": "Available",
    },
    {
        "Name": "Google Vertex AI Support Assistant",
        "Cloud_Provider__c": "Google Cloud",
        "Service_Type__c": "Text Generation",
        "Data_Residency_Region__c": "Asia-Pacific",
        "Estimated_Cost_Per_1K_Tokens__c": 0.009,
        "Status__c": "Available",
    },
    {
        "Name": "Azure Code Assistant Restricted",
        "Cloud_Provider__c": "Azure",
        "Service_Type__c": "Code Generation",
        "Data_Residency_Region__c": "EU",
        "Estimated_Cost_Per_1K_Tokens__c": 0.02,
        "Status__c": "Restricted",
    },
    {
        "Name": "Legacy Image Generator Retired",
        "Cloud_Provider__c": "Other",
        "Service_Type__c": "Image Generation",
        "Data_Residency_Region__c": "Other",
        "Estimated_Cost_Per_1K_Tokens__c": 0.03,
        "Status__c": "Retired",
    },
    {
        "Name": "Google Document AI Australia",
        "Cloud_Provider__c": "Google Cloud",
        "Service_Type__c": "Document Analysis",
        "Data_Residency_Region__c": "Australia",
        "Estimated_Cost_Per_1K_Tokens__c": 0.008,
        "Status__c": "Available",
    },
]

REQUEST_SCENARIOS: list[dict[str, Any]] = [
    {
        "key": "draft-low-risk",
        "business_unit": "People Operations Unit",
        "cloud_model": "AWS Bedrock Text Generation",
        "justification": (
            "Draft request for an HR policy assistant using low sensitivity "
            "internal content."
        ),
        "values": {
            "Use_Case_Type__c": "Other",
            "Data_Sensitivity__c": "Low",
            "Estimated_Monthly_Cost__c": 600,
            "Request_Status__c": "Draft",
        },
        "risk_assessments": [],
    },
    {
        "key": "submitted-review-task",
        "business_unit": "Finance Analytics Unit",
        "cloud_model": CLOUD_MODEL_NAME,
        "justification": (
            "Submitted finance document analysis request awaiting governance review."
        ),
        "values": {
            "Use_Case_Type__c": "Document Analysis",
            "Data_Sensitivity__c": "Medium",
            "Estimated_Monthly_Cost__c": 1600,
            "Request_Status__c": "Submitted",
        },
        "risk_assessments": [],
    },
    {
        "key": "under-review-pending-risk",
        "business_unit": "Marketing Content Unit",
        "cloud_model": "Google Vertex AI Support Assistant",
        "justification": (
            "High sensitivity customer support request under privacy and "
            "compliance review."
        ),
        "values": {
            "Use_Case_Type__c": "Customer Support",
            "Data_Sensitivity__c": "High",
            "Estimated_Monthly_Cost__c": 2500,
            "Request_Status__c": "Under Review",
        },
        "risk_assessments": [
            {
                "Privacy_Risk_Level__c": "High",
                "Compliance_Risk_Level__c": "Medium",
                "Security_Review_Required__c": True,
                "Risk_Comment__c": (
                    "Pending review for customer data handling and support "
                    "transcript retention."
                ),
                "Assessment_Status__c": "Pending",
            }
        ],
    },
    {
        "key": "approved-with-reminder",
        "business_unit": "Finance Analytics Unit",
        "cloud_model": "Google Document AI Australia",
        "justification": (
            "Approved invoice extraction request with deployment reminder evidence."
        ),
        "values": {
            "Use_Case_Type__c": "Document Analysis",
            "Data_Sensitivity__c": "Medium",
            "Estimated_Monthly_Cost__c": 4200,
            "Request_Status__c": "Approved",
        },
        "deployment_offset_days": 7,
        "risk_assessments": [
            {
                "Privacy_Risk_Level__c": "Medium",
                "Compliance_Risk_Level__c": "Low",
                "Security_Review_Required__c": True,
                "Risk_Comment__c": (
                    "Passed with Australian data residency and restricted "
                    "invoice dataset access."
                ),
                "Assessment_Status__c": "Passed",
            }
        ],
    },
    {
        "key": "approved-without-reminder",
        "business_unit": "Cloud Platform Unit",
        "cloud_model": "AWS Bedrock Text Generation",
        "justification": (
            "Approved internal knowledge assistant without a deployment date."
        ),
        "values": {
            "Use_Case_Type__c": "Other",
            "Data_Sensitivity__c": "Medium",
            "Estimated_Monthly_Cost__c": 3200,
            "Request_Status__c": "Approved",
        },
        "risk_assessments": [
            {
                "Privacy_Risk_Level__c": "Low",
                "Compliance_Risk_Level__c": "Low",
                "Security_Review_Required__c": False,
                "Risk_Comment__c": (
                    "Passed because only internal documentation is indexed."
                ),
                "Assessment_Status__c": "Passed",
            }
        ],
    },
    {
        "key": "rejected-failed-risk",
        "business_unit": "Marketing Content Unit",
        "cloud_model": "Legacy Image Generator Retired",
        "justification": (
            "Rejected marketing image generation request using a retired model "
            "and high sensitivity content."
        ),
        "values": {
            "Use_Case_Type__c": "Marketing",
            "Data_Sensitivity__c": "High",
            "Estimated_Monthly_Cost__c": 2400,
            "Request_Status__c": "Rejected",
        },
        "risk_assessments": [
            {
                "Privacy_Risk_Level__c": "High",
                "Compliance_Risk_Level__c": "High",
                "Security_Review_Required__c": True,
                "Risk_Comment__c": (
                    "Failed because the requested model is retired and the "
                    "campaign data is high sensitivity."
                ),
                "Assessment_Status__c": "Failed",
            }
        ],
    },
    {
        "key": "deployed-completed",
        "business_unit": "Cloud Platform Unit",
        "cloud_model": "Azure Code Assistant Restricted",
        "justification": (
            "Completed deployment for a restricted code generation assistant "
            "with cloud admin oversight."
        ),
        "values": {
            "Use_Case_Type__c": "Code Generation",
            "Data_Sensitivity__c": "Low",
            "Estimated_Monthly_Cost__c": 7000,
            "Request_Status__c": "Deployed",
        },
        "risk_assessments": [
            {
                "Privacy_Risk_Level__c": "Low",
                "Compliance_Risk_Level__c": "Medium",
                "Security_Review_Required__c": True,
                "Risk_Comment__c": (
                    "Passed with source code access restrictions and cloud "
                    "admin deployment control."
                ),
                "Assessment_Status__c": "Passed",
            }
        ],
    },
]


def main() -> int:
    """
    Run demo runtime setup.

    Returns:
        Process exit code.
    """
    try:
        profiles = load_profiles()
        ensure_salesforce_license_capacity()
        for user in DEMO_USERS:
            ensure_user(user, profiles[user["profile"]])
        business_unit_ids = ensure_business_units()
        cloud_model_ids = ensure_cloud_models()
        request_ids = ensure_request_scenarios(business_unit_ids, cloud_model_ids)
        print_demo_summary(request_ids)
    except SalesforceCliError as error:
        print(error)
        print(error.output)
        return 1
    except RuntimeError as error:
        print(error)
        return 1
    print("Demo setup completed.")
    return 0


def load_profiles() -> dict[str, str]:
    """
    Load required custom profile IDs.

    Returns:
        A mapping from profile name to profile ID.
    """
    quoted_names = ", ".join(
        f"'{escape_soql_text(user['profile'])}'" for user in DEMO_USERS
    )
    records = query_records(
        f"SELECT Id, Name FROM Profile WHERE Name IN ({quoted_names})",
        DEFAULT_ORG_ALIAS,
    )
    profiles = {
        str(record["Name"]): str(record["Id"])
        for record in records
        if "Name" in record and "Id" in record
    }
    missing = sorted({str(user["profile"]) for user in DEMO_USERS} - profiles.keys())
    if missing:
        raise RuntimeError(f"Missing deployed profiles: {', '.join(missing)}")
    return profiles


def ensure_salesforce_license_capacity() -> None:
    """
    Ensure there are enough Salesforce licenses for missing demo users.

    Raises:
        RuntimeError: If the org cannot create all missing demo users.
    """
    missing_usernames = [
        user["username"]
        for user in DEMO_USERS
        if not find_user_id(str(user["username"]))
    ]
    if not missing_usernames:
        return
    licenses = query_records(
        "SELECT TotalLicenses, UsedLicenses FROM UserLicense WHERE Name = 'Salesforce'",
        DEFAULT_ORG_ALIAS,
    )
    if not licenses:
        raise RuntimeError("Salesforce user license information is unavailable.")
    license_record = licenses[0]
    total = int(license_record["TotalLicenses"])
    used = int(license_record["UsedLicenses"])
    remaining = total - used
    if remaining < len(missing_usernames):
        raise RuntimeError(
            "Not enough Salesforce licenses for demo users: "
            f"{remaining} remaining, {len(missing_usernames)} missing."
        )


def find_user_id(username: str) -> str | None:
    """
    Find a Salesforce user by username.

    Args:
        username: Salesforce username.

    Returns:
        User ID when the user exists.
    """
    records = query_records(
        f"SELECT Id FROM User WHERE Username = '{escape_soql_text(username)}'",
        DEFAULT_ORG_ALIAS,
    )
    if not records:
        return None
    return str(records[0]["Id"])


def ensure_user(user: dict[str, Any], profile_id: str) -> str:
    """
    Create a demo user if it does not already exist.

    Args:
        user: Demo user configuration.
        profile_id: Profile ID to assign.

    Returns:
        User ID.
    """
    username = str(user["username"])
    existing_id = find_user_id(username)
    if existing_id:
        print(f"User exists: {username}")
        return existing_id
    user_id = create_record(
        "User",
        {
            "Username": username,
            "Alias": user["alias"],
            "Email": DEMO_EMAIL,
            "EmailEncodingKey": "UTF-8",
            "LanguageLocaleKey": "en_US",
            "LastName": user["last_name"],
            "LocaleSidKey": "en_US",
            "ProfileId": profile_id,
            "TimeZoneSidKey": "Australia/Sydney",
            "IsActive": True,
        },
        DEFAULT_ORG_ALIAS,
    )
    print(f"Created user: {username}")
    return user_id


def ensure_business_unit() -> str:
    """
    Create or find the demo business unit.

    Returns:
        Business unit record ID.
    """
    return ensure_named_record("Business_Unit__c", BUSINESS_UNITS[0])


def ensure_cloud_model() -> str:
    """
    Create or find the demo cloud model.

    Returns:
        Cloud model record ID.
    """
    return ensure_named_record("Cloud_Model__c", CLOUD_MODELS[0])


def ensure_business_units() -> dict[str, str]:
    """
    Create or update all demo business units.

    Returns:
        Business unit record IDs keyed by business unit name.
    """
    return {
        str(values["Name"]): ensure_named_record("Business_Unit__c", values)
        for values in BUSINESS_UNITS
    }


def ensure_cloud_models() -> dict[str, str]:
    """
    Create or update all demo cloud models.

    Returns:
        Cloud model record IDs keyed by cloud model name.
    """
    return {
        str(values["Name"]): ensure_named_record("Cloud_Model__c", values)
        for values in CLOUD_MODELS
    }


def ensure_named_record(sobject: str, values: dict[str, object]) -> str:
    """
    Create or update a named Salesforce record.

    Args:
        sobject: Salesforce object API name.
        values: Field values including a Name field.

    Returns:
        Salesforce record ID.
    """
    name = str(values["Name"])
    records = query_records(
        f"SELECT Id FROM {sobject} WHERE Name = '{escape_soql_text(name)}' LIMIT 1",
        DEFAULT_ORG_ALIAS,
    )
    if records:
        record_id = str(records[0]["Id"])
        update_record(sobject, record_id, values, DEFAULT_ORG_ALIAS)
        print(f"Updated {sobject}: {name}")
        return record_id
    record_id = create_record(sobject, values, DEFAULT_ORG_ALIAS)
    print(f"Created {sobject}: {name}")
    return record_id


def ensure_request_scenarios(
    business_unit_ids: dict[str, str],
    cloud_model_ids: dict[str, str],
) -> dict[str, str]:
    """
    Create or update all demo request branch scenarios.

    Args:
        business_unit_ids: Business unit record IDs keyed by name.
        cloud_model_ids: Cloud model record IDs keyed by name.

    Returns:
        GenAI request IDs keyed by scenario key.
    """
    existing_request_ids = load_existing_request_ids()
    request_ids: dict[str, str] = {}
    for scenario in REQUEST_SCENARIOS:
        request_id = ensure_request_scenario(
            scenario,
            existing_request_ids,
            business_unit_ids,
            cloud_model_ids,
        )
        request_ids[str(scenario["key"])] = request_id
    return request_ids


def load_existing_request_ids() -> dict[str, str]:
    """
    Load existing marked demo request records.

    Returns:
        Existing GenAI request IDs keyed by scenario key.
    """
    records = query_records(
        "SELECT Id, Business_Justification__c FROM GenAI_Request__c "
        f"WHERE Request_Owner_Email__c = '{escape_soql_text(DEMO_EMAIL)}'",
        DEFAULT_ORG_ALIAS,
    )
    request_ids: dict[str, str] = {}
    for record in records:
        justification = str(record.get("Business_Justification__c", ""))
        for scenario in REQUEST_SCENARIOS:
            key = str(scenario["key"])
            if justification.startswith(scenario_prefix(key)):
                request_ids[key] = str(record["Id"])
    return request_ids


def ensure_request_scenario(
    scenario: dict[str, Any],
    existing_request_ids: dict[str, str],
    business_unit_ids: dict[str, str],
    cloud_model_ids: dict[str, str],
) -> str:
    """
    Create or update one demo request branch scenario.

    Args:
        scenario: Scenario configuration.
        existing_request_ids: Existing request IDs keyed by scenario key.
        business_unit_ids: Business unit record IDs keyed by name.
        cloud_model_ids: Cloud model record IDs keyed by name.

    Returns:
        GenAI request record ID.
    """
    key = str(scenario["key"])
    values = build_request_values(scenario, business_unit_ids, cloud_model_ids)
    target_status = str(values["Request_Status__c"])
    request_id = existing_request_ids.get(key)
    if request_id is None:
        create_values = dict(values)
        create_values["Request_Status__c"] = initial_request_status(target_status)
        request_id = create_record("GenAI_Request__c", create_values, DEFAULT_ORG_ALIAS)
        print(f"Created GenAI_Request__c scenario: {key}")

    ensure_risk_assessments(key, request_id, scenario)
    if target_status == "Submitted":
        delete_existing_review_tasks(request_id)
    apply_request_status(request_id, target_status, values)
    return request_id


def build_request_values(
    scenario: dict[str, Any],
    business_unit_ids: dict[str, str],
    cloud_model_ids: dict[str, str],
) -> dict[str, object]:
    """
    Build Salesforce field values for one request scenario.

    Args:
        scenario: Scenario configuration.
        business_unit_ids: Business unit record IDs keyed by name.
        cloud_model_ids: Cloud model record IDs keyed by name.

    Returns:
        Field values for a GenAI request record.
    """
    values = dict(scenario["values"])
    business_unit_name = str(scenario["business_unit"])
    cloud_model_name = str(scenario["cloud_model"])
    values["Business_Unit__c"] = business_unit_ids[business_unit_name]
    values["Selected_Cloud_Model__c"] = cloud_model_ids[cloud_model_name]
    values["Business_Justification__c"] = (
        f"{scenario_prefix(str(scenario['key']))} {scenario['justification']}"
    )
    values["Request_Owner_Email__c"] = DEMO_EMAIL
    if "deployment_offset_days" in scenario:
        values["Required_Deployment_Date_Time__c"] = future_salesforce_datetime(
            int(scenario["deployment_offset_days"])
        )
    return values


def initial_request_status(target_status: str) -> str:
    """
    Choose the safe initial status for a request scenario.

    Args:
        target_status: Final request status for the scenario.

    Returns:
        Initial status to use when creating the record.
    """
    if target_status in {"Approved", "Rejected", "Deployed"}:
        return "Draft"
    return target_status


def apply_request_status(
    request_id: str,
    target_status: str,
    values: dict[str, object],
) -> None:
    """
    Update a request scenario to its target status.

    Args:
        request_id: GenAI request record ID.
        target_status: Final request status for the scenario.
        values: Full request values for the scenario.
    """
    update_values = dict(values)
    if target_status == "Deployed":
        approved_values = dict(update_values)
        approved_values["Request_Status__c"] = "Approved"
        update_record(
            "GenAI_Request__c", request_id, approved_values, DEFAULT_ORG_ALIAS
        )
    update_record("GenAI_Request__c", request_id, update_values, DEFAULT_ORG_ALIAS)
    print(f"Updated GenAI_Request__c scenario to {target_status}: {request_id}")


def delete_existing_review_tasks(request_id: str) -> None:
    """
    Delete existing review tasks before re-triggering the submitted scenario.

    Args:
        request_id: GenAI request record ID.
    """
    records = query_records(
        "SELECT Id FROM Task "
        f"WHERE WhatId = '{escape_soql_text(request_id)}' "
        "AND Subject = 'Review GenAI Request'",
        DEFAULT_ORG_ALIAS,
    )
    for record in records:
        delete_record("Task", str(record["Id"]), DEFAULT_ORG_ALIAS)
    if records:
        print(f"Deleted existing review tasks: {len(records)}")


def ensure_risk_assessments(
    scenario_key: str,
    request_id: str,
    scenario: dict[str, Any],
) -> None:
    """
    Create or update risk assessments for one request scenario.

    Args:
        scenario_key: Stable request scenario key.
        request_id: GenAI request record ID.
        scenario: Scenario configuration.
    """
    existing_assessment_ids = load_existing_assessment_ids(request_id, scenario_key)
    for index, assessment in enumerate(scenario["risk_assessments"], start=1):
        values = build_risk_assessment_values(
            request_id, scenario_key, index, assessment
        )
        assessment_key = risk_assessment_key(scenario_key, index)
        assessment_id = existing_assessment_ids.get(assessment_key)
        if assessment_id is None:
            assessment_id = create_record(
                "Risk_Assessment__c",
                values,
                DEFAULT_ORG_ALIAS,
            )
            print(f"Created Risk_Assessment__c scenario: {assessment_key}")
        else:
            values_without_parent = dict(values)
            del values_without_parent["GenAI_Request__c"]
            update_record(
                "Risk_Assessment__c",
                assessment_id,
                values_without_parent,
                DEFAULT_ORG_ALIAS,
            )
            print(f"Updated Risk_Assessment__c scenario: {assessment_key}")


def load_existing_assessment_ids(
    request_id: str,
    scenario_key: str,
) -> dict[str, str]:
    """
    Load existing marked risk assessments for one request.

    Args:
        request_id: GenAI request record ID.
        scenario_key: Stable request scenario key.

    Returns:
        Risk assessment IDs keyed by assessment marker.
    """
    records = query_records(
        "SELECT Id, Risk_Comment__c FROM Risk_Assessment__c "
        f"WHERE GenAI_Request__c = '{escape_soql_text(request_id)}'",
        DEFAULT_ORG_ALIAS,
    )
    assessment_ids: dict[str, str] = {}
    for record in records:
        comment = str(record.get("Risk_Comment__c", ""))
        for index in range(1, 6):
            assessment_key = risk_assessment_key(scenario_key, index)
            if comment.startswith(risk_assessment_prefix(assessment_key)):
                assessment_ids[assessment_key] = str(record["Id"])
    return assessment_ids


def build_risk_assessment_values(
    request_id: str,
    scenario_key: str,
    index: int,
    assessment: dict[str, object],
) -> dict[str, object]:
    """
    Build Salesforce field values for one risk assessment.

    Args:
        request_id: GenAI request record ID.
        scenario_key: Stable request scenario key.
        index: One-based assessment index for the scenario.
        assessment: Risk assessment field values.

    Returns:
        Field values for a risk assessment record.
    """
    values = dict(assessment)
    assessment_key = risk_assessment_key(scenario_key, index)
    values["GenAI_Request__c"] = request_id
    values["Risk_Comment__c"] = (
        f"{risk_assessment_prefix(assessment_key)} {assessment['Risk_Comment__c']}"
    )
    return values


def scenario_prefix(key: str) -> str:
    """
    Build the stable text marker for a request scenario.

    Args:
        key: Scenario key.

    Returns:
        Request scenario marker.
    """
    return f"{SCENARIO_MARKER} {key}:"


def risk_assessment_key(scenario_key: str, index: int) -> str:
    """
    Build the stable key for one risk assessment scenario.

    Args:
        scenario_key: Stable request scenario key.
        index: One-based assessment index.

    Returns:
        Risk assessment scenario key.
    """
    return f"{scenario_key}-risk-{index}"


def risk_assessment_prefix(assessment_key: str) -> str:
    """
    Build the stable text marker for a risk assessment scenario.

    Args:
        assessment_key: Risk assessment scenario key.

    Returns:
        Risk assessment scenario marker.
    """
    return f"{SCENARIO_MARKER} {assessment_key}:"


def future_salesforce_datetime(offset_days: int) -> str:
    """
    Build a future UTC datetime value accepted by Salesforce.

    Args:
        offset_days: Number of days after the current date.

    Returns:
        Salesforce-compatible UTC datetime string.
    """
    future_value = datetime.now(UTC) + timedelta(days=offset_days)
    return future_value.replace(minute=0, second=0, microsecond=0).isoformat()


def print_demo_summary(request_ids: dict[str, str]) -> None:
    """
    Print a concise summary of seeded demo branch data.

    Args:
        request_ids: GenAI request IDs keyed by scenario key.
    """
    print("Demo branch setup completed.")
    print(f"Business units prepared: {len(BUSINESS_UNITS)}")
    print(f"Cloud models prepared: {len(CLOUD_MODELS)}")
    print(f"Request scenarios prepared: {len(request_ids)}")
    print(
        "Covered request statuses: Draft, Submitted, Under Review, Approved, "
        "Rejected, Deployed"
    )
    print("Covered risk statuses: Pending, Passed, Failed")


if __name__ == "__main__":
    raise SystemExit(main())
