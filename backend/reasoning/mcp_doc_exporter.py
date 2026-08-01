import logging
import json
from reasoning.form_generator import get_google_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

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
            logger.info(f"Deleted duplicate file: {f['name']} (ID: {f['id']})")
    except Exception as e:
        logger.warning(f"Error checking/deleting duplicate file '{name}': {e}")

def export_strategy_deep_dive_doc(strategy_data: dict) -> str:
    """
    Formats Strategy Deep Dive results into a Google Doc and saves it inside target Drive folder.
    Returns the Google Doc edit URL on success.
    """
    if isinstance(strategy_data, str):
        try:
            strategy_data = json.loads(strategy_data)
        except Exception:
            strategy_data = {}
    if not isinstance(strategy_data, dict):
        strategy_data = {}

    creds = get_google_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    
    from core.config import GOOGLE_DRIVE_FOLDER_ID
    folder_id = GOOGLE_DRIVE_FOLDER_ID or "1-KqYGsX7eUVmo9ShlXx0i2c0tg8EnbsB"

    # 1. Create file inside target folder
    title = "Pulse Intelligence — Strategy Deep Dive Report"
    delete_existing_file(drive_service, title, 'application/vnd.google-apps.document', folder_id)
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    from googleapiclient.errors import HttpError
    try:
        file = drive_service.files().create(
            body=file_metadata,
            fields='id',
            supportsAllDrives=True
        ).execute()
        doc_id = file.get('id')
    except HttpError as err:
        if "storageQuotaExceeded" in str(err):
            raise RuntimeError(
                "Google Service Accounts have 0 MB storage quota in personal Gmail Drive folders. "
                "To export to Google Docs/Slides, please keep GOOGLE_TOKEN_JSON set in Render Environment Variables, or use a Google Workspace Shared Drive."
            )
        raise err

    # 2. Build document text
    doc_text = f"# {title}\n\n"
    steps = strategy_data.get("steps", {})
    
    for step_id, step_info in steps.items():
        step_title = step_info.get("title", step_id)
        doc_text += f"\n## {step_id.upper()}: {step_title}\n"
        data = step_info.get("data", {})
        if isinstance(data, dict):
            for k, v in data.items():
                fmt_key = k.replace("_", " ").title()
                if isinstance(v, list):
                    doc_text += f"**{fmt_key}:**\n"
                    for item in v:
                        doc_text += f"- {json.dumps(item) if isinstance(item, dict) else item}\n"
                else:
                    doc_text += f"**{fmt_key}:** {json.dumps(v) if isinstance(v, dict) else v}\n"
        else:
            doc_text += f"{data}\n"
        doc_text += "\n"

    # Insert content into doc
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": doc_text
                    }
                }
            ]
        }
    ).execute()

    # Set reader permissions
    try:
        drive_service.permissions().create(
            fileId=doc_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        logger.warning(f"Could not set public permissions on doc: {e}")

    return f"https://docs.google.com/document/d/{doc_id}/edit"

def hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    """Helper to convert hex color strings (e.g. #3b82f6) into Google Slides RGB floats."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c*2 for c in hex_str)
    try:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return r, g, b
    except Exception:
        return 0.1, 0.1, 0.2  # default dark navy

def export_strategy_deep_dive_slides(board_deck: dict) -> str:
    """
    Formats the synthesized 10-slide Board Presentation into a Google Slides presentation.
    Generates slides programmatically from scratch using custom brand coloring.
    """
    if isinstance(board_deck, str):
        try:
            board_deck = json.loads(board_deck)
        except Exception:
            board_deck = {}
    if not isinstance(board_deck, dict):
        board_deck = {}

    creds = get_google_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    slides_service = build('slides', 'v1', credentials=creds)

    from core.config import GOOGLE_DRIVE_FOLDER_ID
    folder_id = GOOGLE_DRIVE_FOLDER_ID or "1-KqYGsX7eUVmo9ShlXx0i2c0tg8EnbsB"
    app_name = board_deck.get("app_name", "Blinkit")
    title = f"NL {app_name}"
    
    slides = board_deck.get("slides", [])
    if not isinstance(slides, list):
        slides = []
    primary_color_hex = board_deck.get("primary_color", "#3b82f6")
    secondary_color_hex = board_deck.get("secondary_color", "#10b981")
    
    brand_r, brand_g, brand_b = hex_to_rgb(primary_color_hex)

    def serialize_board_slide_body(slide):
        if not isinstance(slide, dict):
            return str(slide or "")
        lines = []
        skip_keys = {"title", "headline", "slide_number", "type", "speaker_notes"}
        for k, v in slide.items():
            if k in skip_keys:
                continue
            fmt_key = k.replace("_", " ").title()
            if isinstance(v, list):
                lines.append(f"{fmt_key}:")
                for item in v[:5]:
                    lines.append(f"- {item}")
            else:
                lines.append(f"{fmt_key}: {v}")
        return "\n".join(lines)

    # 1. Create a blank presentation
    delete_existing_file(drive_service, title, 'application/vnd.google-apps.presentation', folder_id)
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.presentation',
        'parents': [folder_id]
    }
    try:
        file = drive_service.files().create(
            body=file_metadata,
            fields='id',
            supportsAllDrives=True
        ).execute()
        pres_id = file.get('id')
    except HttpError as err:
        if "storageQuotaExceeded" in str(err):
            raise RuntimeError(
                "Google Service Accounts have 0 MB storage quota in personal Gmail Drive folders. "
                "To export to Google Docs/Slides, please keep GOOGLE_TOKEN_JSON set in Render Environment Variables, or use a Google Workspace Shared Drive."
            )
        raise err

    requests = []
    
    # Create blank slides (except slide 0)
    for idx in range(1, len(slides)):
        requests.append({
            'createSlide': {
                'objectId': f"slide_{idx}",
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        })

    if requests:
        slides_service.presentations().batchUpdate(presentationId=pres_id, body={'requests': requests}).execute()

    presentation = slides_service.presentations().get(presentationId=pres_id).execute()
    updated_slides = presentation.get('slides', [])
    style_requests = []

    # Premium Slate Theme
    bg_r, bg_g, bg_b = 0.05, 0.07, 0.12

    for idx, slide in enumerate(slides):
        if idx >= len(updated_slides):
            continue
            
        slide_obj = updated_slides[idx]
        slide_id = slide_obj.get('objectId')

        # Clear default placeholder textboxes on the first slide
        if idx == 0:
            for el in slide_obj.get('pageElements', []):
                style_requests.append({
                    'deleteObject': {
                        'objectId': el.get('objectId')
                    }
                })

        # Set slide background to dark slate
        style_requests.append({
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'pageBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': bg_r, 'green': bg_g, 'blue': bg_b
                                }
                            }
                        }
                    }
                },
                'fields': 'pageBackgroundFill.solidFill.color'
            }
        })

        slide_num = slide.get('slide_number', idx + 1)
        slide_title = slide.get('title', f"Slide {slide_num}")
        slide_headline = slide.get('headline', '')

        # Accent Brand Bar
        accent_bar_id = f"accent_{slide_id}"
        style_requests.append({
            'createShape': {
                'objectId': accent_bar_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': 6, 'unit': 'PT'},
                        'width': {'magnitude': 640, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': 40, 'translateY': 20,
                        'unit': 'PT'
                    }
                }
            }
        })
        style_requests.append({
            'updateShapeProperties': {
                'objectId': accent_bar_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': brand_r, 'green': brand_g, 'blue': brand_b
                                }
                            }
                        }
                    },
                    'outline': {
                        'propertyState': 'NOT_RENDERED'
                    }
                },
                'fields': 'shapeBackgroundFill.solidFill.color,outline.propertyState'
            }
        })

        # Title Box
        title_box_id = f"title_{slide_id}"
        style_requests.append({
            'createShape': {
                'objectId': title_box_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': 70, 'unit': 'PT'},
                        'width': {'magnitude': 640, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': 40, 'translateY': 35,
                        'unit': 'PT'
                    }
                }
            }
        })
        title_text = f"{slide_title.upper()}\n{slide_headline}"
        style_requests.append({
            'insertText': {
                'objectId': title_box_id,
                'text': title_text
            }
        })
        style_requests.append({
            'updateTextStyle': {
                'objectId': title_box_id,
                'style': {
                    'fontFamily': 'Georgia',
                    'fontSize': {'magnitude': 18, 'unit': 'PT'},
                    'bold': True,
                    'foregroundColor': {
                        'opaqueColor': {
                            'rgbColor': {
                                'red': 1.0, 'green': 1.0, 'blue': 1.0
                            }
                        }
                    }
                },
                'fields': 'fontFamily,fontSize,bold,foregroundColor'
            }
        })

        # Determine layouts dynamically based on slide types
        slide_type = slide.get('type', 'general')
        
        left_lines = []
        right_lines = []
        
        left_title = "Focus Area"
        right_title = "Evidence & Action"
        
        col3_data = [] # List of tuples: (col_title, list_of_lines)
        
        # Format values to strings cleanly
        def val_to_str(val):
            if isinstance(val, list):
                return "\n".join(f"- {item}" for item in val[:4])
            return str(val or "")
        
        if slide_type == 'market_gap':
            left_title = "Platform Market Comparison"
            mg_table = slide.get('market_gap_table', [])
            if isinstance(mg_table, list):
                for row in mg_table[:5]:
                    if isinstance(row, dict):
                        left_lines.append(f"• {row.get('platform')}: {row.get('offer')} (Missing: {row.get('missing')})")
            why_solve = slide.get('why_solve_first', [])
            if why_solve:
                left_lines.append("\nWhy Solve First:")
                left_lines.extend([f"- {w}" for w in (why_solve if isinstance(why_solve, list) else [why_solve])])
                
            right_title = "Market Size & Key Statistics"
            stats = slide.get('stats', {})
            if isinstance(stats, dict):
                for k, v in stats.items():
                    right_lines.append(f"• {k.replace('_', ' ').title()}: {v}")
            bullets = slide.get('bullets', [])
            if bullets:
                right_lines.append("\nStrategic Context:")
                right_lines.extend([f"- {b}" for b in (bullets if isinstance(bullets, list) else [bullets])])

        elif slide_type == 'user_research':
            left_title = "Research Findings & Sentiment"
            findings = slide.get('findings', {})
            if isinstance(findings, dict):
                left_lines.append(f"• Analyzed Reviews: {findings.get('total_analyzed')}")
                left_lines.append(f"• LLM Labeled: {findings.get('llm_labeled')}")
                left_lines.append(f"• Discovery Pain Rate: {findings.get('discovery_pain_rate')}")
                left_lines.append(f"• Primary Friction: {findings.get('top_theme')}")
            sent = slide.get('sentiment', {})
            if isinstance(sent, dict):
                left_lines.append(f"\nSentiment Breakdown:")
                left_lines.append(f"Negative: {sent.get('negative')} | Neutral: {sent.get('neutral')} | Positive: {sent.get('positive')}")
                
            right_title = "Cited Verbatim User Quotes"
            quotes = slide.get('cited_quotes', [])
            if isinstance(quotes, list):
                for q in quotes[:4]:
                    if isinstance(q, dict):
                        right_lines.append(f"\"{q.get('quote')}\"")
                        right_lines.append(f"  — {q.get('source')}\n")
            bullets = slide.get('bullets', [])
            if bullets:
                right_lines.extend([f"- {b}" for b in (bullets if isinstance(bullets, list) else [bullets])[:3]])

        elif slide_type == 'personas_journey':
            left_title = "Target Segment Personas"
            personas = slide.get('personas', [])
            if isinstance(personas, list):
                for p in personas[:2]:
                    if isinstance(p, dict):
                        left_lines.append(f"👤 {p.get('name')} ({p.get('title')})")
                        left_lines.append(f"  Trust Pattern: {p.get('trust_pattern')}")
                        left_lines.append(f"  Unmet Need: {p.get('unmet_need')}")
                        left_lines.append(f"  Behavioral Trap: {p.get('behavioral_trap')}")
                        left_lines.append(f"  Quote: \"{p.get('quote')}\"\n")
                        
            right_title = "User Journey Habit Loop"
            uj = slide.get('user_journey', [])
            if isinstance(uj, list):
                for idx, st in enumerate(uj[:5]):
                    if isinstance(st, dict):
                        right_lines.append(f"Stage {idx+1}: {st.get('stage')} — {st.get('behavior')}")
                        right_lines.append(f"  Friction: {st.get('friction')}\n")

        elif slide_type == 'problem_framing':
            val_gen = slide.get('value_generated', {})
            if not isinstance(val_gen, dict): val_gen = {}
            why_now = slide.get('why_now', {})
            if not isinstance(why_now, dict): why_now = {}
            evidences = slide.get('evidences', [])
            
            col3_data = [
                ("1. Problem & Cohort", [
                    f"TRUE PROBLEM:\n{val_to_str(slide.get('true_problem'))}\n",
                    f"TARGET COHORT:\n{val_to_str(slide.get('target_cohort'))}"
                ]),
                ("2. Evidence & Value", [
                    f"EVIDENCES:\n" + "\n".join(f"- {e}" for e in (evidences if isinstance(evidences, list) else [evidences])[:3]),
                    f"\nVALUE GENERATED:\nUser: {val_gen.get('for_user')}\nPlatform: {val_gen.get('for_platform')}"
                ]),
                ("3. Urgency (Why Now)", [
                    f"Saturation: {why_now.get('saturation')}\n",
                    f"AI Unlock: {why_now.get('ai_unlock')}\n",
                    f"First-Mover: {why_now.get('first_mover')}"
                ])
            ]

        elif slide_type == 'hypotheses_rice':
            left_title = "Hypotheses Evaluated"
            hyps = slide.get('hypotheses', [])
            if isinstance(hyps, list):
                for h in hyps[:4]:
                    if isinstance(h, dict):
                        chosen = " [CHOSEN WINNER]" if h.get('id') == 'H1' else ""
                        left_lines.append(f"• {h.get('id')}: {h.get('name')}{chosen}")
                        left_lines.append(f"  {h.get('statement')}\n")
                        
            right_title = "RICE Framework & Rationale"
            rice = slide.get('rice_scores', [])
            if isinstance(rice, list):
                for r in rice[:4]:
                    if isinstance(r, dict):
                        left_r = f"{r.get('hypothesis_id')}: Reach {r.get('reach')}/10 | Impact {r.get('impact')}/10 | Conf {r.get('confidence')}/10 | Effort {r.get('effort')}/10 => SCORE {r.get('score')}"
                        right_lines.append(left_r)
            win = slide.get('winning_rationale')
            if win:
                right_lines.append(f"\nWinning Rationale:\n{win}")

        elif slide_type == 'solution_comparison':
            left_title = "Evaluated Solutions (S1–S4)"
            sols = slide.get('solutions', [])
            if isinstance(sols, list):
                for s in sols[:4]:
                    if isinstance(s, dict):
                        left_lines.append(f"• {s.get('id')}: {s.get('name')} [{s.get('status')}]")
                        left_lines.append(f"  Desc: {s.get('description')}")
                        left_lines.append(f"  Feedback: \"{s.get('feedback')}\"\n")
                        
            right_title = "Trade-off Justifications"
            vs = slide.get('vs_comparison', [])
            if isinstance(vs, list):
                for v in vs[:4]:
                    if isinstance(v, dict):
                        right_lines.append(f"• vs {v.get('against')}: {v.get('justification')}\n")

        elif slide_type == 'mvp_spec':
            left_title = "MVP Specifications & Trust Cues"
            bullets = slide.get('bullets', [])
            if bullets:
                left_lines.extend([f"• {b}" for b in (bullets if isinstance(bullets, list) else [bullets])])
            cues = slide.get('trust_cues', [])
            if cues:
                left_lines.append("\nConfigured Trust Cues:")
                left_lines.extend([f"- {c}" for c in (cues if isinstance(cues, list) else [cues])])
                
            right_title = "MVP Screen Mapping Spec"
            screens = slide.get('screens', [])
            if isinstance(screens, list):
                for idx, scr in enumerate(screens[:5]):
                    if isinstance(scr, dict):
                        right_lines.append(f"{idx+1}. {scr.get('name')}")
                        right_lines.append(f"   Spec: {scr.get('spec')}\n")

        elif slide_type == 'data_flow_edges':
            left_title = "System Pipelines & Nudges"
            df = slide.get('data_flow', {})
            if isinstance(df, dict):
                left_lines.append(f"① Review Engine:\n{df.get('review_engine')}\n")
                left_lines.append(f"② Product Engine:\n{df.get('product_engine')}\n")
            nudges = slide.get('nudges', [])
            if nudges:
                left_lines.append("Behavioral Nudges:")
                left_lines.extend([f"- {n}" for n in (nudges if isinstance(nudges, list) else [nudges])[:3]])
                
            right_title = "Edge Cases & Mitigations"
            edges = slide.get('edge_cases', [])
            if isinstance(edges, list):
                for ec in edges[:4]:
                    if isinstance(ec, dict):
                        right_lines.append(f"• {ec.get('id')}: {ec.get('title')}")
                        right_lines.append(f"  → Mitigation: {ec.get('mitigation')}\n")

        elif slide_type == 'metrics_indicators':
            left_title = "North Star Metric"
            ns = slide.get('north_star', {})
            if isinstance(ns, dict):
                left_lines.append(f"★ {ns.get('name')}")
                left_lines.append(f"Target Shift: {ns.get('target')}")
                left_lines.append(f"Definition:\n{ns.get('definition')}\n")
                
            right_title = "Leading Indicators & Actions"
            lis = slide.get('leading_indicators', [])
            if isinstance(lis, list):
                for li in lis[:3]:
                    if isinstance(li, dict):
                        right_lines.append(f"• {li.get('name')} (Target: {li.get('target')})")
                        right_lines.append(f"  Proves: {li.get('proves')}")
                        right_lines.append(f"  Below Target: {li.get('below_target_action')}\n")

        elif slide_type == 'failure_mitigations':
            left_title = "Failure Modes & Severity"
            failures = slide.get('failures', [])
            if isinstance(failures, list):
                for f in failures[:4]:
                    if isinstance(f, dict):
                        left_lines.append(f"• [{f.get('severity')}] {f.get('risk')}")
                        left_lines.append(f"  Handling: {f.get('handling')}\n")
            msg = slide.get('closing_message')
            if msg:
                left_lines.append(f"Note: \"{msg}\"")
                
            right_title = "Guardrails & Risk Thresholds"
            guardrails = slide.get('guardrails', [])
            if isinstance(guardrails, list):
                for g in guardrails[:4]:
                    if isinstance(g, dict):
                        right_lines.append(f"• {g.get('name')}: {g.get('threshold')}")
                        right_lines.append(f"  Purpose: {g.get('purpose')}\n")

        else:
            left_title = "Strategic Synthesis"
            left_lines = [serialize_board_slide_body(slide)[:250]]
            right_title = "Supporting Evidence"
            right_lines = [serialize_board_slide_body(slide)[250:600]]

        # Render layout shapes
        if col3_data:
            # 3 Column layout: width 195pt each, translateX at 40, 250, 460
            for col_idx, (col_title, col_lines) in enumerate(col3_data):
                col_x = 40 + col_idx * 210
                col_width = 195
                card_id = f"card_{slide_id}_{col_idx}"
                txt_id = f"txt_{card_id}"
                
                style_requests.append({
                    'createShape': {
                        'objectId': card_id,
                        'shapeType': 'ROUND_RECTANGLE',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'height': {'magnitude': 220, 'unit': 'PT'},
                                'width': {'magnitude': col_width, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1, 'scaleY': 1,
                                'translateX': col_x, 'translateY': 115,
                                'unit': 'PT'
                            }
                        }
                    }
                })
                style_requests.append({
                    'updateShapeProperties': {
                        'objectId': card_id,
                        'shapeProperties': {
                            'shapeBackgroundFill': {
                                'solidFill': {
                                    'color': {
                                        'rgbColor': {
                                            'red': 0.08, 'green': 0.11, 'blue': 0.18
                                        }
                                    }
                                }
                            },
                            'outline': {
                                'outlineFill': {
                                    'solidFill': {
                                        'color': {
                                            'rgbColor': {
                                                'red': 0.18, 'green': 0.22, 'blue': 0.33
                                            }
                                        }
                                    }
                                },
                                'weight': {'magnitude': 1, 'unit': 'PT'}
                            }
                        },
                        'fields': 'shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color,outline.weight'
                    }
                })
                
                style_requests.append({
                    'createShape': {
                        'objectId': txt_id,
                        'shapeType': 'TEXT_BOX',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'height': {'magnitude': 200, 'unit': 'PT'},
                                'width': {'magnitude': col_width - 16, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1, 'scaleY': 1,
                                'translateX': col_x + 8, 'translateY': 123,
                                'unit': 'PT'
                            }
                        }
                    }
                })
                
                full_col_text = f"{col_title.upper()}\n\n" + "\n".join(col_lines)
                style_requests.append({
                    'insertText': {
                        'objectId': txt_id,
                        'text': full_col_text
                    }
                })
                header_len = len(col_title) + 2
                if header_len > 0 and len(full_col_text) > 0:
                    style_requests.append({
                        'updateTextStyle': {
                            'objectId': txt_id,
                            'style': {
                                'fontFamily': 'Georgia',
                                'fontSize': {'magnitude': 15, 'unit': 'PT'},
                                'bold': True,
                                'foregroundColor': {
                                    'opaqueColor': {
                                        'rgbColor': {
                                            'red': brand_r, 'green': brand_g, 'blue': brand_b
                                        }
                                    }
                                }
                            },
                            'textRange': {
                                'type': 'FIXED_RANGE',
                                'startIndex': 0,
                                'endIndex': min(header_len, len(full_col_text))
                            },
                            'fields': 'fontFamily,fontSize,bold,foregroundColor'
                        }
                    })
                if len(full_col_text) > header_len:
                    style_requests.append({
                        'updateTextStyle': {
                            'objectId': txt_id,
                            'style': {
                                'fontFamily': 'Arial',
                                'fontSize': {'magnitude': 14, 'unit': 'PT'},
                                'foregroundColor': {
                                    'opaqueColor': {
                                        'rgbColor': {
                                            'red': 0.85, 'green': 0.88, 'blue': 0.93
                                        }
                                    }
                                }
                            },
                            'textRange': {
                                'type': 'FIXED_RANGE',
                                'startIndex': header_len,
                                'endIndex': len(full_col_text)
                            },
                            'fields': 'fontFamily,fontSize,foregroundColor'
                        }
                    })
        else:
            # 2 Column layout: Left at translateX 40, Right at translateX 365
            columns = [(left_title, left_lines, 40), (right_title, right_lines, 365)]
            for col_idx, (c_title, c_lines, c_x) in enumerate(columns):
                c_width = 300
                card_id = f"card_{slide_id}_{col_idx}"
                txt_id = f"txt_{card_id}"
                
                style_requests.append({
                    'createShape': {
                        'objectId': card_id,
                        'shapeType': 'ROUND_RECTANGLE',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'height': {'magnitude': 220, 'unit': 'PT'},
                                'width': {'magnitude': c_width, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1, 'scaleY': 1,
                                'translateX': c_x, 'translateY': 115,
                                'unit': 'PT'
                            }
                        }
                    }
                })
                style_requests.append({
                    'updateShapeProperties': {
                        'objectId': card_id,
                        'shapeProperties': {
                            'shapeBackgroundFill': {
                                'solidFill': {
                                    'color': {
                                        'rgbColor': {
                                            'red': 0.08, 'green': 0.11, 'blue': 0.18
                                        }
                                    }
                                }
                            },
                            'outline': {
                                'outlineFill': {
                                    'solidFill': {
                                        'color': {
                                            'rgbColor': {
                                                'red': 0.18, 'green': 0.22, 'blue': 0.33
                                            }
                                        }
                                    }
                                },
                                'weight': {'magnitude': 1, 'unit': 'PT'}
                            }
                        },
                        'fields': 'shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color,outline.weight'
                    }
                })
                
                style_requests.append({
                    'createShape': {
                        'objectId': txt_id,
                        'shapeType': 'TEXT_BOX',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'height': {'magnitude': 200, 'unit': 'PT'},
                                'width': {'magnitude': c_width - 20, 'unit': 'PT'}
                            },
                            'transform': {
                                'scaleX': 1, 'scaleY': 1,
                                'translateX': c_x + 10, 'translateY': 123,
                                'unit': 'PT'
                            }
                        }
                    }
                })
                
                full_col_text = f"{c_title.upper()}\n\n" + "\n".join(c_lines)
                style_requests.append({
                    'insertText': {
                        'objectId': txt_id,
                        'text': full_col_text
                    }
                })
                header_len = len(c_title) + 2
                if header_len > 0 and len(full_col_text) > 0:
                    style_requests.append({
                        'updateTextStyle': {
                            'objectId': txt_id,
                            'style': {
                                'fontFamily': 'Georgia',
                                'fontSize': {'magnitude': 15, 'unit': 'PT'},
                                'bold': True,
                                'foregroundColor': {
                                    'opaqueColor': {
                                        'rgbColor': {
                                            'red': brand_r, 'green': brand_g, 'blue': brand_b
                                        }
                                    }
                                }
                            },
                            'textRange': {
                                'type': 'FIXED_RANGE',
                                'startIndex': 0,
                                'endIndex': min(header_len, len(full_col_text))
                            },
                            'fields': 'fontFamily,fontSize,bold,foregroundColor'
                        }
                    })
                if len(full_col_text) > header_len:
                    style_requests.append({
                        'updateTextStyle': {
                            'objectId': txt_id,
                            'style': {
                                'fontFamily': 'Arial',
                                'fontSize': {'magnitude': 14, 'unit': 'PT'},
                                'foregroundColor': {
                                    'opaqueColor': {
                                        'rgbColor': {
                                            'red': 0.85, 'green': 0.88, 'blue': 0.93
                                        }
                                    }
                                }
                            },
                            'textRange': {
                                'type': 'FIXED_RANGE',
                                'startIndex': header_len,
                                'endIndex': len(full_col_text)
                            },
                            'fields': 'fontFamily,fontSize,foregroundColor'
                        }
                    })

    if style_requests:
        slides_service.presentations().batchUpdate(presentationId=pres_id, body={'requests': style_requests}).execute()

    try:
        drive_service.permissions().create(
            fileId=pres_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        logger.warning(f"Could not set public permissions on presentation: {e}")

    return f"https://docs.google.com/presentation/d/{pres_id}/edit"


def export_executive_deck_slides(deck_data: dict) -> str:
    """
    Formats Executive Deck results into a Google Slides presentation.
    Bypasses static template copying and constructs branded decks programmatically from scratch.
    """
    if isinstance(deck_data, str):
        try:
            deck_data = json.loads(deck_data)
        except Exception:
            deck_data = {}
    if not isinstance(deck_data, dict):
        deck_data = {}

    return export_strategy_deep_dive_slides(deck_data)

    # Fallback to creating blank presentation
    delete_existing_file(drive_service, title, 'application/vnd.google-apps.presentation', folder_id)
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.presentation',
        'parents': [folder_id]
    }
    file = drive_service.files().create(
        body=file_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()
    pres_id = file.get('id')

    requests = []

    for idx, slide in enumerate(slides):
        slide_title = slide.get('title', f"Slide {idx+1}")
        slide_headline = slide.get('headline', '')
        slide_body = get_slide_content(slide)
        
        metrics_str = ""
        metrics = slide.get('key_metrics', [])
        if metrics:
            metrics_str = "\n\nKEY METRICS:\n" + "\n".join(f"- {m.get('label')}: {m.get('value')}" for m in metrics)

        full_content = f"{slide_headline}\n\n{slide_body}{metrics_str}"

        if idx == 0:
            presentation = slides_service.presentations().get(presentationId=pres_id).execute()
            existing_slides = presentation.get('slides', [])
            if existing_slides:
                elements = existing_slides[0].get('pageElements', [])
                title_shape = next((el for el in elements if el.get('shape', {}).get('placeholder', {}).get('type') in ['CENTERED_TITLE', 'TITLE']), None)
                sub_shape = next((el for el in elements if el.get('shape', {}).get('placeholder', {}).get('type') == 'SUBTITLE'), None)
                
                if title_shape:
                    requests.append({
                        'insertText': {
                            'objectId': title_shape.get('objectId'),
                            'text': slide_title
                        }
                    })
                if sub_shape:
                    requests.append({
                        'insertText': {
                            'objectId': sub_shape.get('objectId'),
                            'text': full_content
                        }
                    })
        else:
            requests.append({
                'createSlide': {
                    'objectId': f"slide_{idx}",
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY'
                    }
                }
            })

    if requests:
        slides_service.presentations().batchUpdate(presentationId=pres_id, body={'requests': requests}).execute()

    presentation = slides_service.presentations().get(presentationId=pres_id).execute()
    updated_slides = presentation.get('slides', [])
    text_requests = []

    for idx, slide in enumerate(slides):
        if idx == 0 or idx >= len(updated_slides):
            continue
        
        slide_title = slide.get('title', f"Slide {idx+1}")
        slide_headline = slide.get('headline', '')
        slide_body = get_slide_content(slide)
        
        metrics_str = ""
        metrics = slide.get('key_metrics', [])
        if metrics:
            metrics_str = "\n\nKEY METRICS:\n" + "\n".join(f"- {m.get('label')}: {m.get('value')}" for m in metrics)

        full_content = f"{slide_headline}\n\n{slide_body}{metrics_str}"

        target_slide = updated_slides[idx]
        elements = target_slide.get('pageElements', [])
        title_shape = next((el for el in elements if el.get('shape', {}).get('placeholder', {}).get('type') in ['TITLE', 'CENTERED_TITLE']), None)
        body_shape = next((el for el in elements if el.get('shape', {}).get('placeholder', {}).get('type') in ['BODY', 'SUBTITLE', 'OBJECT']), None)

        # Fallback if specific placeholder type is not found
        shapes = [el for el in elements if 'shape' in el]
        if not title_shape and shapes:
            title_shape = shapes[0]
        if not body_shape and len(shapes) > 1:
            body_shape = next((s for s in shapes if s.get('objectId') != (title_shape.get('objectId') if title_shape else None)), None)

        if title_shape:
            text_requests.append({
                'insertText': {
                    'objectId': title_shape.get('objectId'),
                    'text': slide_title
                }
            })
        if body_shape:
            text_requests.append({
                'insertText': {
                    'objectId': body_shape.get('objectId'),
                    'text': full_content
                }
            })

    if text_requests:
        slides_service.presentations().batchUpdate(presentationId=pres_id, body={'requests': text_requests}).execute()

    try:
        drive_service.permissions().create(
            fileId=pres_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        logger.warning(f"Could not set public permissions on presentation: {e}")

    return f"https://docs.google.com/presentation/d/{pres_id}/edit"


