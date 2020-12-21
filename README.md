

# kafka jmx promethus 监控

## Quick Start

```shell
docker-compose up -d
docker ps

CONTAINER ID   IMAGE                       COMMAND                  CREATED             STATUS             PORTS                                        NAMES
f00e041acd78   confluentinc/cp-kafka       "/etc/confluent/dock…"   About an hour ago   Up About an hour   9092/tcp, 0.0.0.0:9094->9094/tcp             kafka-monitor_kafka2_1
e1cdc755d805   confluentinc/cp-kafka       "/etc/confluent/dock…"   About an hour ago   Up About an hour   9092/tcp, 0.0.0.0:9095->9095/tcp             kafka-monitor_kafka3_1
94595b46e3e6   confluentinc/cp-kafka       "/etc/confluent/dock…"   About an hour ago   Up About an hour   9092/tcp, 0.0.0.0:9093->9093/tcp             kafka-monitor_kafka1_1
6199662c07a9   prom/prometheus             "/bin/prometheus --c…"   About an hour ago   Up About an hour   0.0.0.0:9090->9090/tcp                       kafka-monitor_prometheus_1
12865a54dabc   confluentinc/cp-zookeeper   "/etc/confluent/dock…"   About an hour ago   Up About an hour   2888/tcp, 0.0.0.0:2181->2181/tcp, 3888/tcp   kafka-monitor_zoo1_1
80fb6e2ecdb6   grafana/grafana             "/run.sh"                About an hour ago   Up About an hour   0.0.0.0:3000->3000/tcp                       kafka-monitor_grafana_
```

集群包含，

- 一个供kafka使用的zookeeper，负责kafka集群管理和topics管理， 
- 三个以  jmx_exporter 为 javaagent  的 kafka 节点， 
- 一个从jmx_exporter 抓取监控数据的prometheus
- 一个 grafana ，以 prometheus 为数据源，进行监控数据可视化展示

## 介绍

### jmx exporter

[jmx_exporter](https://github.com/prometheus/jmx_exporter)  是 一个 javaagent,可以将宿主进程的 jmx 指标，暴露指定到http端口，处理成 promethus所接收的格式，并支持指标正则匹配，指标二次加工处理 等。

对于 kafka，可以通过 KAFKA_OPTS，指定  javaagent

```
KAFKA_OPTS: -javaagent:/usr/app/jmx_prometheus_javaagent.jar=7071:/usr/app/kafka-2_0_0.yml
```

### promethus

而 promethus 通过配置 targets ，从指定的端口 抓取指标，可以通过 promethus server 访问，也可以作为 grafana 数据源 进行可视化

```yaml
scrape_configs:
  - job_name: 'kafka1'
    static_configs: 
      - targets: ['kafka1:7071']

  - job_name: 'kafka2'
    static_configs:
      - targets: ['kafka2:7071']

  - job_name: 'kafka3'
    static_configs:
      - targets: ['kafka3:7071']
```

### grafana

#### 设置 prometheus 数据源

![image-20201221154118250](D:\github\jmx\kafka-monitor\kafka-monitor\README.assets\image-20201221154118250.png) 

#### 设置查询

![image-20201221155039107](D:\github\jmx\kafka-monitor\kafka-monitor\README.assets\image-20201221155039107.png)



## 示例

### 1. 创建一个 三副本三分区的topic test3

```shell
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 3 --partitions 3 --topic test3
bin/kafka-topics.sh --list --zookeeper localhost:2181
```

### 2. 生产与消费数据

生产

```shell
bin/kafka-console-producer.sh --broker-list localhost:9093 --topic test3
```

消费

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9093 --topic test3 --from-beginning
bin/kafka-console-consumer.sh --bootstrap-server localhost:9094 --topic test3 --from-beginning
bin/kafka-console-consumer.sh --bootstrap-server localhost:9095 --topic test3 --from-beginning
```

### 指标

具体的指标定义，请参阅  https://kafka.apache.org/documentation/#monitoring

这里先关注两个指标  MessagesInPerSec,  BytesInPerSec 

| DESCRIPTION               | MBEAN NAME                                                 | NORMAL VALUE |
| :------------------------ | :--------------------------------------------------------- | :----------- |
| Message in rate           | kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec |              |
| Byte in rate from clients | kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec    |              |

jmx导出的是：

kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec

kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec 

而 kafka-2_0_0.yml 中是选择将 PerSec 为后缀的指标进行累计，转换为相应的 _total指标

kafka_server_brokertopicmetrics_bytesin_total

采集规则如下：

```yaml
# Generic per-second counters with 0-2 key/value pairs
- pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*, (.+)=(.+), (.+)=(.+)><>Count
  name: kafka_$1_$2_$3_total
  type: COUNTER
  labels:
    "$4": "$5"
    "$6": "$7"
    
- pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*, (.+)=(.+)><>Count
  name: kafka_$1_$2_$3_total
  type: COUNTER
  labels:
    "$4": "$5"
    
- pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*><>Count
  name: kafka_$1_$2_$3_total
  type: COUNTER

- pattern: kafka.server<type=(.+), client-id=(.+)><>([a-z-]+)
  name: kafka_server_quota_$3
  type: GAUGE
  labels:
    resource: "$1"
    clientId: "$2"
```

#### Promethus Graph 数据展示

![image-20201221151020715](D:\github\jmx\kafka-monitor\kafka-monitor\README.assets\image-20201221151020715.png)

![image-20201221152041958](D:\github\jmx\kafka-monitor\kafka-monitor\README.assets\image-20201221152041958.png)

#### Grafana 数据展示

![image-20201221155218644](D:\github\jmx\kafka-monitor\kafka-monitor\README.assets\image-20201221155218644.png)