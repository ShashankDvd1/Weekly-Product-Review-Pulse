def push_to_google_docs(app_name: str, report_data: list):
    """
    STUB: Simulates appending the weekly report as a new section to a Google Doc.
    In the final MCP implementation, this would trigger the dedicated Google Docs MCP server.
    """
    print(f"[MCP STUB - Google Docs] Appending {len(report_data)} themes to doc for {app_name}")
    return {"status": "success", "doc_url": f"https://docs.google.com/document/d/stub_{app_name}"}

def push_to_gmail(app_name: str, report_data: list, team_category: str = None):
    """
    STUB: Simulates sending an email via Gmail MCP. 
    If team_category is provided, it only emails that specific team.
    """
    target = team_category if team_category else "All Stakeholders"
    print(f"[MCP STUB - Gmail] Drafting email to {target} for {app_name}...")
    return {"status": "success", "email_id": f"stub_email_{target.replace(' ', '_')}"}
