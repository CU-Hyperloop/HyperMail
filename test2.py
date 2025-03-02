import os
import time
import re
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
# Update to the non-deprecated import (install with: pip install -U langchain-google-community)
try:
    from langchain_google_community import GoogleSearchAPIWrapper
except ImportError:
    # Fall back to the deprecated version if the new one isn't installed
    from langchain_community.utilities import GoogleSearchAPIWrapper
    print("Warning: Using deprecated GoogleSearchAPIWrapper. Please install langchain-google-community.")
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")

# Set up detailed logging
def log_section(section_name):
    """Print a section header for better logging visibility"""
    print("\n" + "="*50)
    print(f"  {section_name}")
    print("="*50)

class RelationshipIntelligenceEngine:
    """
    A sophisticated Relationship Intelligence Engine that enhances email personalization
    by analyzing decision-makers, strategic partnership opportunities, and cultural compatibility.
    """
    
    def __init__(self, llm, search):
        """Initialize the relationship intelligence engine with necessary components"""
        self.llm = llm
        self.search = search
        self.contact_profiles = {}  # Store profiles of contacts
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("RelationshipIntelligence")
    
    def profile_decision_makers(self, company_name):
        """Research and profile likely sponsorship decision-makers at the company."""
        log_section("PROFILING DECISION MAKERS")
        
        # Check for cached profiles
        cache_dir = os.path.join(os.getcwd(), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"contacts_{company_name.replace(' ', '_').lower()}.json")
        
        if os.path.exists(cache_file):
            try:
                print(f"Loading cached contact profiles for {company_name}")
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    print(f"  ✓ Found cached profiles from {cached_data.get('timestamp', 'unknown date')}")
                    self.contact_profiles = cached_data.get('profiles', {})
                    return self.contact_profiles
            except Exception as e:
                print(f"  ❌ Error loading cache: {str(e)}")
                print("  Proceeding with fresh research...")
        
        # Create search queries to find relevant contacts
        search_queries = [
            f"{company_name} sponsorship manager linkedin",
            f"{company_name} marketing director linkedin",
            f"{company_name} corporate social responsibility lead",
            f"{company_name} community relations manager",
            f"{company_name} engineering director"
        ]
        
        # Collect search results for potential contacts
        contact_search_results = []
        for i, query in enumerate(search_queries):
            try:
                print(f"\nContact search query {i+1}/{len(search_queries)}:")
                print(f"  {query}")
                
                start_time = time.time()
                results = self.search.results(query, num_results=3)
                end_time = time.time()
                
                print(f"  ✓ Got {len(results)} results ({end_time - start_time:.2f}s)")
                
                for j, result in enumerate(results):
                    # Store the result with query context
                    contact_search_results.append({
                        "query_context": query,
                        "title": result['title'],
                        "link": result['link'],
                        "snippet": result['snippet']
                    })
                    print(f"    Result {j+1}: {result['title'][:50]}...")
                
                # Add delay between searches
                delay = 2
                print(f"  Waiting {delay}s before next query...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"  ❌ Error searching for '{query}': {str(e)}")
                # Wait longer after error
                recovery_delay = 5
                print(f"  Waiting {recovery_delay}s to recover from error...")
                time.sleep(recovery_delay)
        
        # Process the search results to identify relevant contacts
        identify_contacts_prompt = PromptTemplate(
            input_variables=["search_results", "company_name"],
            template="""
            Based on these search results about potential contacts at {company_name}, 
            identify the most relevant decision-makers who would likely handle sponsorship requests
            from university engineering clubs:
            
            {search_results}
            
            For each relevant person you can identify, extract:
            1. Full name
            2. Job title/role
            3. Department (if available)
            4. LinkedIn profile URL (if available)
            5. Any indication of their decision-making authority
            6. Any connection to engineering, education, or student initiatives
            
            Format the response as a structured list of the top 3 most relevant people.
            If you cannot identify specific individuals, suggest the most relevant roles/titles
            that would typically handle sponsorship decisions at this type of company.
            """
        )
        
        # Format search results for the prompt
        formatted_results = "\n\n".join([
            f"Search Context: {res['query_context']}\nTitle: {res['title']}\nLink: {res['link']}\nSnippet: {res['snippet']}"
            for res in contact_search_results
        ])
        
        try:
            print("\nIdentifying relevant contacts...")
            prompt = identify_contacts_prompt.format(
                search_results=formatted_results,
                company_name=company_name
            )
            
            start_time = time.time()
            contacts_result = self.llm.invoke(prompt).content
            end_time = time.time()
            
            print(f"  ✓ Contacts identified ({end_time - start_time:.2f}s)")
            
            # For each identified contact, build a more detailed profile
            # Extract contact names using simple regex
            contact_names = re.findall(r'(?:^|\n)(?:\d+\.\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', contacts_result)
            
            if not contact_names:
                print("  No specific contacts identified, using role-based profiles")
                # Extract suggested roles if no specific names were found
                role_matches = re.findall(r'(?:^|\n)(?:\d+\.\s*)?([A-Za-z\s]+Manager|Director|Lead|Head|Officer)', contacts_result)
                # Use the roles as placeholder names
                contact_names = role_matches if role_matches else ["Sponsorship Manager", "Marketing Director", "CSR Lead"]
            
            print(f"  Building profiles for {len(contact_names)} contacts/roles:")
            for i, name in enumerate(contact_names[:3]):  # Limit to top 3
                print(f"    {i+1}. {name}")
                self.build_contact_profile(name, company_name)
                # Add delay between profile builds
                time.sleep(2)
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'profiles': self.contact_profiles,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }, f)
                print(f"  ✓ Contact profiles cached to {cache_file}")
            except Exception as e:
                print(f"  ❌ Error caching profiles: {str(e)}")
            
            return self.contact_profiles
            
        except Exception as e:
            print(f"  ❌ Error identifying contacts: {str(e)}")
            # Create fallback generic profiles
            fallback_titles = ["Marketing Director", "Sponsorship Manager", "Corporate Social Responsibility Lead"]
            for title in fallback_titles:
                self.contact_profiles[title] = {
                    'name': title,
                    'role': title,
                    'background': f"Generic profile for {title} position",
                    'interests': "Technology, innovation, education partnerships",
                    'communication_style': "Professional",
                    'connections': []
                }
            return self.contact_profiles
    
    def build_contact_profile(self, contact_name, company_name):
        """Build a detailed profile for a specific contact."""
        print(f"\nBuilding profile for: {contact_name}")
        
        profile_prompt = PromptTemplate(
            input_variables=["contact_name", "company_name"],
            template="""
            Create a detailed professional profile for {contact_name} at {company_name}.
            If this is a specific person, research their professional background.
            If this is a role/title, create a typical profile for someone in this position.
            
            Include:
            1. Likely educational background
            2. Career trajectory
            3. Professional interests and priorities
            4. Communication style (formal/informal, technical/non-technical, data-driven/relationship-focused)
            5. Possible connections to engineering, education, or student initiatives
            6. Decision-making approach (analytical, collaborative, etc.)
            
            Be specific but realistic. If creating a typical profile for a role rather than a real person,
            clearly indicate this is a "typical profile" rather than specific information.
            """
        )
        
        try:
            prompt = profile_prompt.format(
                contact_name=contact_name,
                company_name=company_name
            )
            
            profile_result = self.llm.invoke(prompt).content
            
            # Look for potential university connections
            connection_prompt = PromptTemplate(
                input_variables=["contact_name", "company_name"],
                template="""
                Research potential connections between {contact_name} at {company_name} and:
                1. University of Colorado Boulder
                2. Engineering education
                3. Student competition teams
                4. Hyperloop or tunnel boring technology
                
                If this is a role rather than a specific person, suggest typical connections
                someone in this position might have to these areas.
                
                List any possible connections you find, even if tentative.
                """
            )
            
            connection_result = self.llm.invoke(
                connection_prompt.format(
                    contact_name=contact_name,
                    company_name=company_name
                )
            ).content
            
            # Analyze their communication style
            communication_prompt = PromptTemplate(
                input_variables=["contact_name", "company_name", "profile"],
                template="""
                Based on this profile for {contact_name} at {company_name}:
                
                {profile}
                
                Analyze their likely communication preferences:
                1. Formality level (very formal to very casual)
                2. Communication medium preference (email, call, meeting)
                3. Information density preference (detailed/technical vs. high-level/conceptual)
                4. Persuasion strategies likely to resonate (data-driven, emotional, social proof, etc.)
                5. Key phrases or terminology that would resonate with their background
                
                Provide specific recommendations for communicating effectively with this person.
                """
            )
            
            communication_result = self.llm.invoke(
                communication_prompt.format(
                    contact_name=contact_name,
                    company_name=company_name,
                    profile=profile_result
                )
            ).content
            
            # Store the complete profile
            self.contact_profiles[contact_name] = {
                'name': contact_name,
                'role': re.search(r'(?:Director|Manager|Lead|Officer|Head)', contact_name) and contact_name or "Decision Maker",
                'profile': profile_result,
                'communication_style': communication_result,
                'connections': connection_result
            }
            
            print(f"  ✓ Profile built for {contact_name}")
            return self.contact_profiles[contact_name]
            
        except Exception as e:
            print(f"  ❌ Error building profile: {str(e)}")
            # Create a minimal fallback profile
            self.contact_profiles[contact_name] = {
                'name': contact_name,
                'role': "Decision Maker",
                'profile': "Professional at " + company_name,
                'communication_style': "Professional, concise communication",
                'connections': "Potential interest in engineering innovation"
            }
            return self.contact_profiles[contact_name]
    
    def analyze_strategic_partnership_potential(self, company_name, club_info):
        """Identify strategic partnership opportunities specific to this company."""
        log_section("ANALYZING STRATEGIC PARTNERSHIP POTENTIAL")
        
        # Check for cached analysis
        cache_dir = os.path.join(os.getcwd(), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"partnership_{company_name.replace(' ', '_').lower()}.json")
        
        if os.path.exists(cache_file):
            try:
                print(f"Loading cached partnership analysis for {company_name}")
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    print(f"  ✓ Found cached analysis from {cached_data.get('timestamp', 'unknown date')}")
                    return cached_data.get('analysis', {})
            except Exception as e:
                print(f"  ❌ Error loading cache: {str(e)}")
                print("  Proceeding with fresh analysis...")
        
        # Research previous sponsorships
        print("\nResearching previous sponsorships...")
        sponsorship_queries = [
            f"{company_name} sponsors university",
            f"{company_name} sponsors engineering competition",
            f"{company_name} university partnership",
            f"{company_name} education sponsorship"
        ]
        
        sponsorship_results = []
        for i, query in enumerate(sponsorship_queries):
            try:
                print(f"\nSponsorship search query {i+1}/{len(sponsorship_queries)}:")
                print(f"  {query}")
                
                results = self.search.results(query, num_results=3)
                
                for result in results:
                    sponsorship_results.append({
                        "query": query,
                        "title": result['title'],
                        "link": result['link'],
                        "snippet": result['snippet']
                    })
                
                # Add delay between searches
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error searching for '{query}': {str(e)}")
                time.sleep(5)  # Longer delay after error
        
        # Analyze strategic initiatives
        print("\nAnalyzing strategic initiatives...")
        initiative_queries = [
            f"{company_name} strategic priorities",
            f"{company_name} innovation focus",
            f"{company_name} technology development",
            f"{company_name} future goals"
        ]
        
        initiative_results = []
        for i, query in enumerate(initiative_queries):
            try:
                print(f"\nInitiative search query {i+1}/{len(initiative_queries)}:")
                print(f"  {query}")
                
                results = self.search.results(query, num_results=3)
                
                for result in results:
                    initiative_results.append({
                        "query": query,
                        "title": result['title'],
                        "link": result['link'],
                        "snippet": result['snippet']
                    })
                
                # Add delay between searches
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error searching for '{query}': {str(e)}")
                time.sleep(5)  # Longer delay after error
        
        # Format club info for the analysis
        formatted_club_info = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in club_info.items()])
        
        # Analyze partnership potential with combined search results
        partnership_prompt = PromptTemplate(
            input_variables=["company_name", "sponsorship_results", "initiative_results", "club_info"],
            template="""
            Analyze the strategic partnership potential between {company_name} and CU Hyperloop 
            based on the following information:
            
            COMPANY'S PREVIOUS SPONSORSHIPS AND PARTNERSHIPS:
            {sponsorship_results}
            
            COMPANY'S STRATEGIC INITIATIVES:
            {initiative_results}
            
            CU HYPERLOOP INFORMATION:
            {club_info}
            
            Please provide:
            
            1. PREVIOUS SPONSORSHIP PATTERNS:
               - Types of organizations they typically sponsor
               - Sponsorship amount ranges (if available)
               - What they expect in return (exposure, recruitment, technology access, etc.)
               
            2. ALIGNMENT AREAS:
               - Specific technical areas where CU Hyperloop's work aligns with company initiatives
               - Educational or workforce development alignments
               - Innovation or R&D alignments
               - Brand or marketing alignments
            
            3. UNIQUE VALUE PROPOSITIONS:
               - What unique value can CU Hyperloop offer this specific company?
               - How might the company benefit from this partnership beyond general goodwill?
               - What specific aspects of CU Hyperloop would most appeal to this company?
               - How could partnership metrics be measured to show ROI for the company?
            
            Be specific, focusing on concrete alignment points rather than generic benefits.
            """
        )
        
        try:
            # Format search results for the prompt
            formatted_sponsorship = "\n\n".join([
                f"Query: {res['query']}\nTitle: {res['title']}\nLink: {res['link']}\nSnippet: {res['snippet']}"
                for res in sponsorship_results
            ])
            
            formatted_initiatives = "\n\n".join([
                f"Query: {res['query']}\nTitle: {res['title']}\nLink: {res['link']}\nSnippet: {res['snippet']}"
                for res in initiative_results
            ])
            
            prompt = partnership_prompt.format(
                company_name=company_name,
                sponsorship_results=formatted_sponsorship,
                initiative_results=formatted_initiatives,
                club_info=formatted_club_info
            )
            
            print("\nAnalyzing strategic partnership potential...")
            partnership_analysis = self.llm.invoke(prompt).content
            
            # Extract specific value propositions
            value_prop_prompt = PromptTemplate(
                input_variables=["company_name", "partnership_analysis"],
                template="""
                Based on this partnership analysis for {company_name} and CU Hyperloop:
                
                {partnership_analysis}
                
                Generate 3-5 specific, unique value propositions that CU Hyperloop could offer {company_name}.
                These should be tailored specifically to this company, not generic benefits.
                
                Format each as:
                1. VALUE PROPOSITION: [one-line statement]
                   DETAILS: [2-3 sentences explaining how this creates value for the company]
                   IMPLEMENTATION: [How CU Hyperloop would deliver on this]
                """
            )
            
            value_propositions = self.llm.invoke(
                value_prop_prompt.format(
                    company_name=company_name,
                    partnership_analysis=partnership_analysis
                )
            ).content
            
            # Compile the complete analysis
            partnership_data = {
                'partnership_analysis': partnership_analysis,
                'value_propositions': value_propositions
            }
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'analysis': partnership_data,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }, f)
                print(f"  ✓ Partnership analysis cached to {cache_file}")
            except Exception as e:
                print(f"  ❌ Error caching analysis: {str(e)}")
            
            return partnership_data
            
        except Exception as e:
            print(f"  ❌ Error analyzing partnership potential: {str(e)}")
            # Create fallback analysis
            fallback_analysis = {
                'partnership_analysis': f"Unable to complete detailed analysis for {company_name} due to API error.",
                'value_propositions': "1. VALUE PROPOSITION: Engineering talent pipeline\n2. VALUE PROPOSITION: Innovation showcase\n3. VALUE PROPOSITION: Brand visibility among engineering students"
            }
            return fallback_analysis
    
    def assess_cultural_compatibility(self, company_name):
        """Analyze corporate culture for better communication matching."""
        log_section("ASSESSING CULTURAL COMPATIBILITY")
        
        # Check for cached assessment
        cache_dir = os.path.join(os.getcwd(), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"culture_{company_name.replace(' ', '_').lower()}.json")
        
        if os.path.exists(cache_file):
            try:
                print(f"Loading cached cultural assessment for {company_name}")
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    print(f"  ✓ Found cached assessment from {cached_data.get('timestamp', 'unknown date')}")
                    return cached_data.get('assessment', {})
            except Exception as e:
                print(f"  ❌ Error loading cache: {str(e)}")
                print("  Proceeding with fresh assessment...")
        
        # Collect communication samples
        print("\nCollecting communication samples...")
        communication_queries = [
            f"{company_name} press release",
            f"{company_name} blog",
            f"{company_name} about us",
            f"{company_name} mission statement",
            f"{company_name} values"
        ]
        
        communication_samples = []
        for i, query in enumerate(communication_queries):
            try:
                print(f"\nCommunication sample query {i+1}/{len(communication_queries)}:")
                print(f"  {query}")
                
                results = self.search.results(query, num_results=3)
                
                for result in results:
                    communication_samples.append({
                        "context": query,
                        "title": result['title'],
                        "snippet": result['snippet']
                    })
                
                # Add delay between searches
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error searching for '{query}': {str(e)}")
                time.sleep(5)  # Longer delay after error
        
        # Analyze language patterns
        language_prompt = PromptTemplate(
            input_variables=["company_name", "communication_samples"],
            template="""
            Analyze the language patterns used by {company_name} in these communication samples:
            
            {communication_samples}
            
            Please analyze:
            
            1. FORMALITY LEVEL:
               - How formal/informal is their communication?
               - Do they use technical jargon or plain language?
               - Do they use first person (we, our) or third person?
            
            2. TONE AND EMOTIONAL ATTRIBUTES:
               - What emotional tone do they use (enthusiastic, restrained, ambitious, etc.)?
               - How do they express values and priorities?
               - Do they emphasize innovation, tradition, reliability, etc.?
            
            3. SENTENCE STRUCTURE AND COMPLEXITY:
               - Do they use simple, direct sentences or complex, nuanced phrasing?
               - How technical is their language?
               - What reading level would you estimate for their content?
            
            4. KEY TERMINOLOGY AND PHRASES:
               - What specific industry terms or company-specific vocabulary do they use?
               - Are there recurring phrases or concepts?
               - What words do they use to describe themselves?
            
            Conclude with specific recommendations for matching their communication style.
            """
        )
        
        try:
            # Format communication samples for the prompt
            formatted_samples = "\n\n".join([
                f"Context: {sample['context']}\nTitle: {sample['title']}\nSnippet: {sample['snippet']}"
                for sample in communication_samples
            ])
            
            prompt = language_prompt.format(
                company_name=company_name,
                communication_samples=formatted_samples
            )
            
            print("\nAnalyzing language patterns...")
            language_analysis = self.llm.invoke(prompt).content
            
            # Determine decision-making style
            decision_prompt = PromptTemplate(
                input_variables=["company_name", "communication_samples"],
                template="""
                Based on these communication samples from {company_name}:
                
                {communication_samples}
                
                Analyze their likely decision-making style:
                
                1. How do they appear to make decisions? (data-driven, intuitive, consensus-based, etc.)
                2. What values seem to drive their decisions? (innovation, reliability, cost-efficiency, etc.)
                3. What kind of evidence or reasoning would likely persuade them?
                4. Do they seem to prefer long-term strategic thinking or short-term practical results?
                5. How might they evaluate sponsorship opportunities specifically?
                
                Conclude with specific recommendations for framing requests to align with their decision-making style.
                """
            )
            
            print("\nAnalyzing decision-making style...")
            decision_style = self.llm.invoke(
                decision_prompt.format(
                    company_name=company_name,
                    communication_samples=formatted_samples
                )
            ).content
            
            # Extract cultural values
            values_prompt = PromptTemplate(
                input_variables=["company_name", "communication_samples"],
                template="""
                Based on these communication samples from {company_name}:
                
                {communication_samples}
                
                Extract their core cultural values:
                
                1. What principles or ideals do they explicitly state as important?
                2. What values are implied by their language and priorities?
                3. How do they position themselves in relation to their industry, community, and society?
                4. What do they seem to be most proud of as an organization?
                
                List 5-7 specific values with a brief explanation of how each is expressed.
                Then suggest how CU Hyperloop could authentically align with each value.
                """
            )
            
            print("\nExtracting cultural values...")
            cultural_values = self.llm.invoke(
                values_prompt.format(
                    company_name=company_name,
                    communication_samples=formatted_samples
                )
            ).content
            
            # Generate final recommendations
            recommendations_prompt = PromptTemplate(
                input_variables=["company_name", "language_analysis", "decision_style", "cultural_values"],
                template="""
                Based on this cultural assessment of {company_name}:
                
                LANGUAGE ANALYSIS:
                {language_analysis}
                
                DECISION-MAKING STYLE:
                {decision_style}
                
                CULTURAL VALUES:
                {cultural_values}
                
                Provide specific recommendations for CU Hyperloop's communication approach:
                
                1. TONE AND FORMALITY: How should the email be written to match their style?
                2. CONTENT FOCUS: What should be emphasized or highlighted?
                3. PERSUASION APPROACH: What will be most convincing to them?
                4. SPECIFIC LANGUAGE: What terms or phrases should be used or avoided?
                5. VALUE ALIGNMENT: How should CU Hyperloop position itself to align with their values?
                
                Be specific and actionable with examples of language to use.
                """
            )
            
            print("\nGenerating communication recommendations...")
            recommendations = self.llm.invoke(
                recommendations_prompt.format(
                    company_name=company_name,
                    language_analysis=language_analysis,
                    decision_style=decision_style,
                    cultural_values=cultural_values
                )
            ).content
            
            # Compile the complete assessment
            cultural_assessment = {
                'language_analysis': language_analysis,
                'decision_style': decision_style,
                'cultural_values': cultural_values,
                'recommendations': recommendations
            }
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'assessment': cultural_assessment,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }, f)
                print(f"  ✓ Cultural assessment cached to {cache_file}")
            except Exception as e:
                print(f"  ❌ Error caching assessment: {str(e)}")
            
            return cultural_assessment
            
        except Exception as e:
            print(f"  ❌ Error assessing cultural compatibility: {str(e)}")
            # Create fallback assessment
            fallback_assessment = {
                'language_analysis': "Professional, industry-standard communication style",
                'decision_style': "Likely balances data-driven and relationship-based decision making",
                'cultural_values': "Innovation, excellence, quality, and professionalism are likely core values",
                'recommendations': "Maintain professional tone, emphasize technical capabilities, quantify benefits"
            }
            return fallback_assessment


class EmailGenerator:
    def __init__(self):
        # Initialize the language model
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.2
        )

        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GEMINI_API_KEY
        )

        # Initialize Google Search
        self.search = GoogleSearchAPIWrapper(
            google_api_key=GOOGLE_API_KEY,
            google_cse_id=GOOGLE_CSE_ID
        )
        
        # Initialize the relationship intelligence engine
        self.relationship_engine = RelationshipIntelligenceEngine(
            llm=self.llm,
            search=self.search
        )

    # Function to load and process documents for context
    def load_club_context(self, sponsorship_packet_path, fdp_path, email_template_path):
        """Load and process club-related documents for context."""
        log_section("LOADING CLUB CONTEXT")
        
        # First, verify all files exist with exact case sensitivity
        file_paths = {
            "Sponsorship Packet": sponsorship_packet_path,
            "Final Design Package": fdp_path,
            "Email Template": email_template_path
        }
        
        # Check if files exist and print actual file paths for debugging
        print("Checking file paths (case sensitive):")
        dir_files = os.listdir(os.getcwd())
        for name, path in file_paths.items():
            filename = os.path.basename(path)
            print(f"Looking for {name}: {filename}")
            
            # Check actual files in directory with their exact names
            matched_files = [f for f in dir_files if f.lower() == filename.lower()]
            if matched_files:
                print(f"  Found similar files: {matched_files}")
                # Use the actual filename with correct case
                corrected_path = os.path.join(os.path.dirname(path), matched_files[0])
                file_paths[name] = corrected_path
                print(f"  Using corrected path: {corrected_path}")
            
            if not os.path.exists(file_paths[name]):
                print(f"ERROR: {name} file not found at path: {file_paths[name]}")
                raise FileNotFoundError(f"File not found: {file_paths[name]}")
            else:
                print(f"  ✓ File exists: {file_paths[name]}")
        
        # Updated file paths
        sponsorship_packet_path = file_paths["Sponsorship Packet"]
        fdp_path = file_paths["Final Design Package"]
        email_template_path = file_paths["Email Template"]
        
        # Load documents
        log_section("LOADING DOCUMENTS")
        club_documents = []
        email_documents = []
        
        # Load sponsorship packet
        print(f"Loading sponsorship packet from: {sponsorship_packet_path}")
        if sponsorship_packet_path.endswith('.pdf'):
            loader = PyPDFLoader(sponsorship_packet_path)
            club_documents.extend(loader.load())
        else:
            loader = TextLoader(sponsorship_packet_path)
            club_documents.extend(loader.load())
        print(f"  ✓ Loaded {len(club_documents)} documents from sponsorship packet")
        
        # Load design package
        print(f"Loading design package from: {fdp_path}")
        if fdp_path.endswith('.pdf'):
            loader = PyPDFLoader(fdp_path)
            club_documents.extend(loader.load())
        else:
            loader = TextLoader(fdp_path)
            club_documents.extend(loader.load())
        print(f"  ✓ Loaded total of {len(club_documents)} documents from club materials")
        
        # Load email template - now expected to be a .txt file
        print(f"Loading email template from: {email_template_path}")
        # Since we expect a .txt file, we'll use TextLoader directly
        loader = TextLoader(email_template_path)
        email_documents.extend(loader.load())
        print(f"  ✓ Loaded {len(email_documents)} documents from email template")
        
        # Split documents into smaller chunks
        print("\nSplitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        # Add chunk size management based on available memory
        max_chunks = 100  # Adjust based on system capabilities
        
        club_splits = text_splitter.split_documents(club_documents)
        if len(club_splits) > max_chunks:
            print(f"Warning: Large document detected, limiting to {max_chunks} chunks")
            club_splits = club_splits[:max_chunks]
        
        email_splits = text_splitter.split_documents(email_documents)
        
        print(f"  ✓ Split club documents into {len(club_splits)} chunks")
        print(f"  ✓ Split email documents into {len(email_splits)} chunks")
        
        # Create vector store
        print("\nCreating vector stores...")
        club_vectorstore = Chroma.from_documents(
            documents=club_splits,
            embedding=self.embeddings
        )
        email_vectorstore = Chroma.from_documents(
            documents=email_splits,
            embedding=self.embeddings
        )
        print("  ✓ Vector stores created successfully")
        
        # Create retriever
        club_retriever = club_vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        email_retriever = email_vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        
        return club_retriever, email_retriever

    # Function to extract key information about the club
    def extract_club_info(self, club_retriever):
        """Extract key information about the club from documents."""
        log_section("EXTRACTING CLUB INFORMATION")
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=club_retriever
        )
        
        # Questions to ask about the club
        questions = [
            # fundamentals
            "What does CU Hyperloop do every single year and what do they compete in?",
            "How did CU Hyperloop evolve from focusing on Hyperloop transportation concepts to developing tunnel boring machines, and how has this shift affected their team identity?",
            "What is the mission and key goals of CU Hyperloop?",
            "What are the main achievements and history of the club?",
            "How are the roughly 50 team members organized into functional groups, and what is the workflow from initial concept to competition ready machine?",

            #culture?
            "What is the typical student experience like from joining CU Hyperloop as a new member to becoming a seasoned team contributor?",
            "How does the team recruit new members each year, and what qualities or skills do they look for in potential team members?",
            "What is the atmosphere like during the annual test dig events, and how does the team handle setbacks or technical failures?",
            "What traditions or team-building activities has CU Hyperloop developed that contribute to their team cohesion and culture?",

            #sponsorship
            "What sponsorship tiers does the club offer?",
            "What kind of recognition do sponsors receive?",
            "What specific real-world applications could this technology have beyond the competition, and how might it transform urban transportation?",
            "If there are 4 main things that the club can provide value with to a sponsor what are they and how do they provide value?",
            "What are the key benefits for sponsors to support CU Hyperloop, and how have past sponsors benefited from their involvement or been recognized?",

            #comp
            "What metrics are used to judge success in the Not-a-Boring Competition, and how has CU Hyperloop optimized their machine to excel in these areas?",
            "How does The Boring Company organize the Not-a-Boring Competition, and what is the complete competition experience like from arrival to the final event?",


            #technical
            "How (in detail) does the hexapod propulsion system work and why it did it earn an Innovation Award in 2024?",
            "How does the team's tunnel boring machine simultaneously handle excavation, propulsion, and tunnel reinforcement in a single integrated process?"
            "How does the 3D printing tunnel support system work in real-time, and what materials are used to ensure structural integrity?",
            "What is the complete autonomous control architecture that enabled their Accuracy Award in 2023, from sensors to decision-making algorithms?",

        ]
        
        club_info = {}
        for i, question in enumerate(questions):
            try:
                print(f"\nProcessing question {i+1}/{len(questions)}:")
                print(f"  {question}")
                
                # Start timing
                start_time = time.time()
                result = qa_chain.invoke({"query": question})
                end_time = time.time()
                
                # Get the answer
                answer = result["result"]
                
                # Print a preview of the answer
                preview = answer[:200] + "..." if len(answer) > 200 else answer
                print(f"  ✓ Answer received ({len(answer)} chars, {end_time - start_time:.2f}s):")
                print(f"  Preview: {preview}\n")
                
                # Store the result
                club_info[question] = answer
                
                # Add delay between API calls to avoid hitting rate limits
                delay = 3  # 3 seconds between calls
                print(f"  Waiting {delay}s before next question...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"  ❌ Error processing question: {question}")
                print(f"  Error details: {str(e)}")
                club_info[question] = f"Information unavailable due to API error: {str(e)}"
                
                # Wait longer after encountering an error
                recovery_delay = 10
                print(f"  Waiting {recovery_delay}s to recover from error...")
                time.sleep(recovery_delay)
        
        # Summary of information collected
        print("\nInformation collected:")
        for q, a in club_info.items():
            print(f"  • {q[:50]}... : {len(a)} chars")
            
        return club_info

    # Function to research company information with caching
    def research_company(self, company_name):
        """Research information about the target company with caching for efficiency."""
        log_section(f"RESEARCHING COMPANY: {company_name}")
        
        # Check for cached research
        cache_dir = os.path.join(os.getcwd(), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"company_{company_name.replace(' ', '_').lower()}.json")
        
        if os.path.exists(cache_file):
            try:
                print(f"Loading cached research for {company_name}")
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    print(f"  ✓ Found cached research from {cached_data.get('timestamp', 'unknown date')}")
                    return cached_data.get('company_info', '')
            except Exception as e:
                print(f"  ❌ Error loading cache: {str(e)}")
                print("  Proceeding with fresh research...")
        
        # Create search queries
        search_queries = [
            f"{company_name} about us",
            f"{company_name} sponsorships",
            f"{company_name} donations",
            f"{company_name} supports",
            f"{company_name} projects",
            f"{company_name} technology"
        ]
        
        # Collect search results
        search_results = []
        for i, query in enumerate(search_queries):
            try:
                print(f"\nSearch query {i+1}/{len(search_queries)}:")
                print(f"  {query}")
                
                start_time = time.time()
                results = self.search.results(query, num_results=3)
                end_time = time.time()
                
                print(f"  ✓ Got {len(results)} results ({end_time - start_time:.2f}s)")
                
                for j, result in enumerate(results):
                    search_results.append(f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}\n")
                    print(f"    Result {j+1}: {result['title'][:50]}...")
                
                # Add delay between searches
                delay = 2
                print(f"  Waiting {delay}s before next query...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"  ❌ Error searching for '{query}': {str(e)}")
                # Wait longer after error
                recovery_delay = 5
                print(f"  Waiting {recovery_delay}s to recover from error...")
                time.sleep(recovery_delay)
        
        # Compile company research
        print(f"\nCompiling research on {company_name} from {len(search_results)} search results...")
        
        company_research_prompt = PromptTemplate(
            input_variables=["search_results", "company_name"],
            template="""
            Based on these search results about {company_name}, extract key information that would be relevant for the CU Hyperloop club seeking sponsorship but also any key similarities that could be used to personalize/align the sponsorship request:
            
            {search_results}
            
            Please provide information about:
            1. Company's main products or services
            2. Company's core values and mission (what is it that they value? e.g. innovation, sustainability, american manufacturing, etc.)
            3. Any history of supporting educational, student club initiatives, or simply philanthropy of any kind
            4. Technical areas that might align with the CU Hyperloop project  - e.g. transportation, engineering, sustainability, etc. (could they benefit from a case study?)
            5. Any large recent acheivements or projects that could be highlighted our brought up in relatn to CU Hyperloop's project, acheievments, connections, etc.
            """
        )
        
        prompt = company_research_prompt.format(
            search_results="\n\n".join(search_results),
            company_name=company_name
        )
        
        try:
            print("Generating company profile...")
            start_time = time.time()
            company_info = self.llm.invoke(prompt).content
            end_time = time.time()
            
            # Print preview of the result
            preview = company_info[:200] + "..." if len(company_info) > 200 else company_info
            print(f"  ✓ Company profile generated ({len(company_info)} chars, {end_time - start_time:.2f}s)")
            print(f"  Preview: {preview}\n")
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'company_info': company_info,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'query_count': len(search_queries)
                    }, f)
                print(f"  ✓ Research cached to {cache_file}")
            except Exception as e:
                print(f"  ❌ Error caching research: {str(e)}")
            
            return company_info
            
        except Exception as e:
            error_msg = f"Error getting company info: {str(e)}"
            print(f"  ❌ {error_msg}")
            return f"Basic information about {company_name} (API error: {str(e)})"

    # Function to analyze templates
    def analyze_email_template(self, email_template_retriever):
        """Analyze the email template to understand context and requirements."""
        log_section("ANALYZING EMAIL TEMPLATE")
        
        # Create QA chain for email template
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=email_template_retriever
        )
        
        # Ask specific questions about the email template
        template_questions = [
            "What is the tone and style of the email template?",
            "What key components should be included in the email structure?",
            "What persuasive strategies are used in the template?"
        ]
        
        template_info = {}
        for i, question in enumerate(template_questions):
            try:
                print(f"\nEmail template question {i+1}/{len(template_questions)}:")
                print(f"  {question}")
                
                start_time = time.time()
                result = qa_chain.invoke({"query": question})
                end_time = time.time()
                
                answer = result["result"]
                preview = answer[:200] + "..." if len(answer) > 200 else answer
                print(f"  ✓ Answer received ({len(answer)} chars, {end_time - start_time:.2f}s)")
                print(f"  Preview: {preview}\n")
                
                template_info[question] = answer
                
                # Add delay between API calls
                delay = 2
                print(f"  Waiting {delay}s before next question...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"  ❌ Error analyzing email template with question: {question}")
                print(f"  Error details: {str(e)}")
                template_info[question] = f"Information unavailable due to API error: {str(e)}"
                
                # Wait longer after error
                recovery_delay = 5
                print(f"  Waiting {recovery_delay}s to recover from error...")
                time.sleep(recovery_delay)
        
        # Combine the template analysis
        email_analysis = "\n\n".join([f"{q}:\n{a}" for q, a in template_info.items()])
        print(f"\nEmail template analysis complete ({len(email_analysis)} chars)")
        
        return email_analysis
    
    # Function to generate tailored response
    def generate_response(self, club_info, email_analysis, company_info):
        """Generate a tailored sponsorship request email."""
        log_section("GENERATING RESPONSE EMAIL")
        
        # Format club info for better readability
        formatted_club_info = "\n\n".join([f"QUESTION: {q}\nANSWER: {a}" for q, a in club_info.items()])
        
        print(f"Club info: {len(formatted_club_info)} chars")
        print(f"Email analysis: {len(email_analysis)} chars")
        print(f"Company info: {len(company_info)} chars")
        
        response_prompt = PromptTemplate(
            input_variables=["email_analysis", "company_info", "club_info"],
            template="""
            Write a sponsorship request email for CU Hyperloop using the following information:
            
            EMAIL ANALYSIS:
            {email_analysis}
            
            COMPANY INFORMATION:
            {company_info}
            
            CLUB INFORMATION:
            {club_info}
            
            IMPORTANT: The email MUST begin with "My name is Matis, and I am the Business Development Lead for CU Hyperloop" - do not use any other name or role.
            
            Make it personalized, professional, focused on mutual benefits, and under 300 words.
            """
        )
        
        prompt = response_prompt.format(
            email_analysis=email_analysis,
            company_info=company_info,
            club_info=formatted_club_info,
        )
        
        try:
            print("\nCreating final email...")
            start_time = time.time()
            response_email = self.llm.invoke(prompt).content
            end_time = time.time()
            
            print(f"  ✓ Email generated successfully ({len(response_email)} chars, {end_time - start_time:.2f}s)")
            
            return response_email
            
        except Exception as e:
            error_msg = f"Error generating response email: {str(e)}"
            print(f"  ❌ {error_msg}")
            return f"Error generating email due to API limitations: {str(e)}"

    # NEW METHOD: Parse email templates
    def parse_email_templates(self, email_template_path):
        """Parse multiple email templates from a single file with improved structure recognition."""
        log_section("PARSING EMAIL TEMPLATES")
        
        # Load the template file
        with open(email_template_path, 'r') as file:
            content = file.read()
        
        # Split content into individual templates
        template_blocks = re.split(r'(?:TEMPLATE \d+|OTHER EXAMPLES)', content)
        template_blocks = [block.strip() for block in template_blocks if block.strip()]
        
        templates = []
        
        for block in template_blocks:
            template = {}
            
            # Extract title
            title_match = re.search(r'Title:\s*(.*?)(?:\n|$)', block)
            if title_match:
                template['title'] = title_match.group(1).strip()
            
            # Extract subject
            subject_match = re.search(r'Subject:\s*(.*?)(?:\n|$)', block)
            if subject_match:
                template['subject'] = subject_match.group(1).strip()
            
            # Extract body
            body_match = re.search(r'Body:\s*\n(.*?)(?=\n\n|$)', block, re.DOTALL)
            if body_match:
                # Clean up the body text
                body = body_match.group(1).strip()
                
                # Replace [NAME] and [ROLE] with Matis and Business Development Lead
                body = re.sub(r'\[NAME\]', 'Matis', body)
                body = re.sub(r'\[ROLE\]', 'Business Development Lead', body)
                
                template['body'] = body
                
                # Further analyze the body structure
                paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
                if paragraphs:
                    template['intro'] = paragraphs[0]
                    template['middle'] = paragraphs[1:-1] if len(paragraphs) > 2 else []
                    template['closing'] = paragraphs[-1] if len(paragraphs) > 1 else ""
                    
                    # Extract placeholders for personalization (excluding NAME and ROLE which we've fixed)
                    template['placeholders'] = [p for p in re.findall(r'\[(.*?)\]', body) if p != 'NAME' and p != 'ROLE']
            
            if template:
                templates.append(template)
                print(f"✓ Parsed template: {template.get('title', 'Unnamed')}")
                print(f"  - Subject: {template.get('subject', 'No subject')}")
                print(f"  - Placeholders: {template.get('placeholders', [])}")
                print(f"  - Paragraphs: {len(paragraphs) if 'intro' in template else 0}")
                print(f"  - Name and role fixed to: Matis, Business Development Lead")
        
        print(f"\nTotal templates parsed: {len(templates)}")
        return templates

    # NEW METHOD: Deep analysis of each template
    def analyze_templates(self, templates):
        """Analyze templates to understand their purpose, tone, and use cases."""
        log_section("ANALYZING TEMPLATES")
        
        template_analysis = []
        
        for i, template in enumerate(templates):
            print(f"\nAnalyzing template {i+1}: {template.get('title', 'Unnamed')}")
            
            analysis_prompt = PromptTemplate(
                input_variables=["template"],
                template="""
                Analyze this email template for sponsorship requests:
                
                TITLE: {template[title]}
                SUBJECT: {template[subject]}
                BODY:
                {template[body]}
                
                Please provide:
                1. Primary purpose (monetary donation, parts donation, service request, etc.)
                2. Target audience characteristics (industry type, company size, etc.)
                3. Key persuasion techniques used
                4. Tone analysis (formal, friendly, urgent, etc.)
                5. Structure breakdown (how information is organized)
                6. Strongest elements that should be preserved
                7. Elements that could be improved
                8. Keywords that signal when this template would be most appropriate
                
                Note: This template already uses the fixed introduction "My name is Matis, and I am the Business Development Lead for CU Hyperloop" which must be preserved in all emails.
                """
            )
            
            try:
                prompt = analysis_prompt.format(template=template)
                
                start_time = time.time()
                analysis_result = self.llm.invoke(prompt).content
                end_time = time.time()
                
                template['analysis'] = analysis_result
                template_analysis.append({
                    'template': template,
                    'analysis': analysis_result
                })
                
                print(f"  ✓ Analysis complete ({end_time - start_time:.2f}s)")
                preview = analysis_result[:150] + "..." if len(analysis_result) > 150 else analysis_result
                print(f"  Preview: {preview}")
                
            except Exception as e:
                print(f"  ❌ Error analyzing template: {str(e)}")
                template['analysis'] = f"Analysis failed: {str(e)}"
                template_analysis.append({
                    'template': template,
                    'analysis': f"Analysis failed: {str(e)}"
                })
            
            # Add delay between API calls
            time.sleep(2)
        
        return template_analysis

    # NEW METHOD: Enhanced template selection with relationship intelligence
    def select_best_template_with_relationship_data(self, templates_analysis, company_info, relationship_intelligence):
        """Select the most appropriate template based on company research and relationship intelligence."""
        log_section("SELECTING BEST TEMPLATE WITH RELATIONSHIP INTELLIGENCE")
        
        # Extract components of relationship intelligence
        decision_makers = relationship_intelligence.get('decision_makers', {})
        partnership_potential = relationship_intelligence.get('partnership_potential', {})
        cultural_assessment = relationship_intelligence.get('cultural_assessment', {})
        
        # Format decision maker information for the prompt
        formatted_decision_makers = "\n\n".join([
            f"CONTACT: {name}\nROLE: {profile.get('role', 'Unknown')}\nCOMMUNICATION STYLE: {profile.get('communication_style', 'Unknown')}"
            for name, profile in decision_makers.items()
        ])
        
        # Format partnership potential
        partnership_analysis = partnership_potential.get('partnership_analysis', '')
        value_propositions = partnership_potential.get('value_propositions', '')
        
        # Format cultural assessment
        decision_style = cultural_assessment.get('decision_style', '')
        recommendations = cultural_assessment.get('recommendations', '')
        
        selection_prompt = PromptTemplate(
            input_variables=["company_info", "templates_analysis", "decision_makers", 
                            "partnership_analysis", "value_propositions", 
                            "decision_style", "recommendations"],
            template="""
            Based on this comprehensive company intelligence:
            
            BASIC COMPANY INFO:
            {company_info}
            
            DECISION MAKERS:
            {decision_makers}
            
            PARTNERSHIP POTENTIAL:
            {partnership_analysis}
            
            VALUE PROPOSITIONS:
            {value_propositions}
            
            DECISION-MAKING STYLE:
            {decision_style}
            
            COMMUNICATION RECOMMENDATIONS:
            {recommendations}
            
            And these available email template analyses:
            
            {templates_analysis}
            
            Determine which template would be most effective for this company. Consider:
            
            1. Which template best matches the communication style of the decision makers?
            2. Which template structure would best support the specific value propositions identified?
            3. Which template aligns best with the company's decision-making style?
            4. Which template can be adapted to incorporate the cultural compatibility recommendations?
            
            First, rank the templates from most to least appropriate with clear reasoning based on the relationship intelligence.
            Then provide your final selection of the single best template, with a detailed explanation of why it's optimal given what we know about the specific people who will read it.
            
            Note: All templates use the fixed introduction "My name is Matis, and I am the Business Development Lead for CU Hyperloop" which must be maintained.
            """
        )
        
        # Format the templates analysis for the prompt
        formatted_analyses = "\n\n".join([
            f"TEMPLATE {i+1}: {ta['template'].get('title', 'Unnamed')}\n{ta['analysis']}"
            for i, ta in enumerate(templates_analysis)
        ])
        
        try:
            prompt = selection_prompt.format(
                company_info=company_info,
                templates_analysis=formatted_analyses,
                decision_makers=formatted_decision_makers,
                partnership_analysis=partnership_analysis,
                value_propositions=value_propositions,
                decision_style=decision_style,
                recommendations=recommendations
            )
            
            print("Determining best template match with relationship intelligence...")
            start_time = time.time()
            selection_result = self.llm.invoke(prompt).content
            end_time = time.time()
            
            print(f"  ✓ Relationship-informed template selection complete ({end_time - start_time:.2f}s)")
            
            # Extract the final selection
            # This is a simplified approach - could be enhanced with regex pattern matching
            selected_index = 0  # Default to first template
            for i, ta in enumerate(templates_analysis):
                title = ta['template'].get('title', '')
                if f"TEMPLATE {i+1}" in selection_result and title in selection_result:
                    if "best template" in selection_result.lower() and title.lower() in selection_result.lower():
                        selected_index = i
                        break
            
            selected_template = templates_analysis[selected_index]['template']
            print(f"  Selected template: {selected_template.get('title', 'Unnamed')}")
            
            return {
                'template': selected_template,
                'reasoning': selection_result
            }
            
        except Exception as e:
            print(f"  ❌ Error selecting template with relationship data: {str(e)}")
            # Fallback to first template if there's an error
            return {
                'template': templates_analysis[0]['template'],
                'reasoning': f"Default selection due to error: {str(e)}"
            }

    # NEW METHOD: Enhanced email generation with relationship intelligence
    def generate_relationship_informed_email(self, template_selection, club_info, company_info, relationship_intelligence):
            """Generate a tailored email using relationship intelligence."""
            log_section("GENERATING RELATIONSHIP-INFORMED EMAIL")
            
            selected_template = template_selection['template']
            selection_reasoning = template_selection['reasoning']
            
            # Extract components of relationship intelligence
            decision_makers = relationship_intelligence.get('decision_makers', {})
            partnership_potential = relationship_intelligence.get('partnership_potential', {})
            cultural_assessment = relationship_intelligence.get('cultural_assessment', {})
            
            # Identify primary recipient if possible
            primary_recipient = None
            if decision_makers:
                # Try to find a decision maker with highest authority
                for name, profile in decision_makers.items():
                    role = profile.get('role', '').lower()
                    if 'director' in role or 'manager' in role or 'head' in role:
                        primary_recipient = name
                        break
                
                # If no one with authority found, take the first one
                if not primary_recipient and len(decision_makers) > 0:
                    primary_recipient = list(decision_makers.keys())[0]
            
            # Get communication style if we have a primary recipient
            communication_style = ""
            if primary_recipient and primary_recipient in decision_makers:
                communication_style = decision_makers[primary_recipient].get('communication_style', '')
            
            # Get value propositions and recommendations
            value_propositions = partnership_potential.get('value_propositions', '')
            recommendations = cultural_assessment.get('recommendations', '')
            
            # Format club info for better readability
            formatted_club_info = "\n\n".join([f"QUESTION: {q}\nANSWER: {a}" for q, a in club_info.items()])
            
            generation_prompt = PromptTemplate(
                input_variables=["template", "selection_reasoning", "company_info", "club_info", 
                            "primary_recipient", "communication_style", 
                            "value_propositions", "recommendations"],
                template="""
                Create a highly personalized sponsorship email for CU Hyperloop using this selected template
                and comprehensive relationship intelligence:
                
                TEMPLATE TITLE: {template[title]}
                TEMPLATE SUBJECT: {template[subject]}
                TEMPLATE BODY:
                {template[body]}
                
                TEMPLATE SELECTION REASONING:
                {selection_reasoning}
                
                COMPANY INFORMATION:
                {company_info}
                
                INTENDED PRIMARY RECIPIENT:
                {primary_recipient}
                
                RECIPIENT'S COMMUNICATION STYLE:
                {communication_style}
                
                UNIQUE VALUE PROPOSITIONS FOR THIS COMPANY:
                {value_propositions}
                
                CULTURAL COMPATIBILITY RECOMMENDATIONS:
                {recommendations}
                
                CLUB INFORMATION:
                {club_info}
                
                Instructions:
                1. CRITICAL: The email MUST begin with "Hello [company name]," followed by a line break, and THEN "My name is Matis, and I am the Business Development Lead for CU Hyperloop" - do not use any other name or role
                2. Keep the partnership value propositions realistic and based on CU Hyperloop's EXISTING capabilities - DO NOT propose elaborate new programs or initiatives like custom challenges or research programs
                3. Focus on established, proven benefits like: brand visibility at competitions, access to engineering talent, case studies of technology, sponsorship logo placement
                4. Match the communication style of the recipient using the provided recommendations
                5. Reference any personal or professional connections the recipient might have to engineering, education, or student initiatives
                6. Use language, tone, and structure that aligns with the company's cultural preferences
                7. Make the call to action clear and specific, tailored to the recipient's decision-making style
                8. Keep the email under 300 words while preserving all key persuasive elements
                
                Return the email in this format:
                SUBJECT: [personalized subject line]
                
                [complete email body]
                """
            )
            
            try:
                prompt = generation_prompt.format(
                    template=selected_template,
                    selection_reasoning=selection_reasoning,
                    company_info=company_info,
                    club_info=formatted_club_info,
                    primary_recipient=primary_recipient or "Unknown - use generic greeting",
                    communication_style=communication_style or "Use professional, clear communication",
                    value_propositions=value_propositions,
                    recommendations=recommendations
                )
                
                print("Generating relationship-informed email...")
                start_time = time.time()
                generated_email = self.llm.invoke(prompt).content
                end_time = time.time()
                
                print(f"  ✓ Relationship-informed email generated successfully ({len(generated_email)} chars, {end_time - start_time:.2f}s)")
                
                # Verify the email starts with the required intro and fix if needed
                if not generated_email.find("My name is Matis, and I am the Business Development Lead for CU Hyperloop") > -1:
                    print("  ⚠️ Fixing email to ensure correct introduction")
                    
                    # Extract subject line if present
                    subject_match = re.search(r'^SUBJECT:\s*(.*?)$', generated_email, re.MULTILINE)
                    subject = subject_match.group(1).strip() if subject_match else "Partnership with CU Hyperloop"
                    
                    # Get the body content after the SUBJECT line
                    body_content = re.sub(r'^SUBJECT:\s*.*?$\n+', '', generated_email, 1, re.MULTILINE).strip()
                    
                    # Replace any introduction sentence with our fixed intro
                    body_lines = body_content.split('\n')
                    first_paragraph = body_lines[0]
                    
                    # Check if it has greeting with company name
                    greeting_match = re.search(r'^(Hi|Hello)\s+[\w\s\[\]]+,', first_paragraph)
                    if greeting_match:
                        # Keep the greeting but replace the rest of the paragraph
                        greeting = greeting_match.group(0)
                        body_lines[0] = f"{greeting}\n\nMy name is Matis, and I am the Business Development Lead for CU Hyperloop, a dynamic student team at the University of Colorado Boulder that every year designs and builds an innovative tunnel boring machine. Last year, our 12-ft long, 2000lb TBM earned us 2nd place in the world at the Boring Company's Not-A-Boring Competition, and we're poised to push even further this year."
                    else:
                        # Add generic greeting with company name placeholder and our intro
                        body_lines[0] = f"Hello [company name],\n\nMy name is Matis, and I am the Business Development Lead for CU Hyperloop, a dynamic student team at the University of Colorado Boulder that every year designs and builds an innovative tunnel boring machine. Last year, our 12-ft long, 2000lb TBM earned us 2nd place in the world at the Boring Company's Not-A-Boring Competition, and we're poised to push even further this year."
                    
                    # Reconstruct the email
                    fixed_email = f"SUBJECT: {subject}\n\n{'\n'.join(body_lines)}"
                    generated_email = fixed_email
                
                return generated_email
                
            except Exception as e:
                error_msg = f"Error generating relationship-informed email: {str(e)}"
                print(f"  ❌ {error_msg}")
                
                # Fallback to a simplified email
                return f"""
                SUBJECT: Partnership Opportunity with CU Hyperloop
                
                Hello [company name],
                
                My name is Matis, and I am the Business Development Lead for CU Hyperloop, a dynamic student team at the University of Colorado Boulder that designs and builds innovative tunnel boring machines. We placed 2nd worldwide at the Boring Company's competition last year.
                
                We believe there could be a valuable partnership opportunity between our organizations and would appreciate the chance to discuss this further. As a sponsor, your company would receive logo placement on our machine and materials, recognition at competitions, and access to talented engineering students.
                
                Could we schedule a brief call this week?
                
                Thank you,
                Matis
                CU Hyperloop Team
                
                [Note: This is a simplified fallback email due to an error in generation: {str(e)}]
                """
                
    # NEW METHOD: Enhanced workflow that incorporates relationship intelligence
    def relationship_intelligence_workflow(self, company_name, sponsorship_packet_path, fdp_path, email_template_path):
        """A comprehensive workflow that incorporates relationship intelligence for deeper personalization."""
        try:
            log_section("STARTING RELATIONSHIP INTELLIGENCE WORKFLOW")
            
            # Steps 1-2: Load club context and extract info (same as existing code)
            print("\nStep 1: Loading club context")
            club_retriever, _ = self.load_club_context(
                sponsorship_packet_path=sponsorship_packet_path,
                fdp_path=fdp_path,
                email_template_path=email_template_path
            )
            
            print("\nStep 2: Extracting club information")
            club_info = self.extract_club_info(club_retriever=club_retriever)
            
            # Step 3: Parse and analyze email templates (same as enhanced workflow)
            print("\nStep 3: Parsing email templates")
            templates = self.parse_email_templates(email_template_path)
            
            print("\nStep 4: Analyzing email templates")
            templates_analysis = self.analyze_templates(templates)
            
            # Step 5: Basic company research (same as existing code)
            print("\nStep 5: Researching company")
            company_info = self.research_company(company_name=company_name)
            
            # NEW STEP 6: Relationship Intelligence Analysis
            log_section("RELATIONSHIP INTELLIGENCE ANALYSIS")
            
            # Profile decision makers
            print("\nStep 6a: Profiling decision makers")
            decision_makers = self.relationship_engine.profile_decision_makers(company_name)
            
            # Analyze strategic partnership potential
            print("\nStep 6b: Analyzing strategic partnership potential")
            partnership_analysis = self.relationship_engine.analyze_strategic_partnership_potential(
                company_name, club_info
            )
            
            # Assess cultural compatibility
            print("\nStep 6c: Assessing cultural compatibility")
            cultural_assessment = self.relationship_engine.assess_cultural_compatibility(company_name)
            
            # Combine all relationship intelligence
            relationship_intelligence = {
                'decision_makers': decision_makers,
                'partnership_potential': partnership_analysis,
                'cultural_assessment': cultural_assessment
            }
            
            # Step 7: Select best template with relationship intelligence
            print("\nStep 7: Selecting best template with relationship intelligence")
            template_selection = self.select_best_template_with_relationship_data(
                templates_analysis, 
                company_info,
                relationship_intelligence
            )
            
            # Step 8: Generate tailored email using relationship intelligence
            print("\nStep 8: Generating relationship-informed email")
            response_email = self.generate_relationship_informed_email(
                template_selection, 
                club_info, 
                company_info,
                relationship_intelligence
            )
            
            log_section("RELATIONSHIP INTELLIGENCE WORKFLOW COMPLETED SUCCESSFULLY")
            return response_email
            
        except Exception as e:
            error_msg = f"Error in relationship intelligence workflow: {str(e)}"
            print(f"\n❌ {error_msg}")
            return f"An error occurred during the relationship-enhanced email generation process: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    # List files in the current directory to help diagnose path issues
    print("Files in current directory:")
    for file in os.listdir(current_dir):
        print(f"  - {file}")
    
    # Company to research
    COMPANY_NAME = "hydro engineering consultant"
    
    # Use os.path.join to create proper paths
    # Note: We're being case-insensitive with these initial paths
    # The actual file case will be detected in the load_club_context function
    SPONSORSHIP_PACKET_PATH = os.path.join(current_dir, "sponsorShipPacket.pdf")
    FDP_PATH = os.path.join(current_dir, "fdp.pdf")  
    EMAIL_TEMPLATE_PATH = os.path.join(current_dir, "emailTemplates.txt")  # Changed from .pdf to .txt
    
    # Print the initial paths
    print(f"Initial sponsorship packet path: {SPONSORSHIP_PACKET_PATH}")
    print(f"Initial FDP path: {FDP_PATH}")
    print(f"Initial email template path: {EMAIL_TEMPLATE_PATH}")
    
    # Initialize the email generator
    email = EmailGenerator()
    
    # Use the relationship intelligence workflow
    print("\nUsing relationship intelligence workflow...")
    response = email.relationship_intelligence_workflow(
        company_name=COMPANY_NAME,
        sponsorship_packet_path=SPONSORSHIP_PACKET_PATH,
        fdp_path=FDP_PATH,
        email_template_path=EMAIL_TEMPLATE_PATH
    )
    
    # Print the final response
    print("\nGENERATED RESPONSE EMAIL:")
    print("--------------------------")
    print(response)