## DigiRaven

Welcome to the File Transfer Client project! This application facilitates file transfers using both FTP and SFTP protocols, leveraging multi-threading for enhanced performance and efficiency.
The File Transfer Client is a robust application that supports seamless file transfers between a local machine and remote servers using FTP and SFTP protocols. It is built with efficiency in mind, utilizing multi-threading to handle multiple file transfers concurrently.

Features
FTP and SFTP Support: Transfer files using both FTP and SFTP protocols.
Multi-threading: Enhance performance with concurrent file transfers.
Logging: Maintain logs of all file transfer activities.
User-friendly Interface: Simple command-line interface for easy interaction.
Database Integration: Store transfer logs and configurations using Firebase.

Python 3.6 or higher
paramiko library for SFTP
ftplib library for FTP (included with Python standard library)

File Descriptions
main.py
Handles the main workflow of the application, providing a user interface for initiating file transfers and managing connections.

ftp_client.py
Implements the FTP client using the ftplib library. Functions include connecting to an FTP server, uploading files, and downloading files.

ftp_threads.py
Manages FTP file transfers using multiple threads. This allows for concurrent uploading and downloading of files, significantly improving transfer speeds.

sftp_client.py
Implements the SFTP client using the paramiko library. Functions include connecting to an SFTP server, uploading files, and downloading files.

sftp_threads.py
Manages SFTP file transfers using multiple threads, similar to the FTP threading module.

database.py
Handles database interactions using sqlite3. This module is responsible for storing and retrieving file transfer logs and other configurations.
