# Wine Catalog
This is a python module that creates a website and JSON API for a list of wine items grouped into a wine category.
Users can edit or delete items they've creating.
Adding items, deleteing items and editing items requiring logging in with Google+.

## Instrucitons to Run Project

### Set up a Google Plus auth application.
1. go to https://console.developers.google.com/project and login with Google.
2. Create a new project
3. Name the project
4. Select "API's and Auth-> Credentials-> Create a new OAuth client ID" from the project menu
5. Select Web Application
6. On the consent screen, type in a product name and save.
7. In Authorized javascript origins add:
    http://0.0.0.0:7000
    http://localhost:7000
8. Click create client ID
9. Click download JSON and save it into the root director of this project.
10. Rename the JSON file "client_secret.json"
11. In login.html replace the line:
data-clientid="483619275284-64vm9vtj5ou3j3eaen161unv2j56rpb0.apps.googleusercontent.com"
so that it uses your Client ID from the web applciation.

### Setup the Database & Start the Server
1. In the root director, use the command vagrant up
2. The vagrant machine will install.
3. Once it's complete, type vagrant ssh to login to the VM.
4. In the vm, cd /vagrant
5. type "python database_setup.py" this will create the database with the categories defined in that script.
6. type "python wine_catalog.py" to start the server.

### Open in a webpage
1. Now you can open in a webpage by going to either:
    http://0.0.0.0:7000
    http://localhost:7000

