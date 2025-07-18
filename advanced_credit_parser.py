import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

@dataclass
class DerogatoryItem:
    type: str
    details: str
    date: Optional[str] = None
    creditor: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    bureau: Optional[str] = None

class ThreeBureauCreditReportParser:
    def __init__(self, report_text: str):
        self.report_text = report_text
        self.derogatory_items = []
        
    def clean_text(self) -> str:
        """Clean and normalize the credit report text"""
        text = re.sub(r'\s+', ' ', self.report_text)
        text = re.sub(r'(?i)late payment', 'LATE PAYMENT', text)
        text = re.sub(r'(?i)collection', 'COLLECTION', text)
        text = re.sub(r'(?i)charge.?off', 'CHARGE OFF', text)
        text = re.sub(r'(?i)repossession', 'REPOSSESSION', text)
        text = re.sub(r'(?i)bankruptcy', 'BANKRUPTCY', text)
        text = re.sub(r'(?i)child support', 'CHILD SUPPORT', text)
        text = re.sub(r'(?i)inquiry', 'INQUIRY', text)
        return text
    
    def extract_personal_info_errors(self):
        """Extract wrong names and old addresses from 3-bureau format"""
        # Extract inconsistent names across bureaus
        name_matches = re.finditer(
            r'Name\s*\|.*?([A-Z]+\s+[A-Z]+).*?\|\s*([A-Z]+\s+[A-Z]+)?.*?\|\s*([A-Z]+\s+[A-Z]+)?',
            self.report_text
        )
        
        names = set()
        for match in name_matches:
            for i in range(1, 4):
                if match.group(i) and match.group(i).strip() not in ('--', 'NONE REPORTED'):
                    names.add(match.group(i).strip())
        
        if len(names) > 1:
            for name in names:
                self.derogatory_items.append(
                    DerogatoryItem(type="WRONG NAME", details=name)
                )
        
        # Extract old addresses
        address_section = re.search(
            r'CURRENT ADDRESS:.*?PREVIOUS ADDRESS:(.*?)(?:\n\s*\n|\|)',
            self.report_text, re.DOTALL
        )
        
        if address_section:
            addresses = re.finditer(
                r'(\d+.+?(?:\d{5}|\|))',
                address_section.group(1)
            )
            for addr in addresses:
                address = addr.group(1).replace('|', '').strip()
                if address and "current address" not in address.lower():
                    self.derogatory_items.append(
                        DerogatoryItem(type="OLD ADDRESS", details=address)
                    )
    
    def extract_account_derogatories(self):
        """Extract derogatory account information from the detailed account sections"""
        # Pattern to find account sections
        account_sections = re.finditer(
            r'(\w+[/-]\w+)\s*\|.*?Account #:.*?High Balance:.*?Account Rating:\s*(.*?)\n.*?'
            r'Account Status:\s*(.*?)\n.*?Payment Status:\s*(.*?)\n.*?Creditor Remarks:\s*(.*?)(?:\n\s*\n|\|)',
            self.report_text, re.DOTALL
        )
        
        for section in account_sections:
            creditor = section.group(1)
            rating = section.group(2).strip()
            status = section.group(3).strip()
            payment_status = section.group(4).strip()
            remarks = section.group(5).strip()
            
            # Determine derogatory type based on status and remarks
            derog_type = None
            if 'Derogatory' in rating:
                if 'Collection' in payment_status or 'Placed for collection' in remarks:
                    derog_type = 'COLLECTION'
                elif 'Chargeoff' in payment_status or 'Charged off' in remarks:
                    derog_type = 'CHARGE OFF'
                elif 'Late' in payment_status:
                    derog_type = 'LATE PAYMENT'
                elif 'Repossession' in remarks:
                    derog_type = 'REPOSSESSION'
                else:
                    derog_type = 'DEROGATORY ACCOUNT'
            
            if derog_type:
                # Extract amount if available
                amount_match = re.search(
                    r'Balance Owed:\s*[\$]?\s*([\d,]+\.\d{2})', 
                    section.group(0)
                )
                amount = float(amount_match.group(1).replace(',', '')) if amount_match else None
                
                # Extract date if available
                date_match = re.search(
                    r'Date Reported:\s*(\d{2}/\d{2}/\d{4})',
                    section.group(0)
                )
                date = date_match.group(1) if date_match else None
                
                self.derogatory_items.append(
                    DerogatoryItem(
                        type=derog_type,
                        details=f"{creditor}: {remarks}",
                        date=date,
                        amount=amount,
                        creditor=creditor,
                        status=payment_status
                    )
                )
    
    def extract_public_records(self):
        """Extract public records like bankruptcies"""
        bankruptcy_match = re.search(
            r'BANKRUPTCY:\s*(.*?)\s*Date:\s*(\d{2}/\d{2}/\d{4}).*?Case #:\s*(.*?)\n',
            self.report_text, re.DOTALL
        )
        
        if bankruptcy_match:
            self.derogatory_items.append(
                DerogatoryItem(
                    type="BANKRUPTCY",
                    details=f"{bankruptcy_match.group(1)} (Case #{bankruptcy_match.group(3)})",
                    date=bankruptcy_match.group(2)
                )
            )
    
    def extract_hard_inquiries(self):
        """Extract hard inquiries from the inquiries section"""
        inquiries = re.finditer(
            r'Inquiries.*?Creditor Name\s*\|.*?Date of Inquiry\s*\|.*?Credit Bureau\s*\|(.*?)(?:\n\s*\n|\|)',
            self.report_text, re.DOTALL
        )
        
        for inquiry_section in inquiries:
            inquiry_matches = re.finditer(
                r'([A-Z].*?)\s*\|\s*(\d{2}/\d{2}/\d{4})\s*\|\s*(TransUnion|Experian|Equifax)',
                inquiry_section.group(1)
            )
            for match in inquiry_matches:
                self.derogatory_items.append(
                    DerogatoryItem(
                        type="HARD INQUIRY",
                        details=match.group(1),
                        date=match.group(2),
                        bureau=match.group(3)
                    )
                )
    
    def parse_all(self):
        """Run all extraction methods"""
        self.report_text = self.clean_text()
        self.extract_personal_info_errors()
        self.extract_account_derogatories()
        self.extract_public_records()
        self.extract_hard_inquiries()
        return self.derogatory_items
    
    def generate_dispute_letters(self, user_name: str, user_address: str, output_format: str = "text") -> str:
        """Generate dispute letters tailored to 3-bureau reports"""
        if not self.derogatory_items:
            return "No derogatory items found to dispute."
        
        letters = []
        items_by_type = {}
        
        for item in self.derogatory_items:
            if item.type not in items_by_type:
                items_by_type[item.type] = []
            items_by_type[item.type].append(item)
        
        for item_type, items in items_by_type.items():
            letter = f"DISPUTE LETTER FOR {item_type}\n\n"
            letter += "Credit Bureaus:\n"
            letter += "- TransUnion\n- Experian\n- Equifax\n\n"
            letter += f"Your Name: {user_name}\n"
            letter += f"Current Address: {user_address}\n"
            letter += f"Date: {datetime.now().strftime('%m/%d/%Y')}\n\n"
            
            letter += "Dear Credit Bureau,\n\n"
            letter += f"I am writing to dispute the following {item_type.lower()} information on my credit report. "\
                    "This information is inaccurate and does not belong to me. "\
                    "Please investigate and remove or correct this information as soon as possible.\n\n"
            
            for item in items:
                letter += f"- Item: {item.details}\n"
                if item.date:
                    letter += f"  Date: {item.date}\n"
                if item.creditor:
                    letter += f"  Creditor: {item.creditor}\n"
                if item.amount:
                    letter += f"  Amount: ${item.amount:,.2f}\n"
                if item.bureau:
                    letter += f"  Bureau: {item.bureau}\n"
                letter += "\n"
            
            letter += "The reported information is incorrect. Please provide me with documentation verifying this information. "\
                    "If you cannot verify this information, please delete it from my credit file immediately.\n\n"
            
            letter += "Enclosed are copies of my driver's license and utility bill to verify my identity. "\
                    "Please investigate this matter and correct any inaccurate information within 30 days as required by law.\n\n"
            
            letter += f"Sincerely,\n{user_name}\n"
            letter += "[YOUR SOCIAL SECURITY NUMBER]\n"
            letter += "[DATE OF BIRTH]\n"
            
            letters.append(letter)
        
        if output_format.lower() == "json":
            return json.dumps([letter for letter in letters], indent=2)
        return "\n\n" + "="*80 + "\n\n".join(letters)

def process_3bureau_report(report_text: str, user_name: str, user_address: str) -> Tuple[List[DerogatoryItem], str]:
    """Process a 3-bureau credit report and return derogatory items with dispute letters"""
    parser = ThreeBureauCreditReportParser(report_text)
    derogatory_items = parser.parse_all()
    dispute_letters = parser.generate_dispute_letters(user_name, user_address)
    return derogatory_items, dispute_letters

# Example usage for testing
if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    CREDIT REPORT
    Name | JOHN DOE | JOHNY DOE | J
