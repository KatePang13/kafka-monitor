# jmx_exporter 迁移 dynatrace kafka plugin

环境搭建，请参考 [README](README.md)

## dynatrace plugin.json 格式

plugin.json 中，每个 timeseries 对应一个指标，格式如下:

```json
"metrics": [
    {
      "timeseries": {
        "key": "kafka.server.ReplicaManager.PartitionCount.Value",
        "dimensions": [
          "rx_pid"
        ],
        "unit": "Count",
        "displayname": "Kafka broker - Partitions"
      },
      "source": {
        "allowAdditionalKeys": true,
        "calculateDelta": false,
        "calculateRate": false,
        "aggregation": "AVG",
        "attribute": "Value",
        "domain": "kafka.server",
        "keyProperties": {
          "type": "ReplicaManager",
          "name": "PartitionCount"
        }
      }
    },
    {
      "timeseries": {
        "key": "pg.kafka.server.ReplicaManager.PartitionCount.Value",
        "dimensions": [
          "rx_pid"
        ],
        "unit": "Count",
        "displayname": "Kafka broker - Partitions"
      },
      "source": {
        "allowAdditionalKeys": true,
        "calculateDelta": false,
        "calculateRate": false,
        "aggregation": "MAX",
        "attribute": "Value",
        "domain": "kafka.server",
        "keyProperties": {
          "type": "ReplicaManager",
          "name": "PartitionCount"
        }
      },
      "entity": "PROCESS_GROUP"
    }
]    
```

通过   domain ， keyProperties<type, name>,   attribute    字段定位相应的指标，以上这2个指标采集的是同一个指标，对应的是kafka中的

| DESCRIPTION      | MBEAN NAME                                           | NORMAL VALUE               |
| :--------------- | :--------------------------------------------------- | :------------------------- |
| Partition counts | kafka.server:type=ReplicaManager,name=PartitionCount | mostly even across brokers |

`pg.kafka.server.ReplicaManager.PartitionCount.Value` 是对  `kafka.server.ReplicaManager.PartitionCount.Value` 的聚合

`"entity": "PROCESS_GROUP"`，它对应的是整个 PROCESS_GROUP，而不是单个实例；

- 对于  entity，有三个级别的设置，`metadate`, `metrics`，`timeseries` ，默认继承上一层的配置，最顶层的默认值为 PROCESS_GROUP_INSTANCE
- 在命名中也有体现，以 `pg.` 为前缀
- `aggregation`  时间序列数据点聚合（MIN / MAX / AVG / SUM）。默认值：AVG。这里的聚合是 MAX

关于 plugin.json的详细配置，请参阅 [plugin_json_apidoc](https://dynatrace.github.io/plugin-sdk/api/plugin_json_apidoc.html) 。

示例的指标  PartitionCount.Value 在 jconsole 中显示如下：

![image-20201221221126545](D:\github\jmx\kafka-monitor\kafka-monitor\jmx_exporter 迁移 dynatrace kafka plugin.assets\image-20201221221126545.png)



## kafka plugin 采集的指标

```json
grep  "timeseries" plugin.json -A 1 |grep key
        "key": "kafka.server.BrokerTopicMetrics.BytesInPerSec.OneMinuteRate",
        "key": "kafka.server.BrokerTopicMetrics.BytesOutPerSec.OneMinuteRate",
        "key": "kafka.server.BrokerTopicMetrics.MessagesInPerSec.OneMinuteRate",
        "key": "kafka.server.ReplicaManager.PartitionCount.Value",
        "key": "pg.kafka.server.ReplicaManager.PartitionCount.Value",
        "key": "kafka.server.ReplicaManager.UnderReplicatedPartitions.Value",
        "key": "pg.kafka.server.ReplicaManager.UnderReplicatedPartitions.Value",
        "key": "pg.kafka.controller.KafkaController.OfflinePartitionsCount.Value",
        "key": "pg.kafka.controller.KafkaController.ActiveControllerCount.Value",
        "key": "kafka.log.LogFlushStats.LogFlushRateAndTimeMs.Percentile95th",
        "key": "kafka.log.LogFlushStats.LogFlushRateAndTimeMs.Mean",
        "key": "kafka.network.RequestMetrics.RequestsPerSec.Produce.OneMinuteRate.request",
        "key": "kafka.network.RequestMetrics.RequestsPerSec.FetchConsumer.OneMinuteRate.request",
        "key": "kafka.network.RequestMetrics.RequestsPerSec.FetchFollower.OneMinuteRate.request",
        "key": "kafka.network.RequestMetrics.TotalTimeMs.Produce.Count.request",
        "key": "kafka.network.RequestMetrics.TotalTimeMs.FetchConsumer.Count.request",
        "key": "kafka.network.RequestMetrics.TotalTimeMs.FetchFollower.Count.request",
        "key": "kafka.server.BrokerTopicMetrics.TotalProduceRequestsPerSec.OneMinuteRate",
        "key": "kafka.server.BrokerTopicMetrics.TotalFetchRequestsPerSec.OneMinuteRate",
        "key": "kafka.server.BrokerTopicMetrics.FailedProduceRequestsPerSec.OneMinuteRate",
        "key": "kafka.server.BrokerTopicMetrics.FailedFetchRequestsPerSec.OneMinuteRate",
        "key": "kafka.controller.ControllerStats.LeaderElectionRateAndTimeMs.OneMinuteRate",
        "key": "pg.kafka.controller.ControllerStats.LeaderElectionRateAndTimeMs.OneMinuteRate",
        "key": "kafka.controller.ControllerStats.UncleanLeaderElectionsPerSec.OneMinuteRate",
        "key": "pg.kafka.controller.ControllerStats.UncleanLeaderElectionsPerSec.OneMinuteRate",
        "key": "kafka.server.ReplicaManager.LeaderCount.Value",
        "key": "kafka.server.ReplicaFetcherManager.MaxLag.Replica.Value",
        "key": "kafka.network.RequestChannel.RequestQueueSize.Value",
        "key": "kafka.server.SessionExpireListener.ZooKeeperDisconnectsPerSec.OneMinuteRate",
        "key": "kafka.server.SessionExpireListener.ZooKeeperExpiresPerSec.OneMinuteRate",
        "key": "kafka.producer.producer-metrics.request-rate",
        "key": "kafka.consumer.consumer-metrics.request-rate",
        "key": "kafka.connect.connect-metrics.request-rate",
        "key": "kafka.producer.producer-metrics.request-size-avg",
        "key": "kafka.consumer.consumer-metrics.request-size-avg",
        "key": "kafka.connect.connect-metrics.request-size-avg",
        "key": "kafka.producer.producer-metrics.incoming-byte-rate",
        "key": "kafka.consumer.consumer-metrics.incoming-byte-rate",
        "key": "kafka.connect.connect-metrics.incoming-byte-rate",
        "key": "kafka.producer.producer-metrics.outgoing-byte-rate",
        "key": "kafka.consumer.consumer-metrics.outgoing-byte-rate",
        "key": "kafka.connect.connect-metrics.outgoing-byte-rate",
```

## 迁移

### 直接采集指标

上面的指标中，不是以 pg 开头的，都是直接从 jmx 直接查询得到的指标，直接将 plugin.json 中的关于定位jmx属性的配置翻译成 jmx_exporter 的配置文件即可，为了避免重复性工作，写了一个小工具  [transform.py](tools/transform.py)  进行配置转换, 得到的配置格式如下：

```yaml
lowercaseOutputName: true
rules:
- name: kafka.server.BrokerTopicMetrics.BytesInPerSec.OneMinuteRate
  pattern: kafka.server<type=BrokerTopicMetrics, name=BytesInPerSec><>OneMinuteRate
  type: GAUGE
#...
```

### 聚合指标

dynatrace 中的 plugin.json 中有一个参数 entity，默认是  `PROCESS_GROUP_INSTANCE` ，而有一些指标是 `"entity": "PROCESS_GROUP"`， 这些指标不可能直接通过 jmx 查询 得到，需要在采集到数据之后，对数据做聚合，这里我们暂且在 grafana 可视化的时候，使用 PromQL 进行聚合操作

比如   `pg.kafka.server.ReplicaManager.PartitionCount.Value`  是去聚合所有的 `kafka.server.ReplicaManager.PartitionCount.Value` 取最大值，PromQL 如下所示：

```
max(kafka_server_replicamanager_partitioncount_value) without(instance, job)
```



## 对比验证

### 首页指标

**dynatrace 的 kafka broker:**

![image-20201222183543791](D:\github\jmx\kafka-monitor\kafka-monitor\jmx_exporter迁移dynatrace_kafka_plugin.assets\image-20201222183543791.png)

**grafana 的 kafka-broker：**

![image-20201222183640614](D:\github\jmx\kafka-monitor\kafka-monitor\jmx_exporter迁移dynatrace_kafka_plugin.assets\image-20201222183640614.png)

**dynatrace 的 kafka network:**

![image-20201222183741754](D:\github\jmx\kafka-monitor\kafka-monitor\jmx_exporter迁移dynatrace_kafka_plugin.assets\image-20201222183741754.png)

**grafana 的 kafka-broker:**

![image-20201222183825830](D:\github\jmx\kafka-monitor\kafka-monitor\jmx_exporter迁移dynatrace_kafka_plugin.assets\image-20201222183825830.png)



**经对比，该方法可以采集所有 dynatrace server 上显示的所有 kafka 指标。**