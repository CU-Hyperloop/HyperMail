import { Button, Container, Title, Text, Stack } from '@mantine/core';
import { Link } from 'react-router';
import '../styles/Home.css';

export default function Home() {
  return (
    <Container className='home-container' >
       <Text className="welcome">Welcome to Hypermail</Text>
         <Text className="welcome">An AI Sales Agent</Text>
        <Button component={Link} to="/generate" size="lg" >
          Get Started
        </Button>
      
    </Container>
  );
};
