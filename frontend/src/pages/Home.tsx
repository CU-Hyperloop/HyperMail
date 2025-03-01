import { Button, Container, Title, Text, Stack } from '@mantine/core';
import { Link } from 'react-router';

export default function Home() {
  return (
    <Container style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <Stack align="center" spacing="lg">
        <Text className="welcome" size="xl" weight={500}>
          Welcome to
        </Text>
        <Title className="animated-title">HyperMail</Title>
        <Stack h={100} align="center" justify="center" spacing="md">
          <Button component={Link} to="/generate" size="lg">
            Generate Email
          </Button>
        </Stack>
      </Stack>
    </Container>
  );
};
