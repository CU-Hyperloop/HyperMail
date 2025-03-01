import { Button, Container, Title, Text, Stack } from '@mantine/core';
import { Link } from 'react-router';

export default function Home() {
  return (
    <Container className="home-container">
      <Text className="welcome">Welcome to</Text>
      <Title className="animated-title">HyperMail</Title>
      <Stack h={200} bg="var(--mantine-color-body)" align="stretch" justify="center" gap="md">
        <Button component={Link} to="/generate" size="lg" >
          Generate email 
        </Button>
      </Stack>

    </Container>
  );
};