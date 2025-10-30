Project Setup Guide

Translation Project
This project is a Django-based web application designed to manage translation and review workflows efficiently. It supports user registration, authentication, job allocation, and detailed dashboards for administrators, translators, and reviewers.
This guide provides step-by-step instructions for setting up the Translation Project, including installation of PostgreSQL, pgAdmin4, and PyCharm (2024.2.4 or above) for both Windows and Ubuntu operating systems.

Table of Contents
1. [Prerequisites]
2. [Installing PostgreSQL]
   - [Windows]
   - [Ubuntu]
3. [Installing pgAdmin4]
   - [Windows]
   - [Ubuntu]
4. [Installing PyCharm]
   - [Windows]
   - [Ubuntu]
5. [Setting Up the Translation Project]

 1.Prerequisites
Ensure the following before proceeding:
- Operating System: Windows 10/11 or Ubuntu 20.04/22.04
- Python: Version 3.10 or above
- Internet Connection: Required for downloading software


2.Installing PostgreSQL
Windows
1. Visit the [PostgreSQL Official Downloads Page] https://www.postgresql.org/download/windows/ 
2. Download the PostgreSQL installer for Windows.
3. Run the installer and follow the setup instructions:
   - Choose the installation directory.
   - Set a password for the PostgreSQL superuser account.
   - Use the default port (5432) unless needed otherwise.
4. Verify installation:
   - Open Command Prompt.
   - Run: `psql --version`.
Ubuntu
1.	Open the terminal and run the following commands:
•	sudo apt update
2.	You can install PostgreSQL using the following command:
•	sudo apt install postgresql postgresql-contrib
3.	After the installation is complete, you can check the status of the PostgreSQL service to ensure it is running:
•	sudo systemctl status postgresql
4.	By default, PostgreSQL creates a user named postgres. You can switch to this user and access the PostgreSQL prompt using the following commands:
•	sudo -i -u postgres
•	psql
5.	You should now be at the PostgreSQL prompt, which looks like this:
•	postgres=#
6.	You can change the password for the postgres user by running the following command in the PostgreSQL prompt:
•	\password postgres
 
3.Installing PgAdmin 4 
   Windows
	Visit the pgAdmin Download Page: Go to the official pgAdmin download page:        
https://www.pgadmin.org/download 
	Click on the Windows installer link to download the latest version of pgAdmin4
	Once the download is complete, locate the installer file (usually in your Downloads folder) and double-click it to run.
	Follow the prompts in the installation wizard. You can choose the installation directory and select additional components if needed.
	After the installation is complete, you can launch pgAdmin 4 from the Start menu or desktop shortcut.

    Ubuntu
	Add the pgAdmin Repository: Open a terminal and run the following commands to set up the repository:
	curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
OR
	sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

Install pgAdmin: You can install pgAdmin for both desktop and web modes or choose one of them:
•	sudo apt install pgadmin4
Launch pgAdmin:
For desktop mode, you can find pgAdmin in your applications menu.




4.Installation of PyCharm

Windows
Go to the official JetBrains PyCharm download page: https://www.jetbrains.com/pycharm/download/?section=windows 
Choose the version you want to install (Professional or Community). The Community version is free and open-source.
Once the download is complete, locate the installer file (usually in your Downloads folder) and double-click it to run.
	Follow the Installation WizardClick "Next" on the welcome screen.
Choose the installation directory (the default is usually fine) and click "Next".
Select the installation options you want (e.g., creating a desktop shortcut, associating .py files with PyCharm) and click "Next".
Click "Install" to begin the installation.
	Complete the Installation:
Once the installation is complete, you can choose to run PyCharm immediately by checking the box and clicking "Finish".
	Configure PyCharm:
On the first launch, you may be prompted to import settings from a previous version. Choose your preference and click "OK".
Follow the setup wizard to configure your IDE according to your preferences.

Ubuntu
Go to the official JetBrains PyCharm download page: https://www.jetbrains.com/pycharm/download/?section=linux 
	Choose the version you want to install (Professional or Community) and download the .tar.gz file for Linux.
Extract the Downloaded File:
	Open a terminal and navigate to the directory where the downloaded file is located (usually the Downloads folder):
	cd ~/Downloads
	Extract the downloaded file (replace pycharm-community-*.tar.gz with the actual filename):
	tar -xzf pycharm-community-*.tar.gz

	Move the extracted folder to /opt (a common location for optional software):
	sudo mv pycharm-community-* /opt/pycharm
	Launch PyCharm:
o	You can now launch PyCharm from your applications menu or by running the following command in the terminal:
	/opt/pycharm/bin/pycharm.sh
	Configure PyCharm:
	On the first launch, you may be prompted to import settings from a previous version. Choose your preference and click "OK".
Follow the setup wizard to configure your IDE according to your preferences.

Clone the repository:
cd your-repository
	  Install dependencies:
o	pip install -r requirements.txt


KEYMAN

Keyman is a software that allows users to create and use custom keyboard layouts for various languages. Below are detailed instructions for installing the Keyman module on both Windows and Ubuntu.

Windows

Download Keyman:

o	Go to the official Keyman website: https://keyman.com/downloads/ 
.
o	Click on the "Download" button for the Windows version.

Run the Installer:

o	Once the download is complete, locate the installer file (usually in your Downloads folder) and double-click it to run.

Follow the Installation Wizard:

o	You may see a User Account Control prompt asking for permission to run the installer. Click "Yes" to proceed.
o	The Keyman installation wizard will open. Click "Next" to continue.
o	Read and accept the license agreement, then click "Next".
o	Choose the installation directory (the default is usually fine) and click "Next".
o	Select any additional components you want to install (if prompted) and click "Next".

Complete the Installation:

o	Click "Install" to begin the installation process.
o	Once the installation is complete, you can choose to launch Keyman immediately by checking the box and clicking "Finish".

Configure Keyman:

o	After installation, you can open Keyman from the Start menu.
o	You may need to download and install specific keyboard layouts from the Keyman website or use the Keyman Developer to create your own layouts.
Ubuntu
Add the Keyman Repository:
o	Open a terminal and run the following commands to add the Keyman repository:
	sudo add-apt-repository ppa:keyman/keyman
Update the Package List:
o	After adding the repository, update your package list:
	sudo apt update
Install Keyman:
o	Now, install Keyman using the following command:
	sudo apt install keyman
Install Keyman Keyboard Layouts:
o	

o	You can install additional keyboard layouts using the Keyman application. Open Keyman from your applications menu.
o	You can browse and install keyboard layouts from the Keyman repository.
Configure Keyman:
o	After installation, you can configure Keyman by launching it from your applications menu.
o	You can select the desired keyboard layout and customize settings as needed.


	Configure the database in settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<your_database>',
        'USER': '<your_user>',
        'PASSWORD': '<your_password>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}





	Apply database migrations:
	python manage.py makemigrations
	python manage.py migrate
	Create a superuser:
	python manage.py createsuperuser
	Run the development server:
	python manage.py runserver

________________________________________





#   T r a n s l a t i o n - M a n a g e m e n t - S y s t e m  
 