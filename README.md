# 创建私有网络
```bash 
sudo docker network create --driver bridge scantether_network
```
# 拉去最新mongodb
```bash
sudo docker pull mongo
```
# 创建 mongodb 容器

```bash
sudo docker run \
  --name mongodb_scantether \
  --restart unless-stopped \
  --detach \
  --volume mongodb_scantether_data:/data/db \
  --network scantether_network \
  mongo
```