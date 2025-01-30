#!/bin/bash

# Install MongoDB
sudo apt update
sudo apt install -y mongodb

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Create Database and User
mongo <<EOF
use mydatabase
db.createUser({
    user: "devuser",
    pwd: "securepassword",
    roles: [{ role: "readWrite", db: "mydatabase" }]
})
EOF

echo "MongoDB setup complete."
