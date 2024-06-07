import subprocess
import json
import shutil
import os

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def main():
    subscription_id = input("Enter your Azure subscription ID: ")
    role_name = input("Enter the name of the role, example hrz-role which should be unique: ")
    app_name = input("Enter the name of the application, example hrz-security which should be unique: ")

    # Set the subscription
    print("Setting the subscription...")
    command = f"az account set --subscription {subscription_id}"
    if run_command(command) is None:
        return

    # Login to Azure
    print("Logging in to Azure...")
    print("You will be redirected to the Browser for Login...")
    if run_command("az login") is None:
        return

    # Create the app, service principal, and certificate
    print("Creating the app, service principal, and certificate...")
    command = f"az ad sp create-for-rbac --name {app_name} --role Reader --scopes /subscriptions/{subscription_id} --create-cert"
    output = run_command(command)
    if output is None:
        return

    # Parse the output to get the appId and certificate file path
    sp_info = json.loads(output)
    app_id = sp_info['appId']
    cert_file_path = sp_info['fileWithCertAndPrivateKey']
    print(f"App ID: {app_id}")
    print(f"Certificate file path: {cert_file_path}")

    # Copy the certificate file to the directory where the script is running
    script_dir = os.path.dirname(os.path.abspath(__file__))
    destination_cert_path = os.path.join(script_dir, os.path.basename(cert_file_path))
    shutil.copy(cert_file_path, destination_cert_path)
    print(f"Certificate copied to {destination_cert_path}")

    # Create hrz-role.json file
    hrz_role = {
        "Name": role_name,
        "IsCustom": True,
        "description": "Custom role for integration",
        "assignableScopes": [f"/subscriptions/{subscription_id}"],
        "actions": [
            "Microsoft.Authorization/*/read",
            "Microsoft.ResourceHealth/availabilityStatuses/read",
            "Microsoft.Insights/alertRules/*",
            "Microsoft.Resources/deployments/*",
            "Microsoft.Resources/subscriptions/resourceGroups/read",
            "Microsoft.Support/*",
            "Microsoft.Web/listSitesAssignedToHostName/read",
            "Microsoft.Web/serverFarms/read",
            "Microsoft.Web/sites/config/read",
            "Microsoft.Web/sites/config/web/appsettings/read",
            "Microsoft.Web/sites/config/web/connectionstrings/read",
            "Microsoft.Web/sites/config/appsettings/read",
            "Microsoft.web/sites/config/snapshots/read",
            "Microsoft.Web/sites/config/list/action",
            "Microsoft.Web/sites/read",
            "Microsoft.KeyVault/checkNameAvailability/read",
            "Microsoft.KeyVault/deletedVaults/read",
            "Microsoft.KeyVault/locations/*/read",
            "Microsoft.KeyVault/vaults/*/read",
            "Microsoft.KeyVault/operations/read",
            "Microsoft.Compute/virtualMachines/runCommands/read",
            "Microsoft.Compute/virtualMachines/runCommands/write",
            "Microsoft.Compute/virtualMachines/runCommand/action"
        ],
        "notActions": [],
        "dataActions": [
            "Microsoft.KeyVault/vaults/*/read",
            "Microsoft.KeyVault/vaults/secrets/readMetadata/action"
        ],
        "notDataActions": []
    }

    with open("hrz-role.json", "w") as file:
        json.dump(hrz_role, file, indent=4)
    print("Created hrz-role.json file.")

    # Create custom role
    print("Creating custom role...")
    command = "az role definition create --role-definition hrz-role.json"
    if run_command(command) is None:
        return

    # Assign custom role to the app
    print("Assigning custom role to the app...")
    command = f"az role assignment create --role {role_name} --assignee {app_id} --scope /subscriptions/{subscription_id}"
    if run_command(command) is None:
        return

    # Create app-manifest.json file
    app_manifest = [
        {
            "resourceAppId": "00000003-0000-0000-c000-000000000000",
            "resourceAccess": [
                {"id": "246dd0d5-5bd0-4def-940b-0421030a5b68", "type": "Role"},
                {"id": "e321f0bb-e7f7-481e-bb28-e3b0b32d4bd0", "type": "Role"},
                {"id": "5e0edab9-c148-49d0-b423-ac253e121825", "type": "Role"},
                {"id": "bf394140-e372-4bf9-a898-299cfc7564e5", "type": "Role"},
                {"id": "6e472fd1-ad78-48da-a0f0-97ab2c6b769e", "type": "Role"},
                {"id": "dc5007c0-2d7d-4c42-879c-2dab87571379", "type": "Role"},
                {"id": "b0afded3-3588-46d8-8b3d-9842eff778da", "type": "Role"},
                {"id": "7ab1d382-f21e-4acd-a863-ba3e13f7da61", "type": "Role"},
                {"id": "197ee4e9-b993-4066-898f-d6aecc55125b", "type": "Role"},
                {"id": "9a5d68dd-52b0-4cc2-bd40-abcf44ac3a30", "type": "Role"},
                {"id": "f8f035bb-2cce-47fb-8bf5-7baf3ecbee48", "type": "Role"},
                {"id": "dbb9058a-0e50-45d7-ae91-66909b5d4664", "type": "Role"},
                {"id": "9e640839-a198-48fb-8b9a-013fd6f6cbcd", "type": "Role"},
                {"id": "37730810-e9ba-4e46-b07e-8ca78d182097", "type": "Role"},
                {"id": "c7fbd983-d9aa-4fa7-84b8-17382c103bc4", "type": "Role"}
            ]
        }
    ]

    with open("app-manifest.json", "w") as file:
        json.dump(app_manifest, file, indent=4)
    print("Created app-manifest.json file.")

    # Update the app with required resource access
    print("Updating the app with required resource access...")
    command = f"az ad app update --id {app_id} --required-resource-accesses @app-manifest.json"
    if run_command(command) is None:
        return

    # Grant administrator consent
    print("Granting administrator consent...")
    command = f"az ad app permission admin-consent --id {app_id}"
    if run_command(command) is None:
        return

    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
