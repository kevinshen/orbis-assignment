# State Street ETF Data

## Local development

### Running on host machine

Create a test database, and set the MySQL database configuration in app.py line 14:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db'
```

Run the SQL commands in init.sql. Then cd into the app directory, and run ```bash python app.py ```

### Running on VirtualBox

MySQL setup should be done within the VM.

Install [vagrant](http://www.vagrantup.com/), then run `vagrant up` to provision the VM. Then issue these commands to log into vagrant and run the application:

```bash
vagrant ssh
cd /vagrant
cd app
python app.py
```