import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Travel CRM AI",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background: #f8f9fa; }
.hero-banner {
    width: 100%;
    height: 320px;
    object-fit: cover;
    border-radius: 16px;
    margin-bottom: 16px;
}
[data-testid="stChatMessage"] {
    background: white;
    border-radius: 12px;
    padding: 8px;
    margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ── Destinations data ──────────────────────────────────────────
DESTINATIONS = [
    {
        "name": "Bali, Indonesia", "emoji": "🌴",
        "price": "₹85,000", "days": "7N/8D", "tag": "Beach",
        "color": "#1d9e75", "region": "Southeast Asia",
        "photo": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
        "desc": "Bali is a living postcard — emerald rice terraces, ancient Hindu temples, crashing surf and lush jungles.",
        "highlights": ["Ubud rice terraces & monkey forest", "Tanah Lot sunset temple", "Mount Batur sunrise trek", "Seminyak beach clubs", "Traditional Balinese cooking class"],
        "hotels": ["The Mulia Resort", "Four Seasons Jimbaran", "Alaya Resort Ubud"],
        "best_time": "April – October",
        "includes": ["Return flights", "7 nights hotel", "Daily breakfast", "Airport transfers", "Guided tours"]
    },
    {
        "name": "Maldives", "emoji": "🏝️",
        "price": "₹1,50,000", "days": "5N/6D", "tag": "Luxury",
        "color": "#378add", "region": "Beach",
        "photo": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800",
        "desc": "The Maldives is the ultimate tropical escape — crystal-clear lagoons, overwater bungalows and the finest marine life.",
        "highlights": ["Overwater villa stay", "Snorkelling with manta rays", "Sunset dolphin cruise", "Private beach dining", "Underwater restaurant experience"],
        "hotels": ["Soneva Jani", "Conrad Maldives", "Gili Lankanfushi"],
        "best_time": "November – April",
        "includes": ["Return flights", "5 nights water villa", "All meals", "Seaplane transfers", "Snorkelling gear"]
    },
    {
        "name": "Paris, France", "emoji": "🗼",
        "price": "₹2,20,000", "days": "6N/7D", "tag": "Romance",
        "color": "#534ab7", "region": "Europe",
        "photo": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800",
        "desc": "Paris — the City of Light. From the Eiffel Tower to the Louvre, every corner tells a story of art, culture and romance.",
        "highlights": ["Eiffel Tower visit", "Louvre Museum guided tour", "Seine river cruise", "Versailles day trip", "Montmartre art district walk"],
        "hotels": ["Le Meurice", "Hotel de Crillon", "Shangri-La Paris"],
        "best_time": "April – June, September – October",
        "includes": ["Return flights", "6 nights hotel", "Daily breakfast", "Airport transfers", "City tours"]
    },
    {
        "name": "Switzerland", "emoji": "🏔️",
        "price": "₹3,00,000", "days": "7N/8D", "tag": "Snow",
        "color": "#3c3489", "region": "Europe",
        "photo": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        "desc": "Switzerland is nature perfected — snow-capped Alps, pristine lakes, charming villages and world-class ski resorts.",
        "highlights": ["Jungfraujoch Top of Europe", "Interlaken adventure activities", "Lucerne Chapel Bridge", "Zermatt & Matterhorn views", "Swiss chocolate tour"],
        "hotels": ["The Dolder Grand Zurich", "Victoria-Jungfrau Interlaken", "Mont Cervin Palace"],
        "best_time": "December – March (snow), June – September (hiking)",
        "includes": ["Return flights", "7 nights hotel", "Daily breakfast", "Swiss Travel Pass", "Guided mountain tours"]
    },
    {
        "name": "Rajasthan, India", "emoji": "🏰",
        "price": "₹45,000", "days": "6N/7D", "tag": "Heritage",
        "color": "#d85a30", "region": "India",
        "photo": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800",
        "desc": "Rajasthan is India's royal heartland — magnificent forts, ornate palaces, golden deserts and vibrant folk culture.",
        "highlights": ["Amber Fort Jaipur", "Lake Palace Udaipur", "Thar Desert camel safari", "Mehrangarh Fort Jodhpur", "Pushkar camel fair"],
        "hotels": ["Umaid Bhawan Palace", "Taj Lake Palace", "Rambagh Palace"],
        "best_time": "October – March",
        "includes": ["AC transport", "6 nights heritage hotels", "Daily breakfast & dinner", "All entry tickets", "Local guide"]
    },
    {
        "name": "Kerala, India", "emoji": "🌿",
        "price": "₹35,000", "days": "4N/5D", "tag": "Nature",
        "color": "#3b6d11", "region": "India",
        "photo": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800",
        "desc": "Kerala — God's Own Country. Serene backwaters, lush tea gardens, spice plantations and Ayurvedic wellness.",
        "highlights": ["Alleppey houseboat stay", "Munnar tea gardens", "Periyar wildlife sanctuary", "Kathakali dance performance", "Ayurveda spa day"],
        "hotels": ["Kumarakom Lake Resort", "Brunton Boatyard", "Spice Village Thekkady"],
        "best_time": "September – March",
        "includes": ["AC transport", "4 nights hotel + houseboat", "Daily breakfast", "Backwater cruise", "Spice garden tour"]
    },
    {
        "name": "Dubai, UAE", "emoji": "🌇",
        "price": "₹1,20,000", "days": "4N/5D", "tag": "Luxury",
        "color": "#b7791f", "region": "Asia",
        "photo": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800",
        "desc": "Dubai is where the future meets tradition — towering skyscrapers, golden deserts, luxury malls and world-record attractions.",
        "highlights": ["Burj Khalifa At The Top", "Desert safari with BBQ dinner", "Dubai Mall & fountain show", "Palm Jumeirah tour", "Gold & Spice Souk walk"],
        "hotels": ["Burj Al Arab", "Atlantis The Palm", "Armani Hotel Dubai"],
        "best_time": "November – March",
        "includes": ["Return flights", "4 nights hotel", "Daily breakfast", "Desert safari", "City tour"]
    },
    {
        "name": "Thailand", "emoji": "🐘",
        "price": "₹65,000", "days": "5N/6D", "tag": "Adventure",
        "color": "#0f6e56", "region": "Southeast Asia",
        "photo": "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800",
        "desc": "Thailand is Southeast Asia at its finest — tropical beaches, ornate temples, elephant sanctuaries and amazing street food.",
        "highlights": ["Grand Palace Bangkok", "Elephant sanctuary Chiang Mai", "Phi Phi Islands cruise", "Floating market tour", "Thai cooking class"],
        "hotels": ["Mandarin Oriental Bangkok", "Amanpuri Phuket", "Four Seasons Chiang Mai"],
        "best_time": "November – April",
        "includes": ["Return flights", "5 nights hotel", "Daily breakfast", "Island hopping tour", "Temple tours"]
    },
    {
        "name": "Japan", "emoji": "⛩️",
        "price": "₹2,00,000", "days": "7N/8D", "tag": "Culture",
        "color": "#993556", "region": "Asia",
        "photo": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800",
        "desc": "Japan is a perfect blend of ancient tradition and cutting-edge modernity — cherry blossoms, samurai history and bullet trains.",
        "highlights": ["Mount Fuji day trip", "Kyoto temple trail", "Tokyo Shibuya crossing", "Nara deer park", "Bullet train experience"],
        "hotels": ["Park Hyatt Tokyo", "Ritz Carlton Kyoto", "Aman Tokyo"],
        "best_time": "March – May, October – November",
        "includes": ["Return flights", "7 nights hotel", "Daily breakfast", "JR Pass", "Guided cultural tours"]
    },
    {
        "name": "Italy", "emoji": "🍕",
        "price": "₹2,50,000", "days": "7N/8D", "tag": "Food",
        "color": "#7f77dd", "region": "Europe",
        "photo": "https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?w=800",
        "desc": "Italy is a feast for all senses — ancient ruins, Renaissance art, rolling Tuscan hills, world-class wine and the best food on earth.",
        "highlights": ["Colosseum & Roman Forum", "Vatican Museums", "Venice gondola ride", "Florence Uffizi Gallery", "Amalfi Coast drive"],
        "hotels": ["Hotel de Russie Rome", "Gritti Palace Venice", "Il Pellicano Tuscany"],
        "best_time": "April – June, September – October",
        "includes": ["Return flights", "7 nights hotel", "Daily breakfast", "Train passes", "Museum tickets"]
    },
    {
        "name": "Vietnam", "emoji": "🛵",
        "price": "₹70,000", "days": "6N/7D", "tag": "Culture",
        "color": "#085041", "region": "Southeast Asia",
        "photo": "https://images.unsplash.com/photo-1528127269322-539801943592?w=800",
        "desc": "Vietnam is a country of breathtaking natural beauty — from the karst mountains of Ha Long Bay to the ancient town of Hoi An.",
        "highlights": ["Ha Long Bay cruise", "Hoi An ancient town", "Ho Chi Minh City tour", "Hue imperial citadel", "Mekong Delta boat tour"],
        "hotels": ["Park Hyatt Saigon", "Nam Hai Hoi An", "Sofitel Legend Metropole"],
        "best_time": "February – April",
        "includes": ["Return flights", "6 nights hotel", "Daily breakfast", "Ha Long Bay cruise", "City tours"]
    },
    {
        "name": "Singapore", "emoji": "🦁",
        "price": "₹90,000", "days": "4N/5D", "tag": "City",
        "color": "#ba7517", "region": "Asia",
        "photo": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800",
        "desc": "Singapore is Asia's most dazzling city-state — Gardens by the Bay, Marina Bay Sands and incredible street food.",
        "highlights": ["Gardens by the Bay light show", "Marina Bay Sands SkyPark", "Universal Studios Singapore", "Sentosa Island beaches", "Hawker centre food tour"],
        "hotels": ["Marina Bay Sands", "Raffles Singapore", "Capella Singapore"],
        "best_time": "February – April",
        "includes": ["Return flights", "4 nights hotel", "Daily breakfast", "Airport transfers", "Gardens by the Bay tickets"]
    },
]

SYSTEM_PROMPT = """You are Aria, a friendly and knowledgeable travel assistant for a premium Indian travel company called TravelCRM AI.
You help customers plan holidays, suggest destinations, explain visa requirements,
recommend best times to visit, suggest budgets and answer any travel-related questions.

Our packages:
- Bali 7N/8D from Rs 85,000 per person
- Maldives 5N/6D from Rs 1,50,000 per person
- Paris 6N/7D from Rs 2,20,000 per person
- Switzerland 7N/8D from Rs 3,00,000 per person
- Rajasthan 6N/7D from Rs 45,000 per person
- Kerala 4N/5D from Rs 35,000 per person
- Dubai 4N/5D from Rs 1,20,000 per person
- Thailand 5N/6D from Rs 65,000 per person
- Japan 7N/8D from Rs 2,00,000 per person
- Italy 7N/8D from Rs 2,50,000 per person
- Vietnam 6N/7D from Rs 70,000 per person
- Singapore 4N/5D from Rs 90,000 per person

Rules:
- Always be warm, friendly and conversational like a real travel agent
- Give specific recommendations with prices when asked about budget
- When suggesting destinations always mention highlights and best time to visit
- Keep responses to 3-5 sentences unless more detail is needed
- Always end with a helpful follow-up question to understand the customer better
- For visa questions give specific info for Indian passport holders
- Never make up information — if unsure say you will check and confirm"""

FALLBACK_RESPONSES = {
    "bali":       "Bali is absolutely magical! 🌴 Best time is April–October. Our 7N/8D package starts at ₹85,000 per person and includes Ubud rice terraces, Mount Batur sunrise trek and Seminyak beach. Shall I check availability for your dates?",
    "maldives":   "The Maldives is pure luxury! 🏝️ Overwater villas, crystal lagoons and manta rays await you. Our 5N/6D package starts at ₹1,50,000. Best time is November–April. How many people would be travelling?",
    "paris":      "Paris is always a good idea! 🗼 Our 6N/7D package starts at ₹2,20,000 and includes the Eiffel Tower, Louvre and a Seine cruise. Best visited April–June. Is this for a honeymoon or leisure trip?",
    "switzerland":"Switzerland is breathtaking! 🏔️ Our 7N/8D package starts at ₹3,00,000 and includes the Jungfraujoch, Interlaken and Lucerne. Best for snow is December–March. Would you like skiing or sightseeing?",
    "dubai":      "Dubai is incredible! 🌇 Our 4N/5D package starts at ₹1,20,000 and includes Burj Khalifa, desert safari and the Dubai Mall. Best time is November–March. How many people are travelling?",
    "thailand":   "Thailand is amazing value! 🐘 Our 5N/6D package starts at ₹65,000 and includes Bangkok temples, elephant sanctuary and Phi Phi Islands. Best time is November–April. Is this for family or couple?",
    "japan":      "Japan is absolutely stunning! ⛩️ Our 7N/8D package starts at ₹2,00,000 and includes Mount Fuji, Kyoto temples and a bullet train ride. Best for cherry blossoms is March–May. When are you planning to travel?",
    "kerala":     "Kerala is God's Own Country! 🌿 Our 4N/5D package starts at just ₹35,000 and includes a houseboat stay, Munnar tea gardens and an Ayurveda spa. Best time is September–March. Perfect for a relaxing getaway!",
    "rajasthan":  "Rajasthan is royal India at its finest! 🏰 Our 6N/7D package starts at ₹45,000 and includes Amber Fort, Lake Palace and a camel safari. Best time is October–March. Is this for family or couple?",
    "singapore":  "Singapore is amazing for families! 🦁 Our 4N/5D package starts at ₹90,000 and includes Universal Studios, Gardens by the Bay and Sentosa Island. Best time is February–April. How many people are travelling?",
    "honeymoon":  "Congratulations! 💑 For honeymoons I'd recommend Maldives (ultimate romance, ₹1.5L), Bali (great value, ₹85K), Paris (classic romance, ₹2.2L) or Kerala (serene backwaters, ₹35K). What's your budget range?",
    "family":     "Great for families! 👨‍👩‍👧‍👦 Singapore has Universal Studios, Thailand is very family-friendly, Bali has fun activities for all ages, and Rajasthan is amazing for heritage. How many adults and children are travelling?",
    "budget":     "Great question about budget! 💰 For under ₹50K — Kerala (₹35K) and Rajasthan (₹45K) are fantastic. For ₹50K–₹1L — Bali (₹85K), Thailand (₹65K) and Singapore (₹90K) are very popular. For luxury — Maldives (₹1.5L) and Paris (₹2.2L) are our bestsellers! What's your budget?",
    "visa":       "Great news for Indian passport holders! 🛂 Visa on arrival or e-visa: Thailand, Maldives, Indonesia (Bali), UAE (Dubai) and Singapore. Requires visa: Europe (Schengen), Japan and UK. Which destination are you considering?",
    "cheap":      "For affordable trips, Kerala (₹35K) and Rajasthan (₹45K) are our best value domestic options. For international, Thailand (₹65K) and Vietnam (₹70K) offer incredible experiences at great prices. When are you looking to travel?",
    "italy":      "Italy is a dream destination! 🍕 Our 7N/8D package starts at ₹2,50,000 and includes the Colosseum, Vatican, Venice gondola ride and Amalfi Coast. Best time is April–June. Is this for a couple or family trip?",
    "vietnam":    "Vietnam is absolutely stunning! 🛵 Our 6N/7D package starts at ₹70,000 and includes Ha Long Bay cruise, Hoi An ancient town and a Mekong Delta tour. Best time is February–April. Have you been to Southeast Asia before?",
}

def get_ai_response(messages):
    """Try OpenAI first, then Ollama, then fallback."""

    # Build message list with system prompt
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        if m["role"] in ["user", "assistant"]:
            full_messages.append({
                "role": m["role"],
                "content": m["content"]
            })

    # Option 1: OpenAI ChatGPT API
    try:
        from openai import OpenAI
        api_key = st.secrets.get("OPENAI_API_KEY", "")
        if api_key:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",   # cheap + very smart
                messages=full_messages,
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content, "🟢 Powered by ChatGPT"
    except Exception as e:
        print(f"OpenAI error: {e}")

    # Option 2: Ollama (free local AI)
    try:
        import ollama
        response = ollama.chat(
            model="llama3.2",
            messages=full_messages
        )
        return response["message"]["content"], "🟢 Powered by Llama 3.2"
    except Exception:
        pass

    # Option 3: Claude API
    try:
        import anthropic
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if api_key:
            client = anthropic.Anthropic(api_key=api_key)
            claude_messages = [m for m in full_messages if m["role"] != "system"]
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=claude_messages
            )
            return response.content[0].text, "🟢 Powered by Claude AI"
    except Exception:
        pass

    # Option 4: Smart fallback
    last_user_msg = next(
        (m["content"].lower() for m in reversed(messages) if m["role"] == "user"),
        ""
    )
    reply = next(
        (v for k, v in FALLBACK_RESPONSES.items() if k in last_user_msg),
        "That's a great question! ✈️ I'd love to help you plan the perfect trip. Could you tell me your budget range, travel dates and whether you're travelling solo, as a couple or with family? That will help me give you the best recommendations!"
    )
    return reply, "🟡 Fallback mode"

    # Option 1: Try Ollama (free local AI)
    try:
        import ollama
        response = ollama.chat(
            model="llama3.2",
            messages=full_messages
        )
        return response["message"]["content"], "🟢 Powered by Llama 3.2 (Local AI)"
    except Exception:
        pass

    # Option 2: Try Claude API
    try:
        import anthropic
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if api_key:
            client = anthropic.Anthropic(api_key=api_key)
            claude_messages = [m for m in full_messages if m["role"] != "system"]
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=claude_messages
            )
            return response.content[0].text, "🟢 Powered by Claude AI"
    except Exception:
        pass

    # Option 3: Smart fallback responses
    last_user_msg = next(
        (m["content"].lower() for m in reversed(messages) if m["role"] == "user"),
        ""
    )
    reply = next(
        (v for k, v in FALLBACK_RESPONSES.items() if k in last_user_msg),
        "That's a great question! ✈️ I'd love to help you plan the perfect trip. Could you tell me your budget range, travel dates and whether you're travelling solo, as a couple or with family? That will help me give you the best recommendations!"
    )
    return reply, "🟡 Smart fallback mode (install Ollama for full AI)"


# ── Session state ──────────────────────────────────────────────
if "page"           not in st.session_state: st.session_state.page           = "home"
if "selected_dest"  not in st.session_state: st.session_state.selected_dest  = None
if "portal"         not in st.session_state: st.session_state.portal         = "Customer Portal"
if "chat_messages"  not in st.session_state: st.session_state.chat_messages  = [
    {"role": "assistant", "content": "Hi! I'm Aria, your personal Travel AI assistant 🌍✈️\n\nI can help you:\n- **Find the perfect destination** based on your budget\n- **Plan your itinerary** day by day\n- **Answer visa questions** for Indian passport holders\n- **Compare packages** and find the best deals\n\nWhat would you like to explore today?"}
]

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈️ Travel CRM AI")
    st.markdown("---")

    portal = st.radio("", ["Customer Portal", "Admin Dashboard"],
                      label_visibility="collapsed")
    if portal != st.session_state.portal:
        st.session_state.portal        = portal
        st.session_state.page          = "home"
        st.session_state.selected_dest = None
        st.rerun()

    if st.session_state.page == "detail":
        st.markdown("---")
        if st.button("← Back to destinations", use_container_width=True):
            st.session_state.page          = "home"
            st.session_state.selected_dest = None
            st.rerun()

    st.markdown("---")
    try:
        requests.get(f"{API_URL}/", timeout=2)
        st.success("API Online ✅")
    except:
        st.warning("API Offline ⚠️")
        st.caption("Run: uvicorn main:app --reload")


# ══════════════════════════════════════════════════════════════
# CUSTOMER PORTAL
# ══════════════════════════════════════════════════════════════
if st.session_state.portal == "Customer Portal":

    # ── DESTINATION DETAIL PAGE ───────────────────────────────
    if st.session_state.page == "detail" and st.session_state.selected_dest:
        dest = next((d for d in DESTINATIONS
                     if d["name"] == st.session_state.selected_dest), None)

        if dest:
            # Hero photo
            st.markdown(f"""
            <img src="{dest['photo']}" style="width:100%;height:320px;
                 object-fit:cover;border-radius:16px;margin-bottom:16px;">
            """, unsafe_allow_html=True)

            col_title, col_price = st.columns([3, 1])
            with col_title:
                st.markdown(f"# {dest['emoji']} {dest['name']}")
                st.markdown(f"*{dest['desc']}*")
            with col_price:
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:16px;
                            text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                            border:2px solid {dest["color"]};margin-top:8px;'>
                    <div style='font-size:12px;color:#666;'>Starting from</div>
                    <div style='font-size:26px;font-weight:700;color:{dest["color"]};'>{dest["price"]}</div>
                    <div style='font-size:13px;color:#444;'>{dest["days"]} per person</div>
                    <div style='font-size:12px;color:#888;margin-top:4px;'>Best time: {dest["best_time"]}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            col_h, col_i = st.columns(2)
            with col_h:
                st.markdown("### ✨ Highlights")
                for h in dest["highlights"]:
                    st.markdown(f"• {h}")
            with col_i:
                st.markdown("### ✅ What's included")
                for inc in dest["includes"]:
                    st.markdown(f"• {inc}")

            st.markdown("### 🏨 Recommended hotels")
            hcols = st.columns(3)
            for i, hotel in enumerate(dest["hotels"]):
                with hcols[i]:
                    st.markdown(f"""
                    <div style='background:white;border-radius:10px;padding:14px;
                                text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.07);'>
                        <div style='font-size:24px;'>🏨</div>
                        <div style='font-weight:600;font-size:13px;margin-top:6px;'>{hotel}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # Booking form
            st.markdown(f"### ✈️ Book your trip to {dest['name']}")
            with st.form("booking_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name     = st.text_input("Full name *")
                    adults   = st.selectbox("Adults", [1,2,3,4,5], index=1)
                    date     = st.date_input("Travel date")
                    budget   = st.number_input("Budget (INR)", min_value=10000, step=5000, value=100000)
                with col2:
                    email    = st.text_input("Email address *")
                    children = st.selectbox("Children", [0,1,2,3])
                    phone    = st.text_input("Phone number")
                    special  = st.text_input("Special requests", placeholder="vegetarian, sea view...")

                interests = st.multiselect("Your interests",
                    ["Adventure","Beach","Culture","Food","Heritage",
                     "Luxury","Nature","Romance","Shopping","Wildlife"])

                submitted = st.form_submit_button(
                    f"✈️ Confirm booking to {dest['name']}",
                    type="primary", use_container_width=True
                )
                if submitted:
                    if name and email:
                        details = (f"{adults} adults, {children} children, date: {date}, "
                                   f"budget: ₹{budget:,}, interests: {', '.join(interests)}, "
                                   f"requests: {special}")
                        try:
                            requests.post(f"{API_URL}/booking/create",
                                json={"customer_name": name, "details": details})
                        except:
                            pass
                        st.success(f"🎉 Booking confirmed for **{dest['name']}**! We'll contact you at **{email}** within 24 hours.")
                        st.balloons()
                    else:
                        st.error("Please enter your name and email.")

    # ── HOME PAGE ─────────────────────────────────────────────
    else:
        # Two column layout — destinations left, chatbot right
        col_dest, col_chat = st.columns([3, 2])

        with col_dest:
            st.markdown("# 🌍 Where would you like to travel?")
            st.markdown("Click any destination to explore photos and book your trip.")
            st.markdown("---")

            regions  = ["All"] + sorted(list(set(d["region"] for d in DESTINATIONS)))
            region   = st.selectbox("Filter by region", regions)
            filtered = DESTINATIONS if region == "All" else \
                       [d for d in DESTINATIONS if d["region"] == region]

            cols = st.columns(3)
            for i, dest in enumerate(filtered):
                with cols[i % 3]:
                    st.markdown(f"""
                    <img src="{dest['photo']}"
                         style="width:100%;height:160px;object-fit:cover;
                                border-radius:12px;margin-bottom:6px;">
                    """, unsafe_allow_html=True)
                    st.markdown(f"**{dest['emoji']} {dest['name']}**")
                    st.markdown(f"From **{dest['price']}** · {dest['days']}")
                    st.caption(f"{dest['tag']} · {dest['region']}")
                    if st.button("Explore & Book →", key=f"dest_{i}",
                                 use_container_width=True):
                        st.session_state.selected_dest = dest["name"]
                        st.session_state.page          = "detail"
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)

            # My Bookings
            st.markdown("---")
            st.subheader("📋 My Bookings")
            bookings = [
                {"dest":"Bali Explorer 7N/8D",   "dates":"10–17 Dec 2025","guests":"2 adults",  "amount":"₹1,20,000","status":"Confirmed"},
                {"dest":"Maldives Luxury 5N/6D", "dates":"15–20 Jan 2026","guests":"2A 1C",      "amount":"₹2,00,000","status":"Pending"},
                {"dest":"Dubai Delight 4N/5D",   "dates":"5–9 Mar 2026",  "guests":"2 adults",   "amount":"₹1,50,000","status":"Cancelled"},
            ]
            for b in bookings:
                icon = "🟢" if b["status"]=="Confirmed" else "🟡" if b["status"]=="Pending" else "🔴"
                c1,c2,c3,c4,c5 = st.columns([3,2,2,2,1])
                c1.markdown(f"**{icon} {b['dest']}**")
                c2.markdown(f"📅 {b['dates']}")
                c3.markdown(f"👥 {b['guests']}")
                c4.markdown(f"💰 {b['amount']}")
                c5.markdown(b["status"])
                st.divider()

        # ── AI CHATBOT (right side) ───────────────────────────
        with col_chat:
            st.markdown("## 💬 Chat with Aria")
            st.caption("Your personal AI travel assistant")
            st.markdown("---")

            # Quick suggestion buttons
            st.markdown("**Quick questions:**")
            qcols = st.columns(2)
            suggestions = [
                "Best honeymoon destination?",
                "Trips under ₹1 lakh?",
                "Visa-free countries for Indians?",
                "Best family destination?",
            ]
            for i, suggestion in enumerate(suggestions):
                with qcols[i % 2]:
                    if st.button(suggestion, key=f"sug_{i}",
                                 use_container_width=True):
                        st.session_state.chat_messages.append({
                            "role": "user", "content": suggestion
                        })
                        reply, _ = get_ai_response(st.session_state.chat_messages)
                        st.session_state.chat_messages.append({
                            "role": "assistant", "content": reply
                        })
                        st.rerun()

            st.markdown("---")

            # Chat history
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.chat_messages:
                    with st.chat_message(msg["role"],
                        avatar="🤖" if msg["role"] == "assistant" else "👤"):
                        st.markdown(msg["content"])

            # Chat input
            if prompt := st.chat_input("Ask me about any destination..."):
                st.session_state.chat_messages.append({
                    "role": "user", "content": prompt
                })
                with st.spinner("Aria is thinking..."):
                    reply, source = get_ai_response(st.session_state.chat_messages)
                st.session_state.chat_messages.append({
                    "role": "assistant", "content": reply
                })
                st.rerun()

            # Clear chat
            if len(st.session_state.chat_messages) > 1:
                if st.button("🗑️ Clear chat", use_container_width=True):
                    st.session_state.chat_messages = [
                        {"role": "assistant",
                         "content": "Hi! I'm Aria 🌍✈️ How can I help you plan your perfect holiday?"}
                    ]
                    st.rerun()


# ══════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════
else:
    st.title("📊 Admin Dashboard")
    st.markdown("---")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Bookings","24",    "+3 this week")
    c2.metric("Revenue",       "₹18.4L","+₹2.1L")
    c3.metric("Hot Leads",     "8",     "+2 today")
    c4.metric("Customers",     "31",    "+5 this month")
    c5.metric("Conversion",    "34%",   "+5%")

    st.markdown("---")

    tab1,tab2,tab3,tab4 = st.tabs([
        "📋 All Bookings","🎯 Lead Scores","💰 Revenue","👥 Customers"
    ])

    with tab1:
        st.subheader("All Bookings")
        df = pd.DataFrame([
            {"ID":"BK001","Customer":"Priya Sharma", "Destination":"Bali",      "Dates":"10-17 Dec","Amount":"₹1,20,000","Status":"Confirmed"},
            {"ID":"BK002","Customer":"Rahul Verma",  "Destination":"Maldives",  "Dates":"15-20 Jan","Amount":"₹2,00,000","Status":"Confirmed"},
            {"ID":"BK003","Customer":"Anjali Mehta", "Destination":"Rajasthan", "Dates":"1-7 Feb",  "Amount":"₹1,80,000","Status":"Pending"},
            {"ID":"BK004","Customer":"Karan Mehta",  "Destination":"Dubai",     "Dates":"5-9 Mar",  "Amount":"₹1,50,000","Status":"Pending"},
            {"ID":"BK005","Customer":"Neha Joshi",   "Destination":"Swiss Alps","Dates":"10-16 Apr","Amount":"₹4,00,000","Status":"Confirmed"},
            {"ID":"BK006","Customer":"Suresh Patel", "Destination":"Thailand",  "Dates":"1-6 May",  "Amount":"₹90,000",  "Status":"Confirmed"},
            {"ID":"BK007","Customer":"Meera Nair",   "Destination":"Paris",     "Dates":"14-19 Jun","Amount":"₹3,50,000","Status":"Pending"},
            {"ID":"BK008","Customer":"Amit Singh",   "Destination":"Kerala",    "Dates":"20-24 Jul","Amount":"₹60,000",  "Status":"Cancelled"},
        ])
        sf = st.selectbox("Filter by status", ["All","Confirmed","Pending","Cancelled"])
        if sf != "All": df = df[df["Status"]==sf]
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Lead Scores")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Score a new lead**")
            with st.form("lead_form"):
                l_name   = st.text_input("Name")
                l_dest   = st.text_input("Destination interest")
                l_budget = st.text_input("Budget (INR)")
                l_msgs   = st.slider("Messages sent", 1, 20, 5)
                l_days   = st.slider("Days since contact", 0, 60, 3)
                l_email  = st.checkbox("Responded to email")
                if st.form_submit_button("Score this lead →", use_container_width=True):
                    if l_name:
                        try:
                            res = requests.post(f"{API_URL}/lead/score", json={
                                "name":l_name,"destinations":l_dest,
                                "message_count":l_msgs,"days_since_contact":l_days,
                                "budget":l_budget,"email_responded":l_email
                            })
                            r = res.json()
                            color = "#c53030" if r["category"]=="HOT" else "#b7791f" if r["category"]=="WARM" else "#2b6cb0"
                            st.markdown(f"""
                            <div style='background:white;border-radius:12px;padding:16px;
                                        border:2px solid {color};text-align:center;'>
                                <div style='font-size:36px;font-weight:700;color:{color}'>{r["score"]}</div>
                                <div style='font-size:16px;color:{color};font-weight:600'>{r["category"]} LEAD</div>
                                <div style='font-size:13px;color:#666;margin-top:4px'>{r["action"]}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        except:
                            st.error("Could not reach API")

        with col_b:
            st.markdown("**Current leads**")
            leads_df = pd.DataFrame([
                {"Name":"Vikram Nair",  "Destination":"Swiss, Paris","Score":87,"Category":"HOT"},
                {"Name":"Sanjay Gupta", "Destination":"Australia",   "Score":82,"Category":"HOT"},
                {"Name":"Pooja Iyer",   "Destination":"Maldives",    "Score":76,"Category":"HOT"},
                {"Name":"Rohit Sharma", "Destination":"Dubai",       "Score":65,"Category":"WARM"},
                {"Name":"Sneha Pillai", "Destination":"Thailand",    "Score":58,"Category":"WARM"},
                {"Name":"Arjun Kapoor", "Destination":"Europe",      "Score":22,"Category":"COLD"},
            ])
            st.dataframe(leads_df, use_container_width=True, hide_index=True)
            if st.button("Draft follow-up email for top lead"):
                try:
                    res = requests.post(f"{API_URL}/lead/email",
                        json={"name":"Vikram Nair","destination":"Switzerland"})
                    st.text_area("Email draft", res.json()["email"], height=150)
                except:
                    st.text_area("Email draft",
                        "Hi Vikram,\n\nYour Switzerland holiday package is ready!\n\nWarm regards,\nTravel CRM Team",
                        height=150)

    with tab3:
        st.subheader("Revenue Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Revenue by destination**")
            rev = pd.DataFrame({
                "Destination":["Maldives","Europe","Bali","Dubai","India","Thailand"],
                "Revenue":    [520000,480000,360000,300000,240000,180000]
            })
            st.bar_chart(rev.set_index("Destination"))
        with col2:
            st.markdown("**Monthly bookings trend**")
            monthly = pd.DataFrame({
                "Month":   ["Oct","Nov","Dec","Jan","Feb","Mar"],
                "Bookings":[3,5,8,6,7,9]
            })
            st.line_chart(monthly.set_index("Month"))
        c1,c2,c3 = st.columns(3)
        c1.metric("This month",   "₹3,20,000","+18%")
        c2.metric("Last month",   "₹2,70,000","+12%")
        c3.metric("This quarter", "₹8,40,000","+24%")

    with tab4:
        st.subheader("Customer List")
        search = st.text_input("Search by name or destination")
        customers_df = pd.DataFrame([
            {"Name":"Priya Sharma", "Email":"priya@email.com", "Phone":"+91-9876543210","Bookings":2,"Total Spent":"₹3,20,000","Destinations":"Bali, Maldives"},
            {"Name":"Rahul Verma",  "Email":"rahul@email.com", "Phone":"+91-9876543211","Bookings":1,"Total Spent":"₹2,00,000","Destinations":"Maldives"},
            {"Name":"Anjali Mehta", "Email":"anjali@email.com","Phone":"+91-9876543212","Bookings":1,"Total Spent":"₹1,80,000","Destinations":"Rajasthan"},
            {"Name":"Karan Mehta",  "Email":"karan@email.com", "Phone":"+91-9876543213","Bookings":1,"Total Spent":"₹1,50,000","Destinations":"Dubai"},
            {"Name":"Neha Joshi",   "Email":"neha@email.com",  "Phone":"+91-9876543214","Bookings":1,"Total Spent":"₹4,00,000","Destinations":"Switzerland"},
            {"Name":"Suresh Patel", "Email":"suresh@email.com","Phone":"+91-9876543215","Bookings":2,"Total Spent":"₹1,80,000","Destinations":"Thailand, Bali"},
            {"Name":"Meera Nair",   "Email":"meera@email.com", "Phone":"+91-9876543216","Bookings":1,"Total Spent":"₹3,50,000","Destinations":"Paris"},
            {"Name":"Amit Singh",   "Email":"amit@email.com",  "Phone":"+91-9876543217","Bookings":1,"Total Spent":"₹60,000",  "Destinations":"Kerala"},
        ])
        if search:
            customers_df = customers_df[
                customers_df["Name"].str.contains(search, case=False) |
                customers_df["Destinations"].str.contains(search, case=False)
            ]
        st.dataframe(customers_df, use_container_width=True, hide_index=True)
