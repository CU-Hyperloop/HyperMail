import {Container, Text} from '@mantine/core';

export default function ListCompanies( data ){
    return (
        <Container size="md" style={{ 
            padding: '1rem', 
            borderRadius: '8px',
            borderColor: 'black',
            height: '100vh',
        }}>
            <Text>Companies</Text>
        
        </Container>
    )
}