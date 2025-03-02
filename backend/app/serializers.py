from rest_framework import serializers
from .models import Company, Template, Email, Prompt

# Basic Serializers

class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for the Company model.
    Converts Company model instances to/from JSON.
    """
    class Meta:
        model = Company
        fields = "__all__" 
        read_only_fields = ['id', 'added_at']
    
    def validate(self, data):
        """
        Validate that email or website is provided
         mirrors the model validation but necessary for API layer
        """
        if not data.get('email') and not data.get('website'):
            raise serializers.ValidationError("Either email or website must be provided.")
        return data


class TemplateSerializer(serializers.ModelSerializer):
    """
    Converts Template model instances to/from JSON
    """
    class Meta:
        model = Template
        fields = "__all__" 
        read_only_fields = ['id', 'created_at']


class EmailSerializer(serializers.ModelSerializer):
    """
    Includes company_name and template_subject for convenience in list views
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    template_subject = serializers.CharField(source='template.subject', read_only=True, required=False)
    
    class Meta:
        model = Email
        fields = "__all__" 
        read_only_fields = ['id', 'sent_at']

class PromptSerializer(serializers.ModelSerializer):
    """
    Serializer for the Prompt model.
    Converts Prompt model instances to/from JSON.
    """
    class Meta:
        model = Prompt
        fields = "__all__" 
        read_only_fields = ['id', 'created_at']


# Detailed Serializers with Nested Relationships

class EmailDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Email model that includes full company and template data.
    Useful for retrieving a single email with all related information.
    """
    company = CompanySerializer(read_only=True)
    template = TemplateSerializer(read_only=True)
    
    class Meta:
        model = Email
        fields = "__all__" 
        read_only_fields = ['id', 'sent_at']
    
    def create(self, validated_data):
        """
        Override create method to handle the nested objects when creating a new email.
        For create operations, use company_id and template_id instead of nested objects.
        """
        company_id = self.context['request'].data.get('company_id')
        template_id = self.context['request'].data.get('template_id')
        
        if not company_id:
            raise serializers.ValidationError({'company_id': 'This field is required.'})
            
        validated_data['company_id'] = company_id
        
        if template_id:
            validated_data['template_id'] = template_id
            
        return super().create(validated_data)


class CompanyDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Company model that includes related emails.
    Useful for retrieving a company and seeing all emails sent to them.
    """
    emails = EmailSerializer(many=True, read_only=True)
    emails_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = "__all__" 
        read_only_fields = ['id', 'added_at', 'emails_count']
    
    def get_emails_count(self, obj):
        """
        Return the count of emails sent to this company.
        """
        return obj.emails.count()


class TemplateDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Template model that includes all emails using this template
    Useful for tracking template usage.
    """
    emails = EmailSerializer(many=True, read_only=True)
    emails_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = "__all__" 
        read_only_fields = ['id', 'created_at', 'emails_count']
    
    def get_emails_count(self, obj):
        """
        Return the count of emails using this template
        """
        return obj.emails.count()