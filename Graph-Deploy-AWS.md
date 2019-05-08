# Graph-Deploy-AWS

Once you have a working database on Mac, and you've added your preferred user and deleted neo4j user, don't forget to go into neo4j configuration file and set read only database. Then, go up one directory in Terminal and compress the neo4j-community-3.5.5 directory:
```bash
tar -cvzf neo4j.tar.gz neo4j-community-3.5.5
```

```bash
sftp -i ~/Desktop/YourKeyPair.pem ec2-user@ec2-54-205-5-136.compute-1.amazonaws.com
put neo4j.tar.gz
```

```bash
ssh -i ~/Desktop/YourKeyPair.pem ec2-user@ec2-54-205-5-136.compute-1.amazonaws.com
mkdir neo4j
tar -xvzf neo4j.tar.gz -C neo4j
```

```bash
[ec2-user]$ sudo yum update -y
[ec2-user]$ sudo yum install -y docker
[ec2-user]$ sudo service docker start
[ec2-user]$ sudo docker info
```

```bash
sudo docker run --detach \
--publish=7474:7474 --publish=7687:7687 \
--publish=7473:7473 \
--volume=/home/ec2-user/neo4j/neo4j-community-3.5.5/data:/data \
--volume=/home/ec2-user/neo4j/neo4j-community-3.5.5/logs:/logs \
--volume=/home/ec2-user/neo4j/neo4j-community-3.5.5/import:/var/lib/neo4j/import \
--volume=/home/ec2-user/neo4j/neo4j-community-3.5.5/conf/:/var/lib/neo4j/conf/ \
--ulimit=nofile=40000:40000 \
--name=myneo4j \
neo4j
```

More useful options here: https://neo4j.com/developer/docker-23/
* Stop Container: sudo docker stop myneo4j
* Delete Container: sudo docker rm myneo4j
