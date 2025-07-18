import os
from datetime import datetime

class EnhancedCreditDisputeGenerator:
    def __init__(self, user_data):
        self.user_data = user_data or {}
        self.current_date = datetime.now().strftime('%B %d, %Y')
        self.output_files = []

    def generate_3bureau_dispute_letters_from_report(self, report_text):
        generated_files = []
        
        sample_items = [
            "Unverified late payment on Capital One account",
            "Incorrect balance on Chase credit card", 
            "Unauthorized inquiry from unknown creditor"
        ]
        
        bureaus = ['Equifax', 'Experian', 'TransUnion']
        
        for bureau in bureaus:
            filename = bureau + "_dispute_letter.txt"
            filepath = os.path.join(os.getcwd(), filename)
            
            letter_content = self._generate_letter_content(bureau, sample_items)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(letter_content)
            
            generated_files.append(filepath)
        
        return generated_files
    
    def _generate_letter_content(self, bureau, items):
        user_name = self.user_data.get('full_name', 'Your Name')
        street = self.user_data.get('street_address', '')
        city = self.user_data.get('city', '')
        state = self.user_data.get('state', '')
        zip_code = self.user_data.get('zip_code', '')
        user_address = street + ", " + city + ", " + state + " " + zip_code
        
        letter = self.current_date + "\n\n"
        letter += bureau + " Credit Bureau\n"
        letter += "Consumer Relations Department\n"
        letter += "Atlanta, GA 30374\n\n"
        letter += "Re: Credit Report Dispute - " + user_name + "\n"
        letter += "Last 4 SSN: " + self.user_data.get('ssn_last4', 'XXXX') + "\n"
        letter += "Date of Birth: " + self.user_data.get('dob', 'XX/XX/XXXX') + "\n\n"
        letter += "Dear " + bureau + " Dispute Department,\n\n"
        letter += "I am writing to formally dispute the following items on my credit report:\n\n"
        
        for i, item in enumerate(items, 1):
            letter += str(i) + ". " + item + "\n"
        
        letter += "\nI am requesting that these items be investigated and removed from my credit report as they are inaccurate, unverifiable, or outdated. Under the Fair Credit Reporting Act, you have 30 days to investigate these disputes.\n\n"
        letter += "Please provide me with written documentation of your investigation results and any changes made to my credit report.\n\n"
        letter += "Thank you for your prompt attention to this matter.\n\n"
        letter += "Sincerely,\n\n"
        letter += user_name + "\n"
        letter += user_address + "\n"
        letter += "Phone: " + self.user_data.get('phone', '') + "\n"
        letter += "Email: " + self.user_data.get('email', '') + "\n"
        
        return letter
