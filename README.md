Rackspace Cloud Monitoring plugin for PostgreSQL endpoints as an 
agent.plugin type of check.

Log in, select 1, and exit.

### Installation

    pip install agent.pgep

### Configuration

Create an INI file in `/etc/agent.pgep.ini`. **Please protect this file's permissions.** I recommend mode 0600 owned by uid 0 and gid 0.

You should title each INI section after the database you're connecting to. You can have multiple databases defined, but you can only test a connection to one at a time. For example, we can have a single database configured 

    # /etc/agent.pgep.ini
    [my_app_backend]
    user=my_app_user
    password=Dk292fdjoidslkkKkls
    host=db.myapp.com
    database=my_app_db
    
You can put anything in the INI sections that you see in the "basic connection parameters" at http://initd.org/psycopg/docs/module.html#psycopg2.connect : `database`, `user`, `password`, `host`, `port`.

If we were to invoke the plugin on the server, it would run as `agent.pgep my_app_backend`
    
Thus, when creating the check in the Rackspace monitoring API, that would translate to a JSON payload roughly equal to:

	POST /entities/<entityId>/checks
    {
        'type': 'agent.plugin',
        'details': {
            'file': 'agent.pgep',
            'args': [ 'my_app_backend' ],
            'timeout': 5000
        }
        'label': 'Webserver to PostgreSQL'
    }
    
If your app makes connections to multiple PostgreSQL hosts, you could simply repeat this for for each host it connects to.

### Metrics

This plugin yields the following metrics:

| Metric | Description | Type |
| ------ | ----------- | ---- |
| select_one | The result of `SELECT 1;` | int32 |
| tt_connect | The time (ms) it took to connect | int32 |
| tt_complete | The total time (ms) elapsed to run | int32 |

### Alarm Example

Here's an example of what your alarm criteria should look like. select_one should always equal 1, so the understanding is 
general database failure that you shouldn't need to write criteria for. It's included here to clarify what select_one as a
metric really is.

    if (metric['select_one'] != 1) {
        return new AlarmStatus(CRITICAL, "Something is VERY wrong");
    }
    if (metric['tt_connect'] > 3000) {
        return new AlarmStatus(WARNING, "DB connection time took #{tt_connect} ms");
    }
