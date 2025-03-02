from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import os

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Company, Template, Email, Prompt
from .serializers import *
from .test2 import EmailGenerator 

import os

from .services.generateEmails import GenerateEmails
from rest_framework.permissions import AllowAny
from django.conf import settings
import traceback

#email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailGeneratorViewSet(viewsets.ViewSet):
    """
    ViewSet for generating sponsorship emails using Gemini AI.
    """
    permission_classes = [AllowAny]  # Adjust according to your security needs

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure environment variables are set
        if not hasattr(settings, 'GEMINI_API_KEY'):
            os.environ['GEMINI_API_KEY'] = settings.GEMINI_API_KEY
        if not hasattr(settings, 'GEMINI_MODEL'):
            os.environ['GEMINI_MODEL'] = settings.GEMINI_MODEL
        if not hasattr(settings, 'GOOGLE_API_KEY'):
            os.environ['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
        if not hasattr(settings, 'GOOGLE_CSE_ID'):
            os.environ['GOOGLE_CSE_ID'] = settings.GOOGLE_CSE_ID
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate unique company suggestions based on criteria and save to database.
        """
        try:
            # Extract parameters from request data
            params = {
                'industry': request.data.get('industry', ''),
                'size': request.data.get('size', ''),
                'sector': request.data.get('sector', ''),
                'location': request.data.get('location', ''),
                'vibe': request.data.get('vibe', ''),
                'details': request.data.get('details', '')
            }
            
            # Initialize email generator
            email_generator = GenerateEmails()
            
            # Generate companies
            results = email_generator.generateEmails(params)
            
            # Save companies to database
            saved_companies = []
            for company_data in results["companies"]:
                # Check if company already exists
                if not Company.objects.filter(name=company_data.get('name')).exists():
                    try:
                        # Determine company type
                        company_type = 'monetary'  # Default
                        if 'type' in params and params['type'] in ['monetary', 'parts']:
                            company_type = params['type']
                        
                        # Create new company
                        new_company = Company(
                            name=company_data.get('name', ''),
                            website=company_data.get('website', ''),
                            email=company_data.get('email', ''),
                            description=company_data.get('description', ''),
                            contact_person=company_data.get('contact_person', ''),
                            industry=company_data.get('industry', params.get('industry', '')),
                            location=company_data.get('location', params.get('location', '')),
                            size=company_data.get('size', params.get('size', '')),
                            type=company_type
                        )

                        new_company.save()
                        saved_companies.append(company_data.get('name'))
                    except Exception as e:
                        print(f"Error saving company {company_data.get('name')}: {e}")
            
            # Add information about which companies were saved to the database
            results["saved_to_database"] = saved_companies
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def send_email(self,request):
    
        # Fetching parameters from the request
        to_email = request.data.get('to_email', '')
        subject = request.data.get('subject', '')
        message = request.data.get('message', '')
        cc_email = request.data.get('cc_email', '')  # Optional CC email

        # Check for missing required fields
        if not to_email or not subject or not message:
            return {
                'status': 'error',
                'message': 'Missing required fields: to_email, subject, message'
            }

        # Email configuration
        sender_email = "cuhyperloop@colorado.edu"  # Replace with your email
        sender_password = "obmq rbnx ncvx kmop"  # Replace with your app password
        
        # Create the MIME object
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add CC email if provided
        if cc_email:
            msg['Cc'] = cc_email
        
        # Attach the message to the email as HTML
        msg.attach(MIMEText(message, 'html'))
        
        # Collect all recipients (to + cc) for the actual send operation
        recipients = [to_email]
        if cc_email:
            recipients.append(cc_email)

        # Connect to the SMTP server (Gmail in this case)
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipients, msg.as_string())

            print(f"Email sent to: {to_email} (CC: {cc_email})") 

            return {
                'status': 'success',
                'message': 'Email sent successfully'
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Failed to send email: {str(e)}"
            }


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Company data.
    
    list:
        Get all companies
    retrieve:
        Get a single company with all emails sent
    emails:
        Get all emails for a specific company
    """
    queryset = Company.objects.all().order_by('-added_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'website', 'industry', 'location']
    ordering_fields = ['name', 'added_at', 'type']
    
    def get_serializer_class(self):
        """Return different serializers for list vs detail views"""
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanySerializer
    
    @action(detail=True, methods=['get'])
    def emails(self, request, pk=None):
        """Get all emails for a specific company"""
        company = self.get_object()
        emails = Email.objects.filter(company=company)
        serializer = EmailSerializer(emails, many=True)
        return Response(serializer.data)


class TemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing email templates.
    
    list:
        Get all templates
    retrieve:
        Get a single template with all emails using it
    """
    queryset = Template.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'body']
    ordering_fields = ['created_at', 'type']
    
    def get_serializer_class(self):
        """Return different serializers for list vs detail views"""
        if self.action == 'retrieve':
            return TemplateDetailSerializer
        return TemplateSerializer


class EmailViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing emails.
    
    list:
        Get all emails
    retrieve:
        Get a single email with all details
    """
    queryset = Email.objects.all().order_by('-sent_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'body']
    ordering_fields = ['sent_at', 'status', 'type']
    
    def get_serializer_class(self):
        """Return different serializers for list vs detail views"""
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return EmailDetailSerializer
        return EmailSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new email.
        If a template_id is provided, copy its subject and body.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # If template_id is provided, get template data
        template_id = request.data.get('template_id')
        if template_id:
            template = get_object_or_404(Template, id=template_id)
            # Only copy subject and body if not provided in request
            if 'subject' not in request.data:
                serializer.validated_data['subject'] = template.subject
            if 'body' not in request.data:
                serializer.validated_data['body'] = template.body
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PromptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing prompts.
    
    list:
        Get all prompts
    retrieve:
        Get a single prompt
    """
    queryset = Prompt.objects.all().order_by('-created_at')
    serializer_class = PromptSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text', 'link']
    ordering_fields = ['created_at', 'type']

    @action(detail=False, methods=['post'])
    def generate_email(self, request):
        """
        API endpoint to generate an email based on company name and other parameters.
        """
        try:
            # Get company name from request data
            print(f"Received request: {request.data}")
            company_name = request.data.get('company_name')
            company_name = "hydro engineering consultant"
            if not company_name:
                return Response(
                    {"error": "Company name is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            print("generating info for company");            
            # Set paths to your files 
            SPONSORSHIP_PACKET_PATH = "./data/sponsorShipPacket.pdf"
            FDP_PATH = "./data/fdp.pdf"
            # EMAIL_TEMPLATE_PATH = "./data/emailTemplates.pdf"
            EMAIL_TEMPLATE_PATH = "./data/emailTemplates.txt"

            import os
            # Check if files exist
            print(f"Sponsorship packet exists: {os.path.exists(SPONSORSHIP_PACKET_PATH)}")
            print(f"FDP exists: {os.path.exists(FDP_PATH)}")
            print(f"Email template exists: {os.path.exists(EMAIL_TEMPLATE_PATH)}")
           
            # Initialize the email generator
            try:
                email_generator = EmailGenerator()
                print("Successfully created EmailGenerator instance")
            except Exception as e:
                error_msg = f"Failed to initialize EmailGenerator: {str(e)}"
                print(f"Error: {error_msg}")
                return Response(
                    {"error": error_msg}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            # Generate the email
            # response_email = email_generator.sponsorship_email_workflow(
            #     company_name=company_name,
            #     sponsorship_packet_path=SPONSORSHIP_PACKET_PATH,
            #     fdp_path=FDP_PATH,
            #     email_template_path=EMAIL_TEMPLATE_PATH
            # )

            response_email = email_generator.relationship_intelligence_workflow(
                company_name=company_name,
                sponsorship_packet_path=SPONSORSHIP_PACKET_PATH,
                fdp_path=FDP_PATH,
                email_template_path=EMAIL_TEMPLATE_PATH
            )
            
            # Return the generated email
            return Response({"email": response_email}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


