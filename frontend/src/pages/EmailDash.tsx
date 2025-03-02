import ListCompanies from "../components/ListCompanies"
import MailEditor from "./DraftMail"
import { TextInput, Button, Container, Stack, Group, Textarea, Text, Divider } from '@mantine/core';
import { useLocation } from "react-router";

export default function EmailDash() {

    const location = useLocation();

    const data = location.state?.data;

    console.log('Data from state:', data);

    return (


        <div>
            <Group>
                <ListCompanies />
                <Divider></Divider>
                <MailEditor />
            </Group>

        </div>
    )
}