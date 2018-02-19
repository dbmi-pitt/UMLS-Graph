# Graph-Deploy-AWS

Once you have a working database on Mac, go up one directory in Terminal and compress the neo4j-community-3.3.3 directory:
```bash
tar -cvzf neo4j.tar.gz neo4j-community-3.3.3
```

IF MAKING A NEW EC2 (updating an existing instance may not need to do) for neo4j database do this:
After you launch your instance using “YourKeyPair.pem” you’ll need to do all this, but note the public IP references in commands will be different numbers.

```bash
sftp -i ~/Desktop/YourKeyPair.pem ec2-user@eec2-54-205-5-136.compute-1.amazonaws.com
put neo4j.tar.gz
```

```bash
[ec2-user]$ sudo yum update -y
[ec2-user]$ sudo yum install -y docker
[ec2-user]$ sudo service docker start
[ec2-user]$ sudo docker info
```

```bash
ssh -i ~/Desktop/YourKeyPair.pem ec2-user@ec2-54-205-5-136.compute-1.amazonaws.com
mkdir neo4j
tar -xvzf neo4j.tar.gz -C neo4j
```

```bash
sudo docker run --detach \
--publish=7474:7474 --publish=7687:7687 \
--publish=7473:7473 \
--volume=/home/ec2-user/neo4j/neo4j/data:/data \
--volume=/home/ec2-user/neo4j/neo4j/logs:/logs \
--volume=/home/ec2-user/neo4j/neo4j/import:/var/lib/neo4j/import \
--volume=/home/ec2-user/neo4j/neo4j/conf/:/var/lib/neo4j/conf/ \
--ulimit=nofile=40000:40000 \
--name=myneo4j \
neo4j:3.3
```

More useful options here: https://neo4j.com/developer/docker-23/
* Stop Container: sudo docker stop myneo4j
* Delete Container: sudo docker rm myneo4j
