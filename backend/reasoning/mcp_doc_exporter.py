import logging
import json
from reasoning.form_generator import get_google_credentials
from googleapiclient.discovery import build

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
    file = drive_service.files().create(
        body=file_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()
    doc_id = file.get('id')

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
    creds = get_google_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    slides_service = build('slides', 'v1', credentials=creds)

    from core.config import GOOGLE_DRIVE_FOLDER_ID
    folder_id = GOOGLE_DRIVE_FOLDER_ID or "1-KqYGsX7eUVmo9ShlXx0i2c0tg8EnbsB"
    app_name = board_deck.get("app_name", "Blinkit")
    title = f"NL {app_name}"
    
    slides = board_deck.get("slides", [])
    primary_color_hex = board_deck.get("primary_color", "#3b82f6")
    secondary_color_hex = board_deck.get("secondary_color", "#10b981")
    
    brand_r, brand_g, brand_b = hex_to_rgb(primary_color_hex)

    def serialize_board_slide_body(slide):
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
    file = drive_service.files().create(
        body=file_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()
    pres_id = file.get('id')

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
        
        if slide_type == 'executive_summary':
            left_title = "Strategic Opportunity"
            left_lines = [f"Why Now: {val_to_str(slide.get('why_now'))}", f"Recommendation: {val_to_str(slide.get('recommendation'))}"]
            right_title = "Business Impact"
            right_lines = [f"Problem Focus: {val_to_str(slide.get('problem'))}", f"Expected ROI: {val_to_str(slide.get('business_impact'))}"]
            
        elif slide_type == 'customer_problem':
            left_title = "User Pain Points"
            pains = slide.get('top_3_user_pains', [])
            left_lines = [f"- {p}" for p in (pains if isinstance(pains, list) else [pains])]
            left_lines.append(f"Behavior Patterns:\n{val_to_str(slide.get('behavior_patterns'))}")
            
            right_title = "Jobs To Be Done & Quotes"
            jtbd = slide.get('jobs_to_be_done', [])
            right_lines = [f"JTBD: {j}" for j in (jtbd if isinstance(jtbd, list) else [jtbd])]
            quotes = slide.get('customer_quotes', [])
            right_lines.extend([f"Quote: \"{q}\"" for q in (quotes if isinstance(quotes, list) else [quotes])])
            
        elif slide_type == 'root_cause':
            left_title = "Root Cause Analysis (5 Whys)"
            rcs = slide.get('root_causes', [])
            left_lines = [f"- {r}" for r in (rcs if isinstance(rcs, list) else [rcs])]
            
            right_title = "Assumption Validation"
            vals = slide.get('validated_assumptions', [])
            right_lines = [f"Validated: {v}" for v in (vals if isinstance(vals, list) else [vals])]
            fals = slide.get('false_assumptions', [])
            right_lines.extend([f"Refuted: {f}" for f in (fals if isinstance(fals, list) else [fals])])
            
        elif slide_type == 'landscape':
            left_title = "Market Landscape"
            left_lines = [f"Summary:\n{val_to_str(slide.get('competitor_summary'))}", f"Market Gap:\n{val_to_str(slide.get('market_gap'))}"]
            
            right_title = "White Space Moat"
            right_lines = [f"White Space:\n{val_to_str(slide.get('white_space'))}"]
            opps = slide.get('opportunities', [])
            right_lines.extend([f"- {o}" for o in (opps if isinstance(opps, list) else [opps])])
            
        elif slide_type == 'ai_opportunity':
            left_title = "AI Intervention Strategy"
            left_lines = [f"Current Process:\n{val_to_str(slide.get('current_process'))}", f"AI Optimizations:\n{val_to_str(slide.get('ai_can_improve'))}"]
            
            right_title = "Personalization & Predictions"
            right_lines = [f"Automation: {val_to_str(slide.get('automation'))}", f"Personalization: {val_to_str(slide.get('personalization'))}", f"Predictions: {val_to_str(slide.get('predictions'))}"]
            
        elif slide_type == 'solutions':
            col3_data = [
                ("Conservative Option", [val_to_str(slide.get('conservative'))]),
                ("Innovative (Recommended)", [val_to_str(slide.get('innovative')), f"Rationale:\n{val_to_str(slide.get('recommended'))}"]),
                ("Moonshot Option", [val_to_str(slide.get('moonshot'))])
            ]
            
        elif slide_type == 'business_impact':
            left_title = "North Star & Core Metrics"
            left_lines = [f"North Star Metric:\n{val_to_str(slide.get('north_star_metric'))}"]
            pm = slide.get('primary_metrics', [])
            left_lines.extend([f"KPI: {m}" for m in (pm if isinstance(pm, list) else [pm])])
            
            right_title = "Guardrails & Risk Moats"
            gm = slide.get('guardrail_metrics', [])
            right_lines = [f"Guardrail: {g}" for g in (gm if isinstance(gm, list) else [gm])]
            risks = slide.get('risks', [])
            right_lines.extend([f"Risk: {r}" for r in (risks if isinstance(risks, list) else [risks])])
            
        elif slide_type == 'roadmap':
            col3_data = [
                ("Phase 1: Discovery", [val_to_str(slide.get('phase_1'))]),
                ("Phase 2: Scale", [val_to_str(slide.get('phase_2')), f"Timeline: {val_to_str(slide.get('timeline'))}"]),
                ("Phase 3: Optimization", [val_to_str(slide.get('phase_3'))])
            ]
            
        elif slide_type == 'moat':
            left_title = "Customer Moat"
            left_lines = [f"Switching Costs:\n{val_to_str(slide.get('switching_costs'))}", f"Data Moat:\n{val_to_str(slide.get('data_advantage'))}"]
            
            right_title = "Network Advantage"
            right_lines = [f"Network Effect:\n{val_to_str(slide.get('network_effect'))}", f"Flywheel:\n{val_to_str(slide.get('flywheel'))}"]
            
        elif slide_type == 'executive_recommendation':
            left_title = "CPO Decision Requested"
            left_lines = [f"Decision:\n{val_to_str(slide.get('decision'))}"]
            prio = slide.get('top_priorities', [])
            left_lines.extend([f"Priority: {p}" for p in (prio if isinstance(prio, list) else [prio])])
            
            right_title = "Resource & ROI Projections"
            right_lines = [f"Investment Required:\n{val_to_str(slide.get('investment_required'))}", f"Projected ROI:\n{val_to_str(slide.get('expected_roi'))}"]
            
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
                            'endIndex': len(col_title) + 2
                        },
                        'fields': 'fontFamily,fontSize,bold,foregroundColor'
                    }
                })
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
                            'startIndex': len(col_title) + 2,
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
                            'endIndex': len(c_title) + 2
                        },
                        'fields': 'fontFamily,fontSize,bold,foregroundColor'
                    }
                })
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
                            'startIndex': len(c_title) + 2,
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
    Saves it inside the target Google Drive folder and returns the edit URL.
    """
    creds = get_google_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    slides_service = build('slides', 'v1', credentials=creds)

    from core.config import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_SLIDES_TEMPLATE_ID
    folder_id = GOOGLE_DRIVE_FOLDER_ID or "1-KqYGsX7eUVmo9ShlXx0i2c0tg8EnbsB"

    # 1. Create file inside target folder (either clone template or create blank)
    title = "Pulse Intelligence — Executive Insight Deck"
    
    slides = deck_data.get("slides", [])
    
    def get_slide_content(slide):
        if slide.get('slide_number') == 3 and slide.get('mvp_details'):
            d = slide['mvp_details']
            features = ", ".join(d.get('core_features', []))
            metrics = ", ".join(d.get('success_metrics', []))
            return f"Proposed Solution: {d.get('proposed_solution')}\nTarget Users: {d.get('target_users')}\nPain Points: {d.get('pain_points')}\nCore Features: {features}\nSuccess Metrics: {metrics}"
        
        content = slide.get('content')
        if isinstance(content, list):
            return "\n".join(f"- {item}" for item in content)
        return str(content or "")

    if GOOGLE_SLIDES_TEMPLATE_ID:
        try:
            delete_existing_file(drive_service, title, 'application/vnd.google-apps.presentation', folder_id)
            file = drive_service.files().copy(
                fileId=GOOGLE_SLIDES_TEMPLATE_ID,
                body={
                    'name': title,
                    'parents': [folder_id]
                },
                supportsAllDrives=True
            ).execute()
            pres_id = file.get('id')
            
            # Map dynamic text replacements for Slide 1 to 4
            replacements = []
            for idx, slide in enumerate(slides):
                slide_num = idx + 1
                slide_title = slide.get('title', f"Slide {slide_num}")
                slide_headline = slide.get('headline', '')
                slide_body = get_slide_content(slide)
                
                metrics_str = ""
                metrics = slide.get('key_metrics', [])
                if metrics:
                    metrics_str = "\n\nKEY METRICS:\n" + "\n".join(f"- {m.get('label')}: {m.get('value')}" for m in metrics)
                
                full_content = f"{slide_headline}\n\n{slide_body}{metrics_str}"
                
                replacements.append({"match": f"{{{{Slide{slide_num}_Title}}}}", "replace": slide_title})
                replacements.append({"match": f"{{{{Slide{slide_num}_Content}}}}", "replace": full_content})

            # Run replaceAllText updates
            replace_requests = []
            for rep in replacements:
                replace_requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': rep['match'],
                            'matchCase': True
                        },
                        'replaceText': rep['replace']
                    }
                })
                
            if replace_requests:
                slides_service.presentations().batchUpdate(presentationId=pres_id, body={'requests': replace_requests}).execute()
                
            # Set reader permissions
            try:
                drive_service.permissions().create(
                    fileId=pres_id,
                    body={"type": "anyone", "role": "reader"},
                    supportsAllDrives=True
                ).execute()
            except Exception as e:
                logger.warning(f"Could not set public permissions on presentation: {e}")
                
            return f"https://docs.google.com/presentation/d/{pres_id}/edit"
        except Exception as e:
            logger.exception("Failed to create presentation from template. Falling back to blank deck creation.")

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


