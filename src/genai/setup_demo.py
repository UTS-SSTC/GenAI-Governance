"""Create demo users and seed records for the Salesforce prototype."""

from __future__ import annotations

from typing import Any

from genai.salesforce_cli import (
    DEFAULT_ORG_ALIAS,
    SalesforceCliError,
    create_record,
    escape_soql_text,
    query_records,
)

DEMO_EMAIL = "qianfuvpro@qq.com"
USERNAME_SUFFIX = "576765349-a2"
BUSINESS_UNIT_NAME = "AI Governance Demo Unit"
CLOUD_MODEL_NAME = "Azure OpenAI Demo Model"

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
        business_unit_id = ensure_business_unit()
        cloud_model_id = ensure_cloud_model()
        request_id = create_seed_request(business_unit_id, cloud_model_id)
        create_seed_risk_assessment(request_id)
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
    escaped_name = escape_soql_text(BUSINESS_UNIT_NAME)
    existing = query_records(
        f"SELECT Id FROM Business_Unit__c WHERE Name = '{escaped_name}'",
        DEFAULT_ORG_ALIAS,
    )
    if existing:
        print(f"Business unit exists: {BUSINESS_UNIT_NAME}")
        return str(existing[0]["Id"])
    record_id = create_record(
        "Business_Unit__c",
        {
            "Name": BUSINESS_UNIT_NAME,
            "Department_Type__c": "IT",
            "Manager_Email__c": DEMO_EMAIL,
            "Budget_Limit__c": 5000,
        },
        DEFAULT_ORG_ALIAS,
    )
    print(f"Created business unit: {BUSINESS_UNIT_NAME}")
    return record_id


def ensure_cloud_model() -> str:
    """
    Create or find the demo cloud model.

    Returns:
        Cloud model record ID.
    """
    escaped_name = escape_soql_text(CLOUD_MODEL_NAME)
    existing = query_records(
        f"SELECT Id FROM Cloud_Model__c WHERE Name = '{escaped_name}'",
        DEFAULT_ORG_ALIAS,
    )
    if existing:
        print(f"Cloud model exists: {CLOUD_MODEL_NAME}")
        return str(existing[0]["Id"])
    record_id = create_record(
        "Cloud_Model__c",
        {
            "Name": CLOUD_MODEL_NAME,
            "Cloud_Provider__c": "Azure",
            "Service_Type__c": "Document Analysis",
            "Data_Residency_Region__c": "Australia",
            "Estimated_Cost_Per_1K_Tokens__c": 0.01,
            "Status__c": "Available",
        },
        DEFAULT_ORG_ALIAS,
    )
    print(f"Created cloud model: {CLOUD_MODEL_NAME}")
    return record_id


def create_seed_request(business_unit_id: str, cloud_model_id: str) -> str:
    """
    Create a valid draft GenAI request.

    Args:
        business_unit_id: Business unit lookup ID.
        cloud_model_id: Cloud model lookup ID.

    Returns:
        GenAI request record ID.
    """
    record_id = create_record(
        "GenAI_Request__c",
        {
            "Business_Unit__c": business_unit_id,
            "Selected_Cloud_Model__c": cloud_model_id,
            "Use_Case_Type__c": "Document Analysis",
            "Business_Justification__c": "Demo request for report screenshots.",
            "Data_Sensitivity__c": "Medium",
            "Estimated_Monthly_Cost__c": 1200,
            "Request_Status__c": "Draft",
            "Request_Owner_Email__c": DEMO_EMAIL,
        },
        DEFAULT_ORG_ALIAS,
    )
    print(f"Created draft GenAI request: {record_id}")
    return record_id


def create_seed_risk_assessment(request_id: str) -> str:
    """
    Create a passed risk assessment for a request.

    Args:
        request_id: GenAI request parent ID.

    Returns:
        Risk assessment record ID.
    """
    record_id = create_record(
        "Risk_Assessment__c",
        {
            "GenAI_Request__c": request_id,
            "Privacy_Risk_Level__c": "Medium",
            "Compliance_Risk_Level__c": "Low",
            "Security_Review_Required__c": True,
            "Risk_Comment__c": "Demo assessment for prototype evidence.",
            "Assessment_Status__c": "Passed",
        },
        DEFAULT_ORG_ALIAS,
    )
    print(f"Created risk assessment: {record_id}")
    return record_id


if __name__ == "__main__":
    raise SystemExit(main())
