import json
import random
import os

# ── Paths ──────────────────────────────────────────────────────
RAW_BOOKINGS = "data/raw/bookings.json"
RAW_LEADS    = "data/raw/leads.json"
TRAIN_OUT    = "data/train.jsonl"
VAL_OUT      = "data/val.jsonl"
TRAIN_SPLIT  = 0.85

# ══════════════════════════════════════════════════════════════
# PART 1 — BOOKING examples
# ══════════════════════════════════════════════════════════════

def make_booking_examples(bookings: list) -> list:
    examples = []
    for b in bookings:

        # Example 1: Create a booking
        instruction = f"""Create a confirmed booking with the following details:
Customer name  : {b['customer_name']}
Email          : {b['email']}
Destination    : {b['destination']}
Package        : {b['package']}
Adults         : {b['adults']}
Children       : {b['children']}
Travel dates   : {b['travel_start']} to {b['travel_end']}
Budget (INR)   : {b['budget']}
Special requests: {b['special_requests']}"""

        response = json.dumps({
            "status"          : "confirmed",
            "customer_name"   : b["customer_name"],
            "destination"     : b["destination"],
            "package"         : b["package"],
            "travel_dates"    : {"start": b["travel_start"], "end": b["travel_end"]},
            "guests"          : {"adults": b["adults"], "children": b["children"]},
            "total_cost"      : b["budget"],
            "special_requests": b["special_requests"],
            "next_step"       : "Send confirmation email with payment link"
        }, indent=2)

        examples.append({"instruction": instruction, "response": response})

        # Example 2: Generate itinerary
        days = (
            int(b["travel_end"].split("-")[2]) -
            int(b["travel_start"].split("-")[2])
        )
        instr_itin = f"""Generate a {days}-day travel itinerary for:
Destination : {b['destination']}
Package     : {b['package']}
Guests      : {b['adults']} adults, {b['children']} children
Special     : {b['special_requests']}"""

        resp_itin = json.dumps({
            "destination" : b["destination"],
            "total_days"  : days,
            "itinerary"   : [
                {
                    "day"        : i + 1,
                    "title"      : f"Day {i+1} activity",
                    "activities" : [
                        "Morning sightseeing",
                        "Afternoon leisure",
                        "Evening cultural experience"
                    ],
                    "meals" : "Breakfast + Dinner included",
                    "hotel" : f"Premium hotel in {b['destination']}"
                }
                for i in range(days)
            ],
            "notes": b["special_requests"]
        }, indent=2)

        examples.append({"instruction": instr_itin, "response": resp_itin})

    return examples


# ══════════════════════════════════════════════════════════════
# PART 2 — LEAD SCORING examples
# ══════════════════════════════════════════════════════════════

def calculate_score(lead: dict) -> int:
    score = 0

    # Budget clarity
    if lead["budget"] not in ("Not specified", "", None):
        try:
            val = int(str(lead["budget"]).replace(",", ""))
            score += 25 if val >= 200000 else 15 if val >= 80000 else 8
        except ValueError:
            score += 5

    # Engagement
    mc = lead["message_count"]
    score += 25 if mc >= 8 else 15 if mc >= 4 else 5

    # Recency
    dc = lead["days_since_contact"]
    score += 25 if dc <= 2 else 15 if dc <= 7 else 5

    # Email response
    if lead["email_responded"]:
        score += 15

    # Travel urgency
    tm = lead["travel_month"].lower()
    if any(w in tm for w in ["next month", "this month", "week"]):
        score += 10
    elif any(w in tm for w in ["month", "soon"]):
        score += 5

    return min(score, 100)


def get_category(score: int) -> tuple:
    if score >= 75:
        return "HOT",  "Call within 24 hours — high intent buyer"
    elif score >= 45:
        return "WARM", "Follow up within 3 days with tailored offer"
    else:
        return "COLD", "Add to monthly newsletter — re-engage in 6 weeks"


def make_lead_examples(leads: list) -> list:
    examples = []
    for lead in leads:
        score = calculate_score(lead)
        category, action = get_category(score)

        # Example 1: Score the lead
        instruction = f"""Score this travel sales lead:
Name                 : {lead['name']}
Destinations         : {lead['destinations']}
Budget (INR)         : {lead['budget']}
Travel month         : {lead['travel_month']}
Messages sent        : {lead['message_count']}
Days since contact   : {lead['days_since_contact']}
Responded to email   : {lead['email_responded']}"""

        response = json.dumps({
            "lead_score"         : score,
            "category"           : category,
            "reasoning"          : f"Score based on budget clarity, engagement ({lead['message_count']} msgs), recency ({lead['days_since_contact']} days), email response: {lead['email_responded']}",
            "recommended_action" : action,
            "follow_up_subject"  : f"Your {lead['destinations']} holiday — personalised offer inside"
        }, indent=2)

        examples.append({"instruction": instruction, "response": response})

        # Example 2: Draft follow-up email
        instr_email = f"""Draft a follow-up email for this {category} travel lead.
Name         : {lead['name']}
Interested in: {lead['destinations']}
Budget       : {lead['budget']} INR
Category     : {category}
Tone         : Friendly, professional, not pushy. Max 120 words."""

        resp_email = json.dumps({
            "subject"    : f"Your {lead['destinations']} holiday — personalised offer inside",
            "email_body" : (
                f"Hi {lead['name']},\n\n"
                f"Thank you for your interest in travelling to {lead['destinations']}! "
                f"We have curated some exclusive packages that perfectly match your preferences and budget.\n\n"
                f"{'We would love to connect — are you free for a quick call this week?' if category == 'HOT' else 'Whenever you are ready to explore, we are here to help.'}\n\n"
                f"Warm regards,\nTravel CRM Team"
            )
        }, indent=2)

        examples.append({"instruction": instr_email, "response": resp_email})

    return examples


# ══════════════════════════════════════════════════════════════
# PART 3 — FORMAT + SAVE
# ══════════════════════════════════════════════════════════════

def format_for_mistral(instruction: str, response: str) -> dict:
    return {
        "text": f"<s>[INST] {instruction.strip()} [/INST] {response.strip()} </s>"
    }


def save_jsonl(data: list, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  Saved {len(data)} examples → {path}")


def build_dataset():
    print("\n📂 Loading raw data...")
    with open(RAW_BOOKINGS, encoding="utf-8") as f:
        bookings = json.load(f)
    with open(RAW_LEADS, encoding="utf-8") as f:
        leads = json.load(f)

    print(f"  Bookings loaded : {len(bookings)}")
    print(f"  Leads loaded    : {len(leads)}")

    print("\n⚙️  Generating training examples...")
    all_examples = []
    all_examples += make_booking_examples(bookings)
    all_examples += make_lead_examples(leads)
    print(f"  Total examples  : {len(all_examples)}")

    random.seed(42)
    random.shuffle(all_examples)

    split_idx  = int(len(all_examples) * TRAIN_SPLIT)
    train_data = all_examples[:split_idx]
    val_data   = all_examples[split_idx:]

    print("\n💾 Saving JSONL files...")
    save_jsonl(
        [format_for_mistral(e["instruction"], e["response"]) for e in train_data],
        TRAIN_OUT
    )
    save_jsonl(
        [format_for_mistral(e["instruction"], e["response"]) for e in val_data],
        VAL_OUT
    )

    print(f"\n✅ Dataset ready!")
    print(f"   Train : {len(train_data)} examples  →  {TRAIN_OUT}")
    print(f"   Val   : {len(val_data)} examples   →  {VAL_OUT}")
    print(f"\n👉 Next step: run  python finetune/train.py")


if __name__ == "__main__":
    build_dataset()