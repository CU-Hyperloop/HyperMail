import ListCompanies from "../components/ListCompanies"
import MailEditor from "./DraftMail"
import { TextInput, Button, Container, Stack, Group, Textarea, Text, Divider, Grid } from '@mantine/core';
import { useLocation } from "react-router";

export default function EmailDash() {

    const location = useLocation();

    const data = location.state?.data;

    console.log('Data from state:', data);

    return (


        <div>
            <Grid grow>
                <Grid.Col span={4}>
                    
                    <ListCompanies />
                </Grid.Col>
                <Grid.Col span={8}>
                    <MailEditor />
                </Grid.Col>
            </Grid>

        </div>
    )
}