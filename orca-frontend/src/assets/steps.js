import policyData from "./aws-policy.json";

export const steps = [
    {
        title: "Step 1: Create an AWS Account",
        content: `
            Visit the <a href="https://aws.amazon.com/" target="_blank">AWS Sign Up Page</a>. 
            Click on <strong>"Create a new AWS account"</strong>. Enter your email address, 
            payment details, and personal information. Once registered, log in to the AWS 
            Management Console.
        `
    },
    {
        title: "Step 2: Navigate to the IAM Console",
        content: `
            From the AWS Management Console, search for <strong>"IAM"</strong> using the search bar. 
            Click on the IAM service to navigate to the IAM Dashboard, where you can manage users, 
            roles, and permissions.
        `
    },
    {
        title: "Step 3: Create a New IAM User",
        content: `
            In the left-hand menu of the IAM Dashboard, click <strong>"Users"</strong>, then click 
            <strong>"Add users"</strong>. Provide a <strong>User name</strong> and select 
            <strong>"Access key"</strong> for programmatic access (CLI, SDKs, APIs). Click "Next" to 
            proceed to permissions.
        `
    },
    {
        title: "Step 4: Create and Attach a Custom Policy",
        content: `
            In the <strong>"Set permissions"</strong> step, click <strong>"Attach policies directly"</strong>, 
            then click <strong>"Create policy"</strong>. Use the JSON policy below:
        `,
        policy: policyData
    },
    {
        title: "Step 5: Attach the Policy to the User",
        content: `
            Go back to the <strong>"Add user"</strong> page, search for the custom policy you just 
            created, and select it. Click <strong>"Next"</strong> to review and retrieve access key and secret access key
        `
    },
    {
        title: "Step 6: Upload Cloud Credentials",
        content: `
            Once you have retrieved the necessary access credentials, proceed to click the button below and upload your credentials to Orca
        `,
        requiresUpload: true
    }
    
];

