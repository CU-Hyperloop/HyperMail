import os
import json
import random
import time
from typing import Dict, List, Any
import google.generativeai as genai
from app.models import Company
from django.db.utils import ProgrammingError, OperationalError

class GenerateEmails:
    def __init__(self):
        """Initialize the email generator with API keys from environment variables."""
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.gemini_model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash-001')
        
        # Configure the API
        genai.configure(api_key=self.gemini_api_key)
        
        # Initialize Google's Gemini model
        self.model = genai.GenerativeModel(self.gemini_model_name)
    
    def get_existing_companies(self):
        """
        Get a list of company names that already exist in the database.
        Safely handles database errors if table doesn't exist yet.
        """
        try:
            # Query all company names from database
            existing_companies = Company.objects.values_list('name', flat=True)

            return list(existing_companies)
        except (ProgrammingError, OperationalError) as e:
            # Handle case where table doesn't exist yet (migrations not applied)
            print(f"Database error accessing companies (table may not exist yet): {e}")
            return []
        except Exception as e:
            # Handle other unexpected errors
            print(f"Error getting existing companies: {e}")
            return []
    
    def find_companies(self, params: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Find companies that match the specified criteria, excluding ones already in the database.
        
        Args:
            params: Dictionary containing search parameters
                
        Returns:
            List of dictionaries containing company information
        """
        # Get existing companies from database
        existing_companies = self.get_existing_companies()
        
        # Create a timestamp-based seed for true randomness
        timestamp_seed = int(time.time() * 1000) % 10000
        random_seed = random.randint(1, 10000)
        combined_seed = (timestamp_seed + random_seed) % 10000
        
        # Convert existing companies to a comma-separated string, but limit length
        # to avoid making the prompt too long
        if len(existing_companies) > 50:
            # Sample a subset of companies if there are too many
            company_sample = random.sample(existing_companies, 50)
            existing_str = ", ".join(company_sample)
            total_count = len(existing_companies)
            existing_str += f" and {total_count - 50} others"
        else:
            existing_str = ", ".join(existing_companies)
        
        prompt = f"""
        Find 3 UNIQUE companies that match these criteria:
        Industry: {params.get('industry', 'Any')}
        Size: {params.get('size', 'Any')}
        Location: {params.get('location', 'Any')}
        Sector: {params.get('sector', 'Any')}
        
        IMPORTANT CONSTRAINTS:
        1. DO NOT include any of these companies that are already in our database: {existing_str}
        2. Provide DIFFERENT companies than have been seen before
        3. Each company should be real and verifiable
        4. Random seed: {combined_seed} (use this to ensure different results)
        
        Additional details to consider: {params.get('details', 'None')}
        
        For each company, please provide the following information in JSON format:
        1. name: The company name
        2. website: The company website
        3. email: A relevant contact email if available (or placeholder if not)
        4. description: A brief description of the company (2-3 sentences)
        5. contact_person: Name of a relevant contact person (if available)
        6. key_values: 2-3 company values or mission points that could align with a robotics/engineering team
        7. industry: The company's industry
        8. location: The company's location
        9. size: Approximate company size (Small, Medium, Large)
        
        Return the results as a JSON array of company objects.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.9,  # Higher temperature for more randomness
                    "top_p": 0.95,       # More diverse sampling
                    "top_k": 40,         # Consider more tokens
                    "max_output_tokens": 2048,
                }
            )
            
            # Extract JSON from the response
            raw_text = response.text
            # Find JSON content - look for array structure
            json_start = raw_text.find('[')
            json_end = raw_text.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                companies_json = raw_text[json_start:json_end]
                companies = json.loads(companies_json)
                return companies
            else:
                # If JSON parsing fails, try to process the text format
                return self._parse_text_response(raw_text)
                
        except Exception as e:
            print(f"Error finding companies: {e}")
            return []
    
    def _parse_text_response(self, text: str) -> List[Dict[str, str]]:
        """Parse non-JSON responses into structured data."""
        companies = []
        current_company = {}
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            # New company entry typically starts with a number or company name
            if line.startswith(('1.', '2.', '3.', 'Company 1:', 'Company 2:', 'Company 3:')):
                if current_company and 'name' in current_company:
                    companies.append(current_company)
                current_company = {}
                # Extract company name
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_company['name'] = parts[1].strip()
                else:
                    current_company['name'] = line.lstrip('123. ')
            
            # Parse other fields
            elif ': ' in line:
                key, value = line.split(':', 1)
                key = key.lower().strip()
                value = value.strip()
                
                if key in ('website', 'email', 'description', 'contact person', 'key values', 
                           'industry', 'location', 'size'):
                    # Normalize keys
                    if key == 'contact person':
                        key = 'contact_person'
                    elif key == 'key values':
                        key = 'key_values'
                    current_company[key] = value
        
        # Add the last company
        if current_company and 'name' in current_company:
            companies.append(current_company)
            
        return companies
    
    def generateEmails(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Main method to generate unique companies based on input parameters.
        Does not generate actual email content.
        
        Args:
            params: Dictionary containing generation parameters
                - industry: Industry of the company
                - size: Size of the company
                - sector: Sector of the company
                - location: Location of the company
                - vibe: Not used for company search
                - details: Additional details for customization
                
        Returns:
            Dictionary containing generated companies
        """
        # Find matching companies (that don't exist in DB)
        companies = self.find_companies(params)
        
        # Return companies without generating emails
        results = {
            "companies": companies,
        }
        
        return results