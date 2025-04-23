import pandas as pd                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
from collections import defaultdict
import re



items_list = [
    "Preference for individual vs group projects (R)",
    "Acceptance to feedback.",
    "Anger and frustration",
    "Completing tasks on time",
    "Forgetting to return others' belongings (moral values are measured) (R)",
    "Sabotaging if working against will. (R)",
    "Feeling uncomfortable if competency is challenged. (R)",
    "Preference to work in groups.",
    "Taking impulsive decisions",
    "Altering information (R)",
    "Unable to take criticism. (R)",
    "Enjoying helping others.",
    "Unable to wait in lines. (R)",
    "Working right away on task.",
    "Breaking traffic signals. (R)",
    "Making sarcastic remarks. (R)",
    "Giving justifications for mistakes. (R)",
    "Overcoming situations",
    "Feeling responsible towards institute.",
    "Willing to do anything. (R)",
    "Open to different temperaments",
    "Taking assistance from others",
    "Comparing others' achievements with self-limitations (R)",
    "Leaving a task pending (R)",
    "Correcting people when they are wrong irrespective of their age",
    "Improving oneself",
    "Ask for help",
    "not Understand others' emotions. (R)",
    "Take shortcuts. (R)",
    "Not expressing oneself. (R)",
    "Speaking up if someone is acting against the norms. (R)",
    "Adapt to change",
    "not Understand own feelings. (R)",
    "Overlook rules. (R)",
    "Aggressive. (R)",
    "Changing ways of work.",
    "Doing tasks carefully.",
    "Low motivation to work if mistakes are made. (R)",
    "Willingness to alter information. (R)",
    "Expressing anger passively. (R)",
    "Moving on to a task without completing current one (R)",
    "Open to criticism.",
    "Stubborn. (R)",
    "Change oneself with time.",
    "Waiting impacts mood. (R)",
    "Thinking of new solutions",
    "Traffic annoys me (R)",
    "Easy to handle unforeseen situations"
]





correlated_domains = {
    "Ability to work with others": ["Openness to individuality"],
    "Emotional Composure": ["Insightfulness", "Patience", "Emotional Management"],
    "Insightfulness": ["Emotional Composure", "Patience", "Passive aggression", "Emotional Management"],
    "Emotional Management": ["Emotional Composure", "Patience", "Passive aggression", "Insightfulness"],
    "Passive aggression": ["Insightfulness", "Patience", "Emotional Composure", "Emotional Management"],
    "Problem solving": ["Openness to new experiences"],
    "Patience": ["Insightfulness", "Emotional Composure", "Emotional Management"],
    "Dutifulness": ["Moral values", "Moral obligation"],
    "Moral Obligation": ["Moral values", "Fairness", "Dutifulness"],
    "Moral values": ["Moral obligation", "Fairness", "Dutifulness"],
    "Openness to limitations": ["Openness to growth"],
    "Openness to growth": ["Openness to limitations", "Openness to new experiences", "Openness to individuality"],
    "Openness to individuality": ["Teamwork"],
    "Openness to new experiences": ["Problem solving", "Openness to individuality", "Openness to growth"],
}





def extract_name_score(text):
    """
    Extracts the name and score from a string like 'SELF-CONTROL (80)'.
    Returns: ('SELF-CONTROL', 80.0)
    """
    if isinstance(text, str):
        match = re.match(r'(.+?)\s*\(([\d.]+)\)', text)
        if match:
            name, score = match.groups()
            return name.strip(), float(score)
    return text, None





def extract_score(file_path):
    """
    Extract scores from Excel file with multiple sheets
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        List of dictionaries containing domain and subdomain scores for each sheet
    """
    # Load all sheets from the Excel file
    excel_file = pd.ExcelFile(file_path)
    all_results = []
    
    # Process each sheet
    for sheet_name in excel_file.sheet_names:
        # Load the sheet (skip initial header rows to access actual data)
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=3)
        
        # Skip if sheet is empty or doesn't have required columns
        # if df.empty or not all(col in df.columns for col in ['Domain', 'Subdomain', 'Subdomain Total', 'Subdomain Obtained']):
        #     continue
            
        # Rename columns for easier access
        df.columns = ['Sr No', 'Domain', 'Subdomain', 'Items', 'Subdomain Total', 'Subdomain Obtained']
        
        # Fill missing domain values downward
        df['Domain'] = df['Domain'].ffill()

        
        # Drop rows with missing subdomain or score data
        df = df.dropna(subset=['Subdomain', 'Subdomain Total', 'Subdomain Obtained'])
        
        result = []
        current_domain = None
        
        # Iterate over each row and build structured output
        for _, row in df.iterrows():
            domain_name, domain_score = extract_name_score(row['Domain'])
            subdomain_name, subdomain_score = extract_name_score(row['Subdomain'])
            
            # If we encounter a new domain, push the previous and start a new one
            if current_domain is None or current_domain['name'] != domain_name:
                if current_domain:
                    result.append(current_domain)
                current_domain = {
                    'name': domain_name,
                    'score': domain_score,
                    'subdomains': []
                }
            
            current_domain['subdomains'].append({
                'name': subdomain_name,
                'score': subdomain_score
            })
        
        # Add the last domain
        if current_domain:
            result.append(current_domain)
            
        # Add sheet results to all_results
        all_results.append({
            'sheet_name': sheet_name,
            'data': result
        })

    for result in all_results:
        for domain in result["data"]:
            if domain["name"].lower() == "emotional stability":
                for sub_domain in domain["subdomains"]:
                    name_lower = sub_domain["name"].lower()
                    if name_lower == "self-control":
                        sub_domain["name"] = "Emotional Composure"
                    elif name_lower == "self-regulation":
                        sub_domain["name"] = "Emotional Management"

    
    return all_results





def extract_items(file_path):
    # Load all sheets from the Excel file
    excel_file = pd.ExcelFile(file_path)
    all_results = []
    
    # Process each sheet
    for sheet_name in excel_file.sheet_names:
        # Load the sheet (skip initial header rows to access actual data)
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1)
        
        # Skip if sheet is empty or doesn't have required columns
        # if df.empty or not all(col in df.columns for col in ["Sub-Domain", "Question Value Name"]):
        #     continue
            
        sub_domain_column = df["Sub-Domain"].tolist()
        question_selected = df["Question Value Name"].tolist()
        
        # Check Response Biasness present in the data
        response_bias, high_response_bias = check_response_bias(question_selected)
        
        # Update overall bias flags
        # overall_response_bias = overall_response_bias or response_bias
        # overall_high_response_bias = overall_high_response_bias or high_response_bias
        
        # Dictionary to store multiple values per key
        grouped_values = defaultdict(list)
        
        for sub_domain, selected_option, item in zip(sub_domain_column, question_selected, items_list):
            grouped_values[sub_domain].append([item, selected_option])
        
        # Convert defaultdict to a regular dictionary
        grouped_values = dict(grouped_values)
        
        # Rename sub-domains
        rename_map = {'SELF-CONTROL': 'EMOTIONAL COMPOSURE', 'SELF-REGULATION': 'EMOTIONAL MANAGEMENT'}
        grouped_values = {rename_map.get(k, k): v for k, v in grouped_values.items()}
        
        # Add sheet results to all_results
        all_results.append({
            'sheet_name': sheet_name,
            'data': grouped_values
        })
    
    return all_results, response_bias, high_response_bias



def filter_subdomain(data):
  
  results = {
      "Development areas": [],
      "Strengths": [],
  }
  # Check Social Desireability
  social_desireable, high_social_desireable = check_social_desireablitiy(data)

  for domain in data:
      domain_score = domain["score"]

      for subdomain in domain["subdomains"]:
          sub_name, sub_score = subdomain["name"], subdomain["score"]


          # FAIRNESS-specific rule
          if sub_name == "FAIRNESS":
            if sub_score <= 40:
              results["Development areas"].append({"name": sub_name, "score": sub_score})
            elif sub_score >= 80:
              results['Strengths'].append({"name": sub_name, "score": sub_score})

          # General strength and development categorization
          elif sub_score >= 80:
              results["Strengths"].append({"name": sub_name, "score": sub_score})
          elif sub_score <= 60:
              results["Development areas"].append({"name": sub_name, "score": sub_score})

      # Sort Values of Strength and Weakness       
      results["Strengths"] = sorted(results["Strengths"], key = lambda x:x["score"], reverse = True)
      results["Development areas"] = sorted(results["Development areas"], key = lambda x:x["score"])

  return results, social_desireable, high_social_desireable





def check_response_bias(response_data):
    # Initialize the response bias flag
    response_bias = False
    high_response_bias = False

    # Count how many times "Neutral" appears in the response list
    neutral_count = response_data.count("Neutral")

    # Check for potential response bias based on the number of neutral responses
    if 15 <= neutral_count < 24:
        # Moderate number of neutrals — may indicate some bias
        response_bias = True

    elif neutral_count >= 24:
        # High number of neutrals — likely indicates strong response bias
        analysis = (
            "The individual seems to have taken the test carefully, "
            "possibly to conceal certain aspects of themselves. "
            "The scores may not accurately reflect their traits and skills. "
            "Assessment during the interview is recommended."
        )
        high_response_bias = True
    # Return the result indicating presence or absence of response bias
    return response_bias, high_response_bias





def check_social_desireablitiy(data_score):
    # Initialize counters
    count = 0         # Counts how many subdomains have very high scores (>= 95)
    s_count = 0       # Counts how many subdomains or domains have low scores (<= 60)
    social_desireable = False  # Flag to indicate social desirability pattern
    high_social_desireable = False

    # Loop through each domain and its subdomains
    for domain in data_score:
        for subdomian in domain['subdomains']:
            if subdomian['score'] >= 95:
                count += 1  # High score (possibly faked good impression)
            elif subdomian['score'] <= 60:
                s_count += 1  # Low score

    # Check if any full domain has low overall score
    # for domain in data_score:
    #     if domain['score'] <= 60:
    #         s_count += 1

    # Determine if social desirability is likely
    if count > 5 and s_count == 0:
        social_desireable = True
    elif count > 10:
        high_social_desireable = True
        # This text analysis could be returned or logged for further review
        analysis = (
            "According to the test scores, the candidate seems to have a tendency "
            "to appear in a desirable way. Due to this factor of social desirability, "
            "her test scores may not be interpreted as accurate presentation of her skills."
        )

    return social_desireable, high_social_desireable



