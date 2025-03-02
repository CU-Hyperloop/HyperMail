from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Company, Template, Email, Prompt
from .serializers import *
import os

from .services.generateEmails import GenerateEmails
from rest_framework.permissions import AllowAny
from django.conf import settings
import traceback

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
                            email=company_data.get('email', ''),
                            website=company_data.get('website', ''),
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



