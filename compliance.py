from langchain_openai import ChatOpenAI
import re
import json

def extract_financial_values(text):
    patterns = {
        'interest_rates': r'(\d+\.?\d*)\s*%',
        'loan_amounts': r'\$\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{2})?',
        'time_periods': r'(\d+)\s*(year|month|day)s?',
        'fees': r'fee of \$\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{2})?'
    }
    
    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            if key == 'interest_rates':
                results[key] = [float(match) for match in matches]
            elif key == 'loan_amounts' or key == 'fees':
                results[key] = [match.replace('$', '').replace(',', '') for match in matches]
            elif key == 'time_periods':
                results[key] = [{'value': int(match[0]), 'unit': match[1]} for match in matches]
    
    return results

def verify_compliance(answer, regulations, llm=None):
    if llm is None:
        llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    
    financial_values = extract_financial_values(answer)
    
    verification_prompt = f"""
    As a banking compliance expert, verify if the following answer complies with regulations:
    
    Answer: {answer}
    
    Extracted financial values: {json.dumps(financial_values)}
    
    Relevant regulations: {regulations}
    
    Check for:
    1. Interest rate accuracy
    2. Fee disclosure compliance
    3. Term representation accuracy
    4. Regulatory citation accuracy
    
    Return a JSON with the following structure:
    {{
        "compliant": true/false,
        "issues": ["issue1", "issue2"],
        "corrections": ["correction1", "correction2"],
        "confidence": 0-100
    }}
    """
    
    response = llm.invoke(verification_prompt)
    try:
        result = json.loads(response.content)
        return result
    except:
        return {
            "compliant": False,
            "issues": ["Failed to parse compliance verification result"],
            "corrections": [],
            "confidence": 0
        }

def validate_interest_rate_ranges(rates, product_type):
    # Define acceptable ranges for different product types
    ranges = {
        'mortgage': (2.0, 8.0),
        'personal_loan': (5.0, 36.0),
        'credit_card': (9.0, 29.99),
        'auto_loan': (2.5, 12.0),
        'student_loan': (3.0, 12.0),
        'business_loan': (4.0, 40.0)
    }
    
    if product_type not in ranges:
        return False, f"Unknown product type: {product_type}"
    
    min_rate, max_rate = ranges[product_type]
    
    for rate in rates:
        if rate < min_rate or rate > max_rate:
            return False, f"Interest rate {rate}% is outside acceptable range ({min_rate}%-{max_rate}%) for {product_type}"
    
    return True, "Interest rates within acceptable range"

def check_required_disclosures(text, product_type):
    required_phrases = {
        'mortgage': [
            'annual percentage rate', 
            'closing costs',
            'loan term'
        ],
        'personal_loan': [
            'annual percentage rate',
            'finance charge',
            'total payments'
        ],
        'credit_card': [
            'annual percentage rate',
            'annual fee',
            'minimum payment'
        ]
    }
    
    if product_type not in required_phrases:
        return True, "No specific disclosure requirements defined"
    
    missing_phrases = []
    for phrase in required_phrases[product_type]:
        if phrase.lower() not in text.lower():
            missing_phrases.append(phrase)
    
    if missing_phrases:
        return False, f"Missing required disclosures: {', '.join(missing_phrases)}"
    
    return True, "All required disclosures present" 