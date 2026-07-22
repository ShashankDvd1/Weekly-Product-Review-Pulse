import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reasoning.form_generator import get_google_credentials
from googleapiclient.discovery import build

def main():
    form_id = "1EqlPLfY_9dbv0PA7Zc3d2iHw386T17PceWMFCYz_N1E"
    try:
        creds = get_google_credentials()
        form_service = build('forms', 'v1', credentials=creds)
        
        # 1. Get current form to find existing item IDs to delete
        form = form_service.forms().get(formId=form_id).execute()
        items = form.get("items", [])
        
        requests = []
        
        # Delete all existing items
        for i in range(len(items)):
            requests.append({
                "deleteItem": {
                    "location": {"index": 0}
                }
            })
            
        # Update Form Info
        requests.append({
            "updateFormInfo": {
                "info": {
                    "title": "Blinkit Category Exploration & Shopping Behavior Survey",
                    "description": "Thank you for taking the time to share your feedback. We are conducting research to understand grocery shopping habits and barriers to exploring new product categories (such as electronics, beauty, or toys) on quick-commerce platforms like Blinkit. Your responses will be kept strictly anonymous and confidential. This survey takes approximately 3 minutes."
                },
                "updateMask": "title,description"
            }
        })
        
        # Batch update to clear form first
        form_service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
        print("Cleared existing items and updated form header.")
        
        # 2. Build the new professional list of items
        new_requests = []
        index = 0
        
        def add_text_q(title, required=False):
            nonlocal index
            new_requests.append({
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": required,
                                "textQuestion": {"paragraph": False}
                            }
                        }
                    },
                    "location": {"index": index}
                }
            })
            index += 1

        def add_paragraph_q(title, required=False):
            nonlocal index
            new_requests.append({
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": required,
                                "textQuestion": {"paragraph": True}
                            }
                        }
                    },
                    "location": {"index": index}
                }
            })
            index += 1

        def add_radio_q(title, options, required=False):
            nonlocal index
            new_requests.append({
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": required,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [{"value": opt} for opt in options]
                                }
                            }
                        }
                    },
                    "location": {"index": index}
                }
            })
            index += 1

        def add_checkbox_q(title, options, required=False):
            nonlocal index
            new_requests.append({
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": required,
                                "choiceQuestion": {
                                    "type": "CHECKBOX",
                                    "options": [{"value": opt} for opt in options]
                                }
                            }
                        }
                    },
                    "location": {"index": index}
                }
            })
            index += 1

        def add_scale_q(title, low=1, high=5, low_lbl="Low", high_lbl="High", required=False):
            nonlocal index
            new_requests.append({
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": required,
                                "scaleQuestion": {
                                    "low": low,
                                    "high": high,
                                    "lowLabel": low_lbl,
                                    "highLabel": high_lbl
                                }
                            }
                        }
                    },
                    "location": {"index": index}
                }
            })
            index += 1

        def add_section(title, desc=""):
            nonlocal index
            new_requests.append({
                "createItem": {
                    "item": {
                        "title": title,
                        "description": desc,
                        "pageBreakItem": {}
                    },
                    "location": {"index": index}
                }
            })
            index += 1

        # Section 1: Demographics
        add_text_q("Your Name (Optional)")
        add_radio_q("What is your age range?", ["Under 18", "18–24", "25–34", "35–44", "45–54", "55 or older"])
        add_text_q("What is your occupation?")
        
        # Section 2: Current Shopping Behavior
        add_section("Current Shopping Behavior")
        add_radio_q("How often do you use Blinkit for grocery or household shopping?", [
            "Daily / Multiple times a day",
            "2–3 times a week",
            "Once a week",
            "2–3 times a month",
            "Once a month or less"
        ])
        add_checkbox_q("What product categories do you buy most frequently on Blinkit? (Select all that apply)", [
            "Fresh Produce (Fruits & Vegetables)",
            "Dairy, Bread & Eggs",
            "Munchies & Beverages",
            "Pantry Staples (Atta, Rice, Oil, etc.)",
            "Household Essentials",
            "Personal Care & Hygiene",
            "Other"
        ])

        # Section 3: Category Discovery & Barriers
        add_section("Category Discovery & Barriers")
        add_radio_q("How often do you explore or purchase from non-grocery categories (like electronics, toys, home decor, or beauty) on other e-commerce sites?", [
            "Very frequently",
            "Frequently",
            "Occasionally",
            "Rarely",
            "Never"
        ])
        add_checkbox_q("What prevents you from purchasing non-grocery categories (e.g., electronics, beauty, or toys) on Blinkit? (Select all that apply)", [
            "Lack of trust (authenticity concerns)",
            "Limited product selection / brands",
            "Lack of easy returns/exchanges",
            "High prices / lack of discounts",
            "I don't think of Blinkit for these categories",
            "Other"
        ])

        # Section 4: Alternative Platforms
        add_section("Alternative Platforms")
        add_checkbox_q("Where do you typically buy electronics, beauty, or toy products online?", [
            "Amazon",
            "Flipkart",
            "Myntra / Nykaa / Specialized beauty stores",
            "Quick commerce competitors (Zepto, Instamart)",
            "Direct-to-Consumer (D2C) brand websites",
            "Other"
        ])

        # Section 5: Proposed Solution Validation
        add_section("Proposed Solution Validation")
        add_scale_q("How interested would you be in buying items like chargers, headphones, cosmetics, or toys on Blinkit if they were delivered in 10 minutes?", 1, 5, "Not interested at all", "Extremely interested")
        add_checkbox_q("What features would make you more likely to explore and buy these categories on Blinkit? (Select all that apply)", [
            "A dedicated tab/feed for product discovery",
            "Guaranteed 10-minute return/exchange policy",
            "Verified brand-authenticity badge",
            "Bundle discounts (e.g., free delivery on groceries if buying beauty products)",
            "Other"
        ])

        # Section 6: Convenience & Delivery Premium
        add_section("Convenience & Delivery Premium")
        add_radio_q("Would you purchase high-value items (e.g., premium headphones or luxury cosmetics) on Blinkit for emergency/last-minute needs?", [
            "Yes, definitely",
            "Yes, but only under ₹1,000 value",
            "No, I prefer traditional e-commerce or offline stores for high-value items"
        ])
        add_radio_q("How much extra delivery/convenience fee would you pay for 10-minute delivery of these items instead of waiting 1–2 days on standard e-commerce?", [
            "Nothing (Standard delivery fee only)",
            "₹10 - ₹30",
            "₹30 - ₹50",
            "₹50 - ₹100",
            "₹100+"
        ])

        # Section 7: Open Feedback
        add_section("Open Feedback")
        add_paragraph_q("What is your main concern when purchasing non-grocery items on a quick-commerce platform?")
        add_paragraph_q("Do you have any suggestions to improve the category discovery and shopping experience on Blinkit?")

        form_service.forms().batchUpdate(formId=form_id, body={"requests": new_requests}).execute()
        print("Google Form updated successfully with professional schema!")
        
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    main()
