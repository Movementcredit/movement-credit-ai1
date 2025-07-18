# ---
# Main generator class for dispute letters
from fpdf import FPDF
import os

class EnhancedCreditDisputeGenerator:
    def __init__(self, user_data):
        self.user_data = user_data or {}
        self.current_date = 'July 15, 2025'
        self.output_files = []

    def generate_3bureau_dispute_letters_from_report(self, report_text_or_path):
        if report_text_or_path.lower().endswith('.txt'):
            bureau_derog_data = extract_derogatory_data_from_txt(report_text_or_path)
            derogatory_items = []
            for bureau, items in bureau_derog_data.items():
                for item in items:
                    derogatory_items.append(type('DerogItem', (), {
                        'type': item.get('Status', 'DEROGATORY'),
                        'details': f"Creditor: {item.get('Creditor','')} | Account #: {item.get('Account Number','')} | Balance: {item.get('Balance','')} | Dispute: {item.get('Dispute Status','')} | Past Due: {item.get('Past Due Amount','')} | 30/60/90: {item.get('Late 30','')}/{item.get('Late 60','')}/{item.get('Late 90','')}",
                        'date': None,
                        'creditor': item.get('Creditor'),
                        'amount': item.get('Balance'),
                        'bureau': bureau
                    })())
        else:
            raise NotImplementedError('Only .txt reports are supported in this version.')
        if not derogatory_items:
            return []
        output_folder = "uploads"
        os.makedirs(output_folder, exist_ok=True)
        full_name = self.user_data.get('full_name', '')
        self.output_files = []
        for item in derogatory_items:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, f"DISPUTE LETTER FOR {item.type}", 0, 1)
            pdf.set_font('Helvetica', '', 12)
            pdf.cell(0, 10, f"Name: {full_name}", 0, 1)
            pdf.cell(0, 10, f"Address: {self.user_data.get('street_address', '')}, {self.user_data.get('city', '')}, {self.user_data.get('state', '')} {self.user_data.get('zip_code', '')}", 0, 1)
            pdf.cell(0, 10, f"Date: {self.current_date}", 0, 1)
            pdf.ln(5)
            amount_str = ""
            if hasattr(item, 'amount') and item.amount:
                try:
                    amount_val = float(str(item.amount).replace(',', '').replace('$', ''))
                    amount_str = f"  Amount: ${amount_val:,.2f}"
                except Exception:
                    amount_str = f"  Amount: {item.amount}"
            letter_body = (
                f"Dear Credit Bureau,\n\n"
                f"I am writing to dispute the following {item.type.lower()} information on my credit report. This information is inaccurate and does not belong to me. Please investigate and remove or correct this information as soon as possible.\n\n"
                f"- Item: {item.details}\n"
                f"{f'  Date: {item.date}' if hasattr(item, 'date') and item.date else ''}\n"
                f"{f'  Creditor: {item.creditor}' if hasattr(item, 'creditor') and item.creditor else ''}\n"
                f"{amount_str}\n"
                f"{f'  Bureau: {item.bureau}' if hasattr(item, 'bureau') and item.bureau else ''}\n\n"
                "The reported information is incorrect. Please provide me with documentation verifying this information. If you cannot verify this information, please delete it from my credit file immediately.\n\n"
                "Enclosed are copies of my driver's license, utility bill, and credit report to verify my identity. Please investigate this matter and correct any inaccurate information within 30 days as required by law.\n\n"
                f"Sincerely,\n{full_name}\n"
            )
            pdf.multi_cell(0, 8, letter_body)
            filename = os.path.join(
                output_folder,
                f"3Bureau_Dispute_{safe_filename(item.type)}_{safe_filename(full_name)}.pdf"
            )
            pdf.output(filename, 'F')
            pdf.close()
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print(f"PDF generated: {filename} ({os.path.getsize(filename)} bytes)")
                self.output_files.append(filename)
            else:
                print(f"PDF generation failed or file empty: {filename}")
        return self.output_files
import re
from collections import defaultdict
def extract_derogatory_data_from_txt(txt_path):
    derogatory_data = defaultdict(list)

    with open(txt_path, 'r', encoding='utf-8') as file:
        full_text = file.read()

    # Normalize and segment by bureau (case-insensitive, handles ® or not)
    bureau_sections = re.split(r"(transunion[®]?|experian[®]?|equifax[®]?)", full_text, flags=re.IGNORECASE)

    for i in range(1, len(bureau_sections), 2):
        bureau = bureau_sections[i].replace("®", "").capitalize()
        section = bureau_sections[i + 1]
        # Find derogatory account blocks (robust: match lines containing Derogatory, Collection, or Charge-off and grab following lines)
        derog_blocks = []
        lines = section.splitlines()
        block = []
        in_block = False
        for line in lines:
            if re.search(r"Derogatory|Collection|Charge[- ]?off", line, re.IGNORECASE):
                if block:
                    derog_blocks.append("\n".join(block))
                    block = []
                in_block = True
            if in_block:
                block.append(line)
                # Heuristic: end block if we hit a blank line or a new section
                if line.strip() == '' or re.match(r'^[A-Z][A-Za-z\s]+:$', line):
                    derog_blocks.append("\n".join(block))
                    block = []
                    in_block = False
        if block:
            derog_blocks.append("\n".join(block))
        for block in derog_blocks:
            account_info = {}
            creditor_match = re.search(r"(?:Account\s+#.*?\n)?([A-Z0-9\s\-/&]+)\n", block)
            account_info["Creditor"] = creditor_match.group(1).strip() if creditor_match else "UNKNOWN"
            acc_num = re.search(r"Account\s+#\s*([A-Z0-9*]+)", block)
            account_info["Account Number"] = acc_num.group(1) if acc_num else "N/A"
            balance_match = re.search(r"Balance Owed:\s*\$?([0-9,]+)", block)
            account_info["Balance"] = balance_match.group(1) if balance_match else "Unknown"
            if re.search(r"Charge[- ]?off|Charged off", block, re.IGNORECASE):
                account_info["Status"] = "Charge-off"
            elif re.search(r"Collection", block, re.IGNORECASE):
                account_info["Status"] = "Collection"
            else:
                account_info["Status"] = "Derogatory"
            if "dispute" in block.lower():
                account_info["Dispute Status"] = "Disputed"
            else:
                account_info["Dispute Status"] = "Not Disputed"
            past_due_match = re.search(r"Past Due Amount:\s*\$?([0-9,]+)", block)
            account_info["Past Due Amount"] = past_due_match.group(1) if past_due_match else "N/A"
            late_30 = re.search(r"30:\s*([0-9]+)", block)
            late_60 = re.search(r"60:\s*([0-9]+)", block)
            late_90 = re.search(r"90:\s*([0-9]+)", block)
            account_info["Late 30"] = late_30.group(1) if late_30 else "0"
            account_info["Late 60"] = late_60.group(1) if late_60 else "0"
            account_info["Late 90"] = late_90.group(1) if late_90 else "0"
            derogatory_data[bureau].append(account_info)
    return derogatory_data

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name or '')


# ---
# Local parser now used. No external API required.
