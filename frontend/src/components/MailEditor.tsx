import { TextInput, Button, Container, Stack, Group, Textarea, Text } from '@mantine/core';


export default function MailEditor() {

    return (
        <Container size="md" style={{ backgroundColor: '#f9fafb', padding: '2rem', borderRadius: '8px' }}>
            <Stack spacing="md">
                <Group position="apart">
                    <Text>To: </Text>
                    <TextInput placeholder="To"  />
                </Group>
                <Group position="apart">
                    <Text>Cc: </Text>
                    <TextInput placeholder="Cc"   />
                </Group>

                <Group position="apart">
                    <Text>Subject: </Text>
                    <TextInput placeholder="Subject"  />
                </Group>
                
                <Textarea placeholder="Body" autosize minRows={10}  />

                <Group position="right">
                <Button variant="outline" color="gray">Cancel</Button>
                <Button color="blue">Send</Button>
                </Group>
            </Stack>
        </Container>
    )
}