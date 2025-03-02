import { useState } from 'react';
import { Button, Code, Text, TextInput, Textarea, Autocomplete } from '@mantine/core';
import { hasLength, isEmail, useForm } from '@mantine/form';

import { useNavigate } from 'react-router';

export default function Form() {

    const navigate = useNavigate();

    const handleSubmit = (values: any) => {
        console.log(values);

        // call api here

        navigate('/draft');
    }

    const form = useForm({
        mode: 'controlled',
        initialValues: { industry: '', size: '', sector:'', location: '', vibe:''},
        validate: {
        //   name: hasLength({ min: 3 }, 'Must be at least 3 characters'),
        //   email: isEmail('Invalid email'),
        },
      });
    
      const [submittedValues, setSubmittedValues] = useState<typeof form.values | null>(null);
    
      return (
        <form onSubmit={form.onSubmit(setSubmittedValues)}>
            <Autocomplete {...form.getInputProps('industry')}  data= {industries} label="Industry" placeholder="Name" />
            <Autocomplete {...form.getInputProps('size')}  data = {companySizes} mt="md" label="Size" placeholder="Size" />
            <TextInput {...form.getInputProps('sector')} mt="md" label="Sector" placeholder="Sector" />
            <TextInput {...form.getInputProps('location')} mt="md" label="Location" placeholder="Location" />
            <Autocomplete {...form.getInputProps('vibe')} data = {emailVibes} mt="md" label="Email Vibe" placeholder="Vibe" />
            <Textarea {...form.getInputProps('details')} mt="md" label="Customize" placeholder="Customize your email..." />
            
            <Button type="submit" mt="md" onClick={handleSubmit}>
                Submit
            </Button>
        
            <Text mt="md">Form values:</Text>
            <Code block>{JSON.stringify(form.values, null, 2)}</Code>
        
            <Text mt="md">Submitted values:</Text>
            <Code block>{submittedValues ? JSON.stringify(submittedValues, null, 2) : '–'}</Code>
        </form>
      );
}

export const industries = [
    "Construction",
    "Mining",
    "Infrastructure",
    "Civil Engineering",
    "Transportation",
    "Urban Development",
    "Water and Wastewater Management",
    "Oil and Gas",
    "Environmental Services",
    "Railways",
    "Energy (Renewable and Non-Renewable)",
    "Geotechnical Engineering",
    "Government and Public Sector",
    "Heavy Machinery Manufacturing",
    "Road and Highway Construction",
    "Utilities (Power, Gas, Water)",
    "Tunneling and Subsurface Construction",
    "Maritime and Port Construction",
    "Building and Real Estate Development",
    "Smart Cities and Urban Planning"
  ];

  const companySizes = [
    "Micro (1-9 employees)",
    "Small (10-49 employees)",
    "Medium (50-249 employees)",
    "Large (250-999 employees)",
    "Enterprise (1000+ employees)"
  ];

  const emailVibes = [
    "Professional",
    "Casual",
    "Friendly",
    "Concise",
    "Empathetic",
    "Optimistic",
    "Polite",
    "Enthusiastic"
  ];