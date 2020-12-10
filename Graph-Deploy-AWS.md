# Graph-Deploy-AWS

Once you have a working database on Mac, and you've added your preferred user and deleted neo4j user, don't forget to go into neo4j configuration file and set read only database (one can copy auth and config files from previous), and may set larger heap sizes, and also remove used import csv files to reduce size. Then, go up one directory in Terminal and compress the neo4j directory:
```bash
tar -cvzf neo4j-4.2.tar.gz neo4j-4.2
```

```bash
sftp -i ~/Desktop/YourKeyPair.pem ec2-user@ec2-54-205-5-136.compute-1.amazonaws.com
put neo4j-4.2.tar.gz
```

```bash
ssh -i ~/Desktop/YourKeyPair.pem ec2-user@ec2-54-205-5-136.compute-1.amazonaws.com
mkdir neo4j
tar -xvzf neo4j-4.2.tar.gz -C neo4j
```

```bash
[ec2-user]$ sudo yum update -y
[ec2-user]$ sudo yum install -y docker
[ec2-user]$ sudo service docker start
[ec2-user]$ sudo docker info
```
#### Some APIs may use APOC Core so installing to the neo4j implementation is recommended. 
APOC Core can be installed by moving the APOC jar file from the $NEO4J_HOME/labs directory to the $NEO4J_HOME/plugins directory and restarting Neo4j. APOC Full contains all the procedures and functions included in APOC Core. You must not install both libraries.

```bash
sudo docker run --detach \
--publish=7474:7474 --publish=7687:7687 \
--publish=7473:7473 \
--volume=/home/ec2-user/neo4j/neo4j-4.2/data:/data \
--volume=/home/ec2-user/neo4j/neo4j-4.2/logs:/logs \
--volume=/home/ec2-user/neo4j/neo4j-4.2/plugins:/plugins \
--volume=/home/ec2-user/neo4j/neo4j-4.2/conf/:/conf/ \
--ulimit=nofile=40000:40000 \
--name=myneo4j \
neo4j:4.2
```

More useful options here: https://neo4j.com/developer/docker-23/
* Stop Container: sudo docker stop myneo4j
* Delete Container: sudo docker rm myneo4j
