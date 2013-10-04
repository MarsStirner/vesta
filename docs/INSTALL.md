http://docs.mongodb.org/manual/installation/
http://docs.mongodb.org/manual/tutorial/add-user-administrator/

use vesta
db.addUser({user: 'vesta_user', pwd: 'vesta_password', roles: ['readWrite', 'dbAdmin']})

use vesta_test
db.addUser({user: 'vesta_user', pwd: 'vesta_password', roles: ['readWrite', 'dbAdmin']})
