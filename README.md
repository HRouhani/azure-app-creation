# Azure Application Setup Script

This script helps you create an application in Azure, set up a service principal, and assign a custom role with the required permissions.

## Prerequisites

- Azure CLI installed and configured on your machine.
- Access to an Azure subscription.

## Usage

1. Clone the repository:

   ```sh
   git clone https://github.com/Hrouhani/your-repository-name.git
   cd your-repository-name


2. Run the script:

    ```sh
   python3 


3. Follow the prompts to input your Azure subscription ID, role name, and application name.


##  What the Script Does

1.  Sets the Azure subscription:
The script starts by setting the specified Azure subscription using the Azure CLI command **az account set --subscription**.

2.  Logs in to Azure:
It prompts the user to log in to Azure, which opens a browser window for authentication using the Azure CLI command **az login**.

3.  Creates an application, service principal, and certificate:
The script creates an Azure AD application, a service principal, and a certificate using the command **az ad sp create-for-rbac --name**.

4.  Copies the certificate file to the script's directory:
The certificate file created is copied to the directory where the script is running.

5.  Creates a custom role (mondoo-role.json):
It generates a JSON file defining a custom role with specific permissions required for the application.

6.  Assigns the custom role to the application:
The custom role is assigned to the newly created application using the command **az role assignment create**.

7.  Creates an application manifest (app-manifest.json):
The script creates a JSON file defining the required resource accesses for the application.

8.  Updates the application with the required resource accesses:
It updates the application to include the necessary permissions defined in the manifest using the command **az ad app update**.

9.  Grants administrator consent:
Finally, the script grants administrator consent to the application for the required permissions using the command **az ad app permission admin-consent**.
