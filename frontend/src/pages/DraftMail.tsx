import { TextInput, Button, Container, Stack, Group, Textarea, Text } from '@mantine/core';

export default function MailEditor() {
    return (
        <Container size="md" style={{ 
            padding: '1rem', 
            borderRadius: '8px',
            backgroundColor: 'red',  // Changed from white/light background
            height: '100vh',
        }}>
            <Stack spacing="md" style={{ width: '100%' }}>
                <Group position="apart" style={{ backgroundColor: 'transparent' }}>
                    <Text style={{ color: '#FFD700' }}>To: </Text>
                    <TextInput placeholder="To" style={{ flex: 1 }} />
                </Group>
                <Group position="apart" style={{ backgroundColor: 'transparent' }}>
                    <Text style={{ color: '#FFD700' }}>Cc: </Text>
                    <TextInput placeholder="Cc" style={{ flex: 1 }} />
                </Group>

                <Group position="apart" style={{ backgroundColor: 'transparent' }}>
                    <Text style={{ color: '#FFD700' }}>Subject: </Text>
                    <TextInput placeholder="Subject" style={{ flex: 1 }} />
                </Group>
                
                <Textarea 
                    placeholder="Body" 
                    autosize 
                    minRows={15}
                    style={{ backgroundColor: 'transparent' }}
                />

                <Group position="right" style={{ backgroundColor: 'transparent' }}>
                    <Button variant="outline" color="blue">Cancel</Button>
                    <Button color="blue">Send</Button>
                </Group>
            </Stack>
        </Container>
    );
}