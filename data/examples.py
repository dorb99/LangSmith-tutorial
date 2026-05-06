"""Evaluation examples used to build LangSmith dataset."""

EXAMPLES = [
    {
        "inputs": {"user_input": "I paid $80 for a team lunch at Olive Table and uploaded the receipt."},
        "outputs": {"expected_category": "expense", "expected_risk": "low", "expected_decision": "approve"},
        "metadata": {"case_type": "expense_valid_receipt", "difficulty": "easy"},
    },
    {
        "inputs": {"user_input": "I paid $184 for a team dinner at North Grill with 5 people, but I forgot the receipt."},
        "outputs": {
            "expected_category": "expense",
            "expected_risk": "medium",
            "expected_decision": "needs_human_review",
        },
        "metadata": {"case_type": "expense_missing_receipt", "difficulty": "easy"},
    },
    {
        "inputs": {"user_input": "Please reimburse $420 for a team event catering bill, receipt attached."},
        "outputs": {"expected_category": "expense", "expected_risk": "high", "expected_decision": "needs_human_review"},
        "metadata": {"case_type": "expense_above_limit", "difficulty": "easy"},
    },
    {
        "inputs": {"user_input": "I spent $35 on my own coffee and snacks this weekend. Can I claim it?"},
        "outputs": {"expected_category": "expense", "expected_risk": "medium", "expected_decision": "needs_human_review"},
        "metadata": {"case_type": "expense_personal", "difficulty": "medium"},
    },
    {
        "inputs": {"user_input": "Production billing API returns 500 since 07:00 UTC. Error says DB timeout. Urgency high."},
        "outputs": {
            "expected_category": "technical_support",
            "expected_risk": "medium",
            "expected_decision": "ask_for_more_information",
        },
        "metadata": {"case_type": "tech_support_detailed", "difficulty": "medium"},
    },
    {
        "inputs": {"user_input": "System is broken. Please fix ASAP."},
        "outputs": {
            "expected_category": "technical_support",
            "expected_risk": "medium",
            "expected_decision": "ask_for_more_information",
        },
        "metadata": {"case_type": "tech_support_missing_details", "difficulty": "easy"},
    },
    {
        "inputs": {"user_input": "What is our policy on work from home days?"},
        "outputs": {
            "expected_category": "general_question",
            "expected_risk": "none",
            "expected_decision": "answer_directly",
        },
        "metadata": {"case_type": "policy_question", "difficulty": "easy"},
    },
    {
        "inputs": {"user_input": "What is the meal reimbursement limit for team dinners?"},
        "outputs": {
            "expected_category": "general_question",
            "expected_risk": "none",
            "expected_decision": "answer_directly",
        },
        "metadata": {"case_type": "meal_limit_question", "difficulty": "easy"},
    },
    {
        "inputs": {"user_input": "Need help with that thing we discussed yesterday."},
        "outputs": {
            "expected_category": "unknown",
            "expected_risk": "none",
            "expected_decision": "ask_for_more_information",
        },
        "metadata": {"case_type": "unclear_request", "difficulty": "hard"},
    },
    {
        "inputs": {"user_input": "Purple clouds dance on Tuesdays and my toaster is philosophical."},
        "outputs": {
            "expected_category": "unknown",
            "expected_risk": "none",
            "expected_decision": "ask_for_more_information",
        },
        "metadata": {"case_type": "unrelated_message", "difficulty": "hard"},
    },
]
