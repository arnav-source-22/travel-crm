from agents.booking_agent import BookingAgent

class LeadAgent(BookingAgent):

    def score_lead(self, lead: dict) -> str:
        instruction = f"""Score this travel lead:
Name               : {lead['name']}
Destinations       : {lead['destinations']}
Budget             : {lead.get('budget', 'Not specified')}
Travel month       : {lead.get('travel_month', 'Unknown')}
Messages sent      : {lead['message_count']}
Days since contact : {lead['days_since_contact']}
Email responded    : {lead.get('email_responded', False)}"""
        return self._ask(instruction)

    def draft_email(self, name: str, destination: str) -> str:
        instruction = f"Draft a short follow-up email for {name} who is interested in travelling to {destination}."
        return self._ask(instruction)