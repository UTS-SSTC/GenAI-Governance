"""Smoke-test Salesforce validation rules and simple automation."""

from __future__ import annotations

from genai.salesforce_cli import (
    DEFAULT_ORG_ALIAS,
    SalesforceCliError,
    create_record,
    escape_soql_text,
    query_records,
    update_record,
)
from genai.setup_demo import BUSINESS_UNIT_NAME, CLOUD_MODEL_NAME, DEMO_EMAIL


def main() -> int:
    """
    Run Salesforce prototype smoke tests.

    Returns:
        Process exit code.
    """
    try:
        business_unit_id = require_record_id("Business_Unit__c", BUSINESS_UNIT_NAME)
        cloud_model_id = require_record_id("Cloud_Model__c", CLOUD_MODEL_NAME)
        check_high_sensitivity_rule(business_unit_id)
        check_budget_rule(business_unit_id)
        check_approved_requires_assessment_rule(business_unit_id, cloud_model_id)
        check_approved_requires_model_rule(business_unit_id)
        check_review_task_flow(business_unit_id, cloud_model_id)
    except SalesforceCliError as error:
        print(error)
        print(error.output)
        return 1
    except RuntimeError as error:
        print(error)
        return 1
    print("Smoke tests completed.")
    return 0


def require_record_id(sobject: str, name: str) -> str:
    """
    Find a named seed record.

    Args:
        sobject: Salesforce object API name.
        name: Record name to find.

    Returns:
        Record ID.
    """
    records = query_records(
        f"SELECT Id FROM {sobject} WHERE Name = '{escape_soql_text(name)}' LIMIT 1",
        DEFAULT_ORG_ALIAS,
    )
    if not records:
        raise RuntimeError(f"Missing seed record: {sobject} {name}")
    return str(records[0]["Id"])


def expect_salesforce_error(
    expected_message: str, action_name: str, action: object
) -> None:
    """
    Assert that an action fails with an expected Salesforce error.

    Args:
        expected_message: Error text expected in the redacted output.
        action_name: Human-readable action name.
        action: Callable test action.
    """
    if not callable(action):
        raise RuntimeError(f"Smoke test action is not callable: {action_name}")
    try:
        action()
    except SalesforceCliError as error:
        output_text = str(error.output)
        if expected_message not in output_text:
            message = (
                f"{action_name} failed, but not with expected message: "
                f"{expected_message}"
            )
            raise RuntimeError(message) from error
        print(f"Passed validation check: {action_name}")
        return
    raise RuntimeError(f"{action_name} unexpectedly succeeded.")


def check_high_sensitivity_rule(business_unit_id: str) -> None:
    """
    Verify high sensitivity requests require justification.

    Args:
        business_unit_id: Business unit lookup ID.
    """
    expect_salesforce_error(
        "High sensitivity GenAI requests must include a business justification.",
        "high sensitivity justification",
        lambda: create_record(
            "GenAI_Request__c",
            {
                "Business_Unit__c": business_unit_id,
                "Use_Case_Type__c": "Document Analysis",
                "Data_Sensitivity__c": "High",
                "Estimated_Monthly_Cost__c": 100,
                "Request_Status__c": "Draft",
                "Request_Owner_Email__c": DEMO_EMAIL,
            },
            DEFAULT_ORG_ALIAS,
        ),
    )


def check_budget_rule(business_unit_id: str) -> None:
    """
    Verify monthly cost cannot exceed the business unit budget.

    Args:
        business_unit_id: Business unit lookup ID.
    """
    expect_salesforce_error(
        "Estimated monthly cost cannot exceed the business unit budget limit.",
        "budget limit",
        lambda: create_record(
            "GenAI_Request__c",
            {
                "Business_Unit__c": business_unit_id,
                "Use_Case_Type__c": "Document Analysis",
                "Business_Justification__c": "Intentional invalid cost.",
                "Data_Sensitivity__c": "Medium",
                "Estimated_Monthly_Cost__c": 999999,
                "Request_Status__c": "Draft",
                "Request_Owner_Email__c": DEMO_EMAIL,
            },
            DEFAULT_ORG_ALIAS,
        ),
    )


def check_approved_requires_assessment_rule(
    business_unit_id: str,
    cloud_model_id: str,
) -> None:
    """
    Verify approved requests require at least one risk assessment.

    Args:
        business_unit_id: Business unit lookup ID.
        cloud_model_id: Cloud model lookup ID.
    """
    request_id = create_record(
        "GenAI_Request__c",
        {
            "Business_Unit__c": business_unit_id,
            "Selected_Cloud_Model__c": cloud_model_id,
            "Use_Case_Type__c": "Document Analysis",
            "Business_Justification__c": "Intentional missing assessment.",
            "Data_Sensitivity__c": "Medium",
            "Estimated_Monthly_Cost__c": 100,
            "Request_Status__c": "Draft",
            "Request_Owner_Email__c": DEMO_EMAIL,
        },
        DEFAULT_ORG_ALIAS,
    )
    expect_salesforce_error(
        "A GenAI request cannot be approved without at least one completed risk "
        "assessment.",
        "approved request assessment",
        lambda: update_record(
            "GenAI_Request__c",
            request_id,
            {"Request_Status__c": "Approved"},
            DEFAULT_ORG_ALIAS,
        ),
    )


def check_approved_requires_model_rule(business_unit_id: str) -> None:
    """
    Verify approved requests require a selected cloud model.

    Args:
        business_unit_id: Business unit lookup ID.
    """
    request_id = create_record(
        "GenAI_Request__c",
        {
            "Business_Unit__c": business_unit_id,
            "Use_Case_Type__c": "Document Analysis",
            "Business_Justification__c": "Intentional missing model.",
            "Data_Sensitivity__c": "Medium",
            "Estimated_Monthly_Cost__c": 100,
            "Request_Status__c": "Draft",
            "Request_Owner_Email__c": DEMO_EMAIL,
        },
        DEFAULT_ORG_ALIAS,
    )
    create_record(
        "Risk_Assessment__c",
        {
            "GenAI_Request__c": request_id,
            "Privacy_Risk_Level__c": "Low",
            "Compliance_Risk_Level__c": "Low",
            "Security_Review_Required__c": False,
            "Risk_Comment__c": "Smoke test assessment.",
            "Assessment_Status__c": "Passed",
        },
        DEFAULT_ORG_ALIAS,
    )
    expect_salesforce_error(
        "An approved GenAI request must have a selected cloud model.",
        "approved request model",
        lambda: update_record(
            "GenAI_Request__c",
            request_id,
            {"Request_Status__c": "Approved"},
            DEFAULT_ORG_ALIAS,
        ),
    )


def check_review_task_flow(business_unit_id: str, cloud_model_id: str) -> None:
    """
    Verify submitted requests create a review task.

    Args:
        business_unit_id: Business unit lookup ID.
        cloud_model_id: Cloud model lookup ID.
    """
    request_id = create_record(
        "GenAI_Request__c",
        {
            "Business_Unit__c": business_unit_id,
            "Selected_Cloud_Model__c": cloud_model_id,
            "Use_Case_Type__c": "Document Analysis",
            "Business_Justification__c": "Task automation smoke test.",
            "Data_Sensitivity__c": "Medium",
            "Estimated_Monthly_Cost__c": 100,
            "Request_Status__c": "Submitted",
            "Request_Owner_Email__c": DEMO_EMAIL,
        },
        DEFAULT_ORG_ALIAS,
    )
    tasks = query_records(
        "SELECT Id, Subject, Priority, Status FROM Task "
        f"WHERE WhatId = '{escape_soql_text(request_id)}' "
        "AND Subject = 'Review GenAI Request' LIMIT 1",
        DEFAULT_ORG_ALIAS,
    )
    if not tasks:
        raise RuntimeError("Review task flow did not create a related task.")
    print("Passed automation check: review task creation")


if __name__ == "__main__":
    raise SystemExit(main())
