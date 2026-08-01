import json
import os
import logging
from typing import List, Optional, Union, Any
from pydantic import BaseModel, field_validator
from core.llm_client import LLMClient
from core.config import LLM_MODEL_REASONING, LLM_TEMPERATURE_CREATIVE, GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_API_SCOPES

logger = logging.getLogger(__name__)

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False

class SurveyQuestion(BaseModel):
    title: str = "Question"
    type: str = "text" # multiple_choice, checkbox, text, paragraph, scale
    options: Optional[Union[List[str], Any]] = None

    @field_validator("options", mode="before")
    @classmethod
    def convert_options(cls, v):
        if v is None:
            return None
        if isinstance(v, dict):
            if "min" in v and "max" in v:
                try:
                    min_v = int(v["min"])
                    max_v = int(v["max"])
                    step = int(v.get("step", 1)) or 1
                    return [str(i) for i in range(min_v, max_v + 1, step)]
                except Exception:
                    pass
            return [f"{k}: {val}" for k, val in v.items()]
        if isinstance(v, list):
            return [str(opt) for opt in v]
        if isinstance(v, (int, float, str)):
            return [str(v)]
        return v

class SurveySection(BaseModel):
    title: str = "Section"
    description: Optional[str] = ""
    questions: List[SurveyQuestion] = []

class SurveyForm(BaseModel):
    title: str = "Quick Commerce Ingestion Survey"
    description: Optional[str] = ""
    sections: List[SurveySection] = []
    objective: Optional[str] = None
    hypotheses: Optional[List[str]] = None
    success_criteria: Optional[str] = None
    estimated_time: Optional[str] = None
    suggested_sample_size: Optional[int] = None
    distribution_channels: Optional[List[str]] = None
    expected_insights: Optional[str] = None

PROMPT_TEMPLATE = """You are an expert Product Manager and User Researcher.
Generate a professional, structured survey or interview script tailored specifically to the given product and problem statement.

# INPUT
- Product Name: {product_name}
- Problem Statement: {problem_statement}
- Product Description: {product_description}
- Target Segment: {target_segment}
- Features: {key_features}
- Assumptions to Validate: {assumptions}

# REQUIREMENTS
You must generate exactly 10-15 high-quality user interview questions across 7 logical sections:
1. About the User (Demographics)
2. Current Behaviour (What they do today)
3. Problem Validation (How often they face the issue)
4. Existing Alternatives (Competitors, workarounds)
5. Proposed Solution Validation (Based on the key features)
6. Adoption & Pricing (Willingness to pay, switch)
7. Open Feedback (Concerns, suggestions)

For each question, specify the type (multiple_choice, checkbox, text, paragraph, scale) and options if applicable.
Return the output strictly in the requested JSON format without any extra markdown formatting outside the JSON block.
"""

def generate_survey_structure(project_data: dict) -> SurveyForm:
    client = LLMClient()
    
    prompt = PROMPT_TEMPLATE.format(
        product_name=project_data.get("product_name", "Unknown Product"),
        problem_statement=project_data.get("problem_statement", "N/A"),
        product_description=project_data.get("product_description", "N/A"),
        target_segment=project_data.get("target_segment", "N/A"),
        key_features=project_data.get("key_features", "N/A"),
        assumptions=project_data.get("assumptions", "N/A")
    )
    
    schema_json = SurveyForm.model_json_schema()
    system_prompt = f"Output strictly as a JSON object matching this schema: {json.dumps(schema_json)}"
    
    # Use Llama 3.3 for deep reasoning
    res_json = client.generate(
        system_prompt=system_prompt,
        user_prompt=prompt,
        creative=True
    )
    
    return SurveyForm(**res_json)


def get_google_credentials():
    """
    Returns valid Google Credentials. Priority:
    1. Service Account credentials (GOOGLE_SERVICE_ACCOUNT_JSON env var, service_account.json, or root *.json service key)
    2. Saved user OAuth token (GOOGLE_TOKEN_JSON env var or token.json file)
    3. OAuth client_secret (GOOGLE_CLIENT_SECRET_JSON env var or client_secret.json file)
    """
    from core.config import GOOGLE_CLIENT_SECRET_FILE, GOOGLE_TOKEN_FILE, GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_API_SCOPES
    from google.oauth2.credentials import Credentials as UserCredentials
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    import json
    import glob
    
    auth_errors = []

    # 1. Service Account credentials (Priority #1)
    sa_env = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_env:
        try:
            cleaned_sa = sa_env.strip()
            if (cleaned_sa.startswith("'") and cleaned_sa.endswith("'")) or (cleaned_sa.startswith('"') and cleaned_sa.endswith('"')):
                cleaned_sa = cleaned_sa[1:-1]
            sa_info = json.loads(cleaned_sa)
            logger.info("Authenticated using GOOGLE_SERVICE_ACCOUNT_JSON environment variable.")
            return ServiceAccountCredentials.from_service_account_info(sa_info, scopes=GOOGLE_API_SCOPES)
        except Exception as e:
            err_msg = f"Service Account from GOOGLE_SERVICE_ACCOUNT_JSON env failed: {e}"
            logger.error(err_msg)
            auth_errors.append(err_msg)

    # Check designated service account file or any mcpreviewserver / service_account *.json files
    sa_candidate_files = [
        GOOGLE_SERVICE_ACCOUNT_FILE,
        os.path.join("backend", "credentials", "service_account.json"),
        os.path.join("credentials", "service_account.json")
    ] + glob.glob("mcpreviewserver-*.json") + glob.glob("backend/credentials/*.json")

    for sa_path in sa_candidate_files:
        if sa_path and os.path.exists(sa_path) and os.path.getsize(sa_path) > 0:
            try:
                with open(sa_path, "r", encoding="utf-8") as f:
                    sa_data = json.load(f)
                if isinstance(sa_data, dict) and sa_data.get("type") == "service_account":
                    logger.info(f"Authenticated using Service Account key file: {sa_path}")
                    return ServiceAccountCredentials.from_service_account_file(sa_path, scopes=GOOGLE_API_SCOPES)
            except Exception as e:
                err_msg = f"Service Account file {sa_path} failed: {e}"
                logger.error(err_msg)
                auth_errors.append(err_msg)

    # 2. Check existing user OAuth token (env var or file) as fallback
    token_json_str = os.getenv("GOOGLE_TOKEN_JSON")
    if token_json_str:
        try:
            cleaned_str = token_json_str.strip()
            if (cleaned_str.startswith("'") and cleaned_str.endswith("'")) or (cleaned_str.startswith('"') and cleaned_str.endswith('"')):
                cleaned_str = cleaned_str[1:-1]
            info = json.loads(cleaned_str)
            creds = UserCredentials.from_authorized_user_info(info, GOOGLE_API_SCOPES)
            if creds and creds.valid:
                return creds
            if creds and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                return creds
        except Exception as e:
            err_msg = f"GOOGLE_TOKEN_JSON env var auth failed: {e}"
            logger.error(err_msg)
            auth_errors.append(err_msg)

    if os.path.exists(GOOGLE_TOKEN_FILE):
        try:
            with open(GOOGLE_TOKEN_FILE) as f:
                info = json.load(f)
            creds = UserCredentials.from_authorized_user_info(info, GOOGLE_API_SCOPES)
            if creds and creds.valid:
                return creds
            if creds and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                return creds
        except Exception as e:
            err_msg = f"token.json file auth failed: {e}"
            logger.error(err_msg)
            auth_errors.append(err_msg)

    details = " | ".join(auth_errors) if auth_errors else "No GOOGLE_SERVICE_ACCOUNT_JSON or valid Service Account key file found."
    raise FileNotFoundError(f"Google authentication failed on server: {details}")



def survey_to_google_form_requests(survey: SurveyForm) -> list:
    """
    Converts SurveyForm sections and questions into Google Forms API batchUpdate request items.
    """
    requests = [
        {
            "updateFormInfo": {
                "info": {
                    "title": survey.title,
                    "description": survey.description or ""
                },
                "updateMask": "title,description"
            }
        }
    ]

    index = 0
    for section_idx, section in enumerate(survey.sections):
        # Add page break / section header if not the very first section header
        if section_idx > 0:
            requests.append({
                "createItem": {
                    "item": {
                        "title": section.title,
                        "description": section.description or "",
                        "pageBreakItem": {}
                    },
                    "location": {"index": index}
                }
            })
            index += 1

        # In the first section, insert optional User Name and Email fields if not already present
        if section_idx == 0:
            has_name = any("name" in q.title.lower() for q in section.questions)
            if not has_name:
                requests.append({
                    "createItem": {
                        "item": {
                            "title": "Your Name (Optional)",
                            "questionItem": {
                                "question": {
                                    "required": False,
                                    "textQuestion": {"paragraph": False}
                                }
                            }
                        },
                        "location": {"index": index}
                    }
                })
                index += 1

        for q in section.questions:
            item_data = {
                "title": q.title,
                "questionItem": {
                    "question": {
                        "required": False
                    }
                }
            }

            q_type = (q.type or "").lower()
            options = q.options or []

            if q_type in ["multiple_choice", "radio", "mcq"]:
                item_data["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "RADIO",
                    "options": [{"value": opt} for opt in (options if options else ["Option 1"])]
                }
            elif q_type in ["checkbox", "checkboxes"]:
                item_data["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "CHECKBOX",
                    "options": [{"value": opt} for opt in (options if options else ["Option 1"])]
                }
            elif q_type in ["paragraph", "long_text"]:
                item_data["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": True
                }
            elif q_type in ["scale", "linear_scale", "rating"]:
                item_data["questionItem"]["question"]["scaleQuestion"] = {
                    "low": 1,
                    "high": 5,
                    "lowLabel": "Low",
                    "highLabel": "High"
                }
            else:
                item_data["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": False
                }

            requests.append({
                "createItem": {
                    "item": item_data,
                    "location": {"index": index}
                }
            })
            index += 1

    return requests


def delete_existing_file(drive_service, name: str, mime_type: str, folder_id: str):
    """Search for a file with the same name and mimeType in the folder and delete it to prevent duplication."""
    try:
        query = f"name = '{name}' and '{folder_id}' in parents and mimeType = '{mime_type}' and trashed = false"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get('files', [])
        for f in files:
            drive_service.files().delete(fileId=f['id'], supportsAllDrives=True).execute()
    except Exception:
        pass

def create_google_form(survey: SurveyForm) -> str:
    """
    Creates a real Google Form directly inside the designated Google Drive folder and populates all questions.
    Returns the Form URL on success.
    """
    if not GOOGLE_LIBS_AVAILABLE:
        raise ImportError("google-api-python-client or google-auth is not installed.")
        
    creds = get_google_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    from core.config import GOOGLE_DRIVE_FOLDER_ID
    folder_id = GOOGLE_DRIVE_FOLDER_ID or "1-KqYGsX7eUVmo9ShlXx0i2c0tg8EnbsB"

    # 1. Create file inside target folder via Drive API (deleting old first)
    delete_existing_file(drive_service, survey.title, 'application/vnd.google-apps.form', folder_id)
    file_metadata = {
        'name': survey.title,
        'mimeType': 'application/vnd.google-apps.form',
        'parents': [folder_id]
    }
    file = drive_service.files().create(
        body=file_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()
    form_id = file.get('id')

    # 2. Populate title, description, sections, and questions via Forms batchUpdate
    form_service = build('forms', 'v1', credentials=creds)
    requests = survey_to_google_form_requests(survey)
    
    # Prepend deletes for any default initial items created by Google Forms (e.g. Untitled Question)
    try:
        current_form = form_service.forms().get(formId=form_id).execute()
        current_items = current_form.get('items', [])
        if current_items:
            delete_requests = []
            for _ in range(len(current_items)):
                delete_requests.append({
                    "deleteItem": {
                        "location": {
                            "index": 0
                        }
                    }
                })
            requests = delete_requests + requests
    except Exception as e:
        print(f"Warning: Could not fetch or delete default items: {e}")

    form_service.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests}
    ).execute()
    
    # 3. Set sharing permissions
    try:
        drive_service.permissions().create(
            fileId=form_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        print(f"Warning: Could not set permissions: {e}")
        
    return f"https://docs.google.com/forms/d/{form_id}/edit"


def generate_survey_and_form(project_data: dict) -> dict:
    """
    Main orchestrator for generating the survey and attempting API creation.
    Returns a dict with either 'form_url' or 'markdown_fallback'.
    """
    survey = generate_survey_structure(project_data)
    
    # Try to create real Google Form
    form_url = None
    api_error = None
    try:
        form_url = create_google_form(survey)
    except Exception as e:
        api_error = str(e)
        
    # Generate markdown fallback
    md = f"# {survey.title}\n\n{survey.description}\n\n"
    for sec in survey.sections:
        md += f"## {sec.title}\n_{sec.description}_\n\n"
        for q in sec.questions:
            md += f"**{q.title}** ({q.type})\n"
            if q.options:
                for opt in q.options:
                    md += f"- {opt}\n"
            md += "\n"
            
    # Save to D drive
    product_name = project_data.get("product_name", "Unknown")
    safe_product_name = "".join(c for c in product_name if c.isalnum() or c in " _-").strip().replace(" ", "_")
    d_drive_folder = f"D:\\{safe_product_name}_Project"
    
    try:
        os.makedirs(d_drive_folder, exist_ok=True)
        file_path = os.path.join(d_drive_folder, "survey_interview_questions.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md)
    except Exception as e:
        print(f"Warning: Could not save to D drive: {e}")
            
    return {
        "success": True,
        "form_url": form_url,
        "api_error": api_error,
        "markdown_fallback": md,
        "extra_features": {
            "objective": survey.objective,
            "hypotheses": survey.hypotheses,
            "success_criteria": survey.success_criteria,
            "estimated_time": survey.estimated_time,
            "suggested_sample_size": survey.suggested_sample_size,
            "distribution_channels": survey.distribution_channels,
            "expected_insights": survey.expected_insights
        }
    }
