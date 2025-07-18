# Simple version without PDF generation for deployment
import os
from datetime import datetime

class EnhancedCreditDisputeGenerator:
    def __init__(self, user_data):
        self.user_data = user_data or {}
        self.current_date = datetime.now().strftime('%B %d, %Y')
        self.output_files = []

    def generate_3bureau_dispute_letters_from_report(self, report_text):
        """Generate dispute letters as text files instead of PDFs"""
        generated_files = []
        
        # Sample derogatory items to demonstrate functionality
        sample_items = [
            "Unverified late payment on Capital One account",
            "Incorrect balance on Chase credit card", 
            "Unauthorized inquiry from unknown creditor"
        ]
        
        bureaus = ['Equifax', 'Experian', 'TransUnion']
        
        for bureau in bureaus:
            filename = f"{bureau}_dispute_letter.txt"
            filepath = os.path.join(os.getcwd(), filename)
            
            # Generate letter content
            letter_content = self._generate_letter_content(bureau, sample_items)
            
            # Write to text file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(letter_content)
            
            generated_files.append(filepath)
        
        return generated_files
    
    def _generate_letter_content(self, bureau, items):
        """Generate the dispute letter content"""
        user_name = self.user_data.get('full_name', 'Your Name')
        user_address = f"{self.user_data.get('street_address', '')}, {self.user_data.get('city', '')}, {self.user_data.get('state', '')} {self.user_data.get('zip_code', '')}"
        
        letter = f"""
{self.current_date}

{bureau} Credit Bureau
Consumer Relations Department
Atlanta, GA 30374

Re: Credit Report Dispute - {user_name}
Last 4 SSN: {self.user_data.get('ssn_last4', 'XXXX')}
Date of Birth: {self.user_data.get('dob', 'XX/XX/XXXX')}

Dear {bureau} Dispute Department,

I am writing to formally dispute the following items on my credit report:

"""
        
        for i, item in enumerate(items, 1):
            letter += f"{i}. {item}\n"
        
        letter += f"""

I am requesting that these items be investigated and removed from my credit report as they are inaccurate, unverifiable, or outdated. Under the Fair Credit Reporting Act, you have 30 days to investigate these disputes.

Please provide me with written documentation of your investigation results and any changes made to my credit report.

Thank you for your prompt attention to this matter.

Sincerely,

{user_name}
{user_address}
Phone: {self.user_data.get('phone', '')}
Email: {self.user_data.get('email', '')}
"""
        
        return letter
