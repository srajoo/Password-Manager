# Password-Manager

## Steps to run

```sh
python -m venv env
source env/bin/activate
pip install requirements.py

cd password_manager

python manange.py runserver
```

## Features

- Custom user authentication. A secret key is generated for each user upon sign up to provide an extra layer of security
- Users are able to create organizations, add users to organizations with either editor or viewer access.
- Creators of organizations and users with editor level access to organizations are able to add users, update organization, and delete organization.
- In order to implement password sharing, vault structures have been created in organizations to store passwords.
- Users with creator access or organization level edit access can create, update, delete vaults.
- Organization owners, editors, and vault owners are able to give 'edit' or 'view' access to the vaults to other users.
- Organization owners, editors, vault owners, and users with vault edit access are able to create, update, and delete passwords within vaults.
- Vault access permission is given to organization owners, editors, vault owners, and users with vault edit or view access.
- Passwords can also be shared using a link accessible to all with a set expiry duration.
- Daily scheduled task of checking user configured passwords to notify users when the password is about to expire.

## Security Features

- A secret key is needed to login.
- Rate limiting has been implemented on APIs to protect against brute-force attack. The number of attempts have been limited to 10/minute.
- User accounts are locked out for 30 minutes after 3 failed attempts at logging in. 
- Passwords are salted then hashed before storing in the database.
- Password policies such as minimum length and character variety has been enforced. 

## ER Diagram

![erd](https://github.com/srajoo/Password-Manager/assets/103288051/0d9a8b8e-ee2c-4e2a-a3ea-b38f565f3462)


