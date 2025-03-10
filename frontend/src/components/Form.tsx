import { useState, useEffect } from 'react';
import { Button, Code, Text, TextInput, Textarea, Autocomplete, Alert, Box, Loader } from '@mantine/core';
import { hasLength, useForm } from '@mantine/form';
import {industries, companySizes, emailVibes} from '../data/formData';
import getCompanies from '../api';
import { useNavigate } from 'react-router';

export default function Form() {

    const navigate = useNavigate();

    const [loading, setLoading] = useState(false);
    const [apiResponse, setApiResponse] = useState<any>(null);
    const [companies, setCompanies] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    
    const form = useForm({
        mode: 'controlled',
        initialValues: { 
          industry: '', 
          size: '', 
          sector:'', 
          location: '', 
          vibe:'',
          details: '',
        },
        validate: {
          industry: hasLength({ min: 2 }, 'Industry is required'),
        },
    });
    
    const handleSubmit = async (values: typeof form.values) => {
      setLoading(true);
      setError(null);
      setApiResponse(null);

      const data = {
        industry: values.industry,
        size: values.size,
        sector: values.sector,
        location: values.location,
        vibe: values.vibe,
        details: values.details
      }
      
      try {
        const response = await getCompanies(data);
        console.log('API response:', response.companies);
        setCompanies(response.companies); 
    } catch (err: any) {
        setError(err.message || 'An error occurred while calling the OpenAI API');
    } finally {
        setLoading(false);
    }
};

    useEffect(() => {
        if (companies !== null) {
            console.log('Navigating with companies:', companies);
            navigate('/dashboard', { state: { data: companies } });
        }
    }, [companies, navigate]);
    
    return (
      <>
        {error && (
          <Alert color="red" title="Error" mb="md" withCloseButton onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        <form
        onSubmit={(event) => {
            event.preventDefault();
            handleSubmit(form.values);
        }}  
        >
            <Autocomplete {...form.getInputProps('industry')} data={industries} label="Industry" placeholder="Name" required mt="md" />
            <Autocomplete {...form.getInputProps('size')} data={companySizes} mt="md" label="Size" placeholder="Size" />
            <TextInput {...form.getInputProps('sector')} mt="md" label="Sector" placeholder="Sector" />
            <TextInput {...form.getInputProps('location')} mt="md" label="Location" placeholder="Location" />
            <Autocomplete {...form.getInputProps('vibe')} data={emailVibes} mt="md" label="Email Vibe" placeholder="Vibe" />
            <Textarea {...form.getInputProps('details')} mt="md" label="Customize" placeholder="Customize your email..." />
            
            <Button type="submit" mt="md" loading={loading} fullWidth>
                {loading ? 'Searching...' : 'Submit'}
            </Button>
        
            {loading && (
              <Box ta="center" mt="xl">
                <Loader size="md" />
                <Text mt="sm">Calling Gemini API...</Text>
              </Box>
            )}
            
            {apiResponse && (
              <Box mt="xl">
                <Text fw={700} size="lg">OpenAI API Response:</Text>
                <Code block mt="md" style={{ whiteSpace: 'pre-wrap', textAlign: 'left' }}>
                  {companies}
                </Code>
              </Box>
            )}
            
            {/* <Text mt="md">Form values:</Text>
            <Code block>{JSON.stringify(form.values, null, 2)}</Code> */}
        </form>
      </>
    );
}