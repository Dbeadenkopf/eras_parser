import re
from PyPDF2 import PdfReader



def parse_visa_status(text):
    results = {}
    if re.search(r"My\s*ERAS\s*Application", text, re.I):
        auth_match = re.search(r"Authorized\s+to\s+Work\s+in\s+the\s+U\.?S\.?\s*:\s*(Yes|No)", text, re.I)
        if auth_match:
            results["Authorized_to_Work_in_US"] = auth_match.group(1).strip()
            
            if auth_match.group(1).lower() == "yes":
                cwa = re.search(r"Current\s+Work\s+Authorization\s*:\s*([^\n\r]+)", text, re.I)
                if cwa:
                    results["Current_Work_Authorization"] = cwa.group(1).strip()
            else:
                vsn = re.search(r"Visa\s+Sponsorship\s+Needed\s*:\s*([^\n\r]+)", text, re.I)
                vss = re.search(r"Visa\s+Sponsorship\s+Sought\s*:\s*([^\n\r]+)", text, re.I)
                if vsn:
                    results["Visa_Sponsorship_Needed"] = vsn.group(1).strip()
                if vss:
                    results["Visa_Sponsorship_Sought"] = vss.group(1).strip()
    return results


def parse_usmle_transcript(text):
    results = {}

    if re.search(r"USMLE Transcript", text, re.I) and re.search(r"United\s+States\s+Medical\s+Licensing\s+Examination", text, re.I):
        # Step 1
        step1_matches = re.findall(r"Step\s*1.*?(\d{1,2}/\d{1,2}/\d{4}).*?\b(Pass|Fail)\b(?:.*?(\d{3}))?", text, re.I)
        step1_clean = []
        seen = set()
        for d, r, s in step1_matches:
            key = (d, r.lower(), s)
            if key not in seen:
                seen.add(key)
                step1_clean.append({"Date": d, "Result": r.capitalize(), "Score": s if s else None})
        results["Step_1_Attempts"] = step1_clean
        results["Step_1_Failures"] = sum(1 for x in step1_clean if x["Result"].lower() == "fail")

        # Step 2
        step2_matches = re.findall(r"Step\s*2.*?(\d{1,2}/\d{1,2}/\d{4}).*?\b(Pass|Fail)\b(?:.*?(\d{3}))?", text, re.I)
        step2_clean = []
        seen2 = set()
        for d, r, s in step2_matches:
            key = (d, r.lower(), s)
            if key not in seen2:
                seen2.add(key)
                step2_clean.append({"Date": d, "Result": r.capitalize(), "Score": s if s else None})
        results["Step_2_Attempts"] = step2_clean
        results["Step_2_Failures"] = sum(1 for x in step2_clean if x["Result"].lower() == "fail")

    return results


def parse_ecfmg_status(text):
    results = {"ECFMG_Certified": "Not Available"}
    if re.search(r"ECFMG Status Report", text, re.I):
        match = re.search(r"ECFMG Certified\s*:\s*(Yes|No)", text, re.I)
        if match:
            results["ECFMG_Certified"] = match.group(1).strip()

        issue_date = re.search(r"Certificate Issue Date\s*:\s*([^\n\r]+)", text, re.I)
        valid_through = re.search(r"Valid Through\s*:\s*([^\n\r]+)", text, re.I)
        if issue_date:
            results["Certificate_Issue_Date"] = issue_date.group(1).strip()
        if valid_through:
            results["Valid_Through"] = valid_through.group(1).strip()

    return results


if __name__ == "__main__":
    reader = PdfReader("/Users/davidbeadenkopf/Desktop/programming stuff/DB/eras_parser/HaruyaHirotaheadercuts.pdf")

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    print("Visa Info:", parse_visa_status(text))
    print("USMLE Info:", parse_usmle_transcript(text))
    print("ECFMG Info:", parse_ecfmg_status(text))
