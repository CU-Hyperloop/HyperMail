import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")

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

    # Function to load and process documents for context
    def load_club_context(self, sponsorship_packet_path, fdp_path, email_template_path):
        """Load and process club-related documents for context."""
        print("Loading club context documents...")
        
        # Load documents
        club_documents = []
        email_documents = []
        
        # Load sponsorship packet
        if sponsorship_packet_path.endswith('.pdf'):
            loader = PyPDFLoader(sponsorship_packet_path)
            club_documents.extend(loader.load())
        else:
            loader = TextLoader(sponsorship_packet_path)
            club_documents.extend(loader.load())
        
        # Load design package (might be large)
        if fdp_path.endswith('.pdf'):
            loader = PyPDFLoader(fdp_path)
            club_documents.extend(loader.load())
        else:
            loader = TextLoader(fdp_path)
            club_documents.extend(loader.load())
        
        # Load email template (might be large)
        if email_template_path.endswith('.pdf'):
            loader = PyPDFLoader(email_template_path)
            email_documents.extend(loader.load())
        else:
            loader = TextLoader(email_template_path)
            email_documents.extend(loader.load())
        
        # Split documents into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        club_splits = text_splitter.split_documents(club_documents)
        email_splits = text_splitter.split_documents(club_documents)
        
        # Create vector store
        club_vectorstore = Chroma.from_documents(
            documents=club_splits,
            embedding=self.embeddings
        )
        email_vectorstore = Chroma.from_documents(
            documents=email_splits,
            embedding=self.embeddings
        )
        
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
        print("Extracting club information...")
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=club_retriever
        )
        
        # Ask specific questions about the club
        questions = [
            "What is the name and mission of CU Hyperloop?",
            "What are the main achievements and projects of the club?",
            "What sponsorship tiers or options does the club offer?",
            "What kind of recognition do sponsors receive?",
            "What are the key technical specifications of the Tunnel Boring Machine?"
        ]
        
        club_info = {}
        for question in questions:
            result = qa_chain.invoke({"query": question})
            club_info[question] = result["result"]
        
        return club_info

    #Function to research company information
    def research_company(self, company_name):
        """Research information about the target company."""
        print(f"Researching information about {company_name}...")
        
        # Create search queries
        search_queries = [
            f"{company_name} about us",
            f"{company_name} corporate social responsibility",
            f"{company_name} sponsorships",
            f"{company_name} technology focus",
            f"{company_name} recent news"
        ]
        
        # Collect search results
        search_results = []
        for query in search_queries:
            results = self.search.results(query, num_results=2)
            for result in results:
                search_results.append(f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}\n")
        
        # Compile company research
        company_research_prompt = PromptTemplate(
            input_variables=["search_results", "company_name"],
            template="""
            Based on these search results about {company_name}, extract key information that would be relevant for the CU Hyperloop club seeking sponsorship:
            
            {search_results}
            
            Please provide information about:
            1. Company's main products or services
            2. Company's values and mission
            3. Any history of supporting educational or student club initiatives
            4. Technical areas that might align with the CU Hyperloop project
            5. Key decision makers for sponsorships if available
            """
        )
        
        prompt = company_research_prompt.format(
            search_results="\n\n".join(search_results),
            company_name=company_name
        )
        
        company_info = self.llm.invoke(prompt).content
        return company_info

    #Function to analyze received email
    def analyze_email_template(self, email_template_retriever):
        """Analyze the email template to understand context and requirements."""
        print("Analyzing email template...")
        
        email_analysis_prompt = PromptTemplate(
            input_variables=["email_template"],
            template="""
            Analyze each one of the email templates given below:
            
            {email_template}
            
            Please extract:
            1. The style of the email template
            2. All the important points we mention in a normal email to sponsors
            3. Determine what is the persuasive parts of the email
            4. Extract the different strategies we use to persaude sponsors

            Given all the things you have learned return a summary of what you have learned from each email template make a final email template and return it
            """
        )
        
        prompt = email_analysis_prompt.format(email_template=email_template_retriever)
        analysis = self.llm.invoke(prompt).content
        
        return analysis
    
    # Function to generate tailored response
    def generate_response(self, club_info, email_analysis, company_info):
        """Generate a tailored sponsorship request email."""
        print("Generating response email...")
        
        response_prompt = PromptTemplate(
            input_variables=["email_analysis", "company_info", "club_info"],
            template="""
            You are tasked with writing a sponsorship request email for a CU Hyperloop. Use the following information:
            
            EMAIL ANALYSIS:
            {email_analysis}
            
            COMPANY INFORMATION:
            {company_info}
            
            CLUB INFORMATION:
            {club_info}
            
            Create a personalized email that:
            1. Follows the general structure of the email template
            2. Addresses the specific person and company by name
            3. Makes connections between the club's projects and the company's interests/values
            4. Highlights specific sponsorship opportunities that would benefit this company
            5. References something specific about the company to show research was done
            6. Maintains a professional but enthusiastic tone
            7. Includes specific details about the robot that would interest this particular company
            8. Is concise and is no longer that 300 words
            9. Make sure there is no text within a [] that represents a fill in section. You should fill these sections in
            
            Write the complete email ready to send.
            """
        )
        
        prompt = response_prompt.format(
            email_analysis=email_analysis,
            company_info=company_info,
            club_info="\n\n".join([f"{q}:\n{a}" for q, a in club_info.items()]),
        )
        
        response_email = self.llm.invoke(prompt).content
        return response_email

    # Main workflow function
    def sponsorship_email_workflow(self, company_name, sponsorship_packet_path, fdp_path, email_template_path):
        """
        Complete workflow for processing incoming emails and generating sponsorship requests.
        
        Args:
            company_name: name of the company the email is going to
            sponsorship_packet_path: Path to the sponsorship packet PDF or text file
            fdp_path: Path to the final design package PDF or text file
            email_template_path: Path to the email template text file
        
        Returns:
            Generated response email
        """
        # Step 1: Load club context
        club_retriever, email_template_retriever = self.load_club_context(
            sponsorship_packet_path=sponsorship_packet_path,
            fdp_path=fdp_path,
            email_template_path=email_template_path
        )
        
        # Step 2: Extract club information
        club_info = self.extract_club_info(club_retriever=club_retriever)
        
        # Step 3: Analyze email template
        email_analysis = self.analyze_email_template(email_template_retriever=email_template_retriever)
        
        # Step 4: Research company
        company_info = self.research_company(company_name=company_name)
        
        # Step 5: Generate response
        response_email = self.generate_response(club_info=club_info, email_analysis=email_analysis, company_info=company_info)
        
        return response_email

# Example usage
if __name__ == "__main__":
    # Paths to your documents
    COMPANY_NAME="hydro engineering consultant"
    SPONSORSHIP_PACKET_PATH = "./sponsorShipPacket.pdf"
    FDP_PATH = "./fdp.pdf"
    EMAIL_TEMPLATE_PATH = "./emailTemplates.pdf"

    email = EmailGenerator()
    
    # Generate response
    response = email.sponsorship_email_workflow(
        company_name=COMPANY_NAME,
        sponsorship_packet_path=SPONSORSHIP_PACKET_PATH,
        fdp_path=FDP_PATH,
        email_template_path=EMAIL_TEMPLATE_PATH
    )
    
    print("\nGENERATED RESPONSE EMAIL:")
    print("--------------------------")
    print(response)