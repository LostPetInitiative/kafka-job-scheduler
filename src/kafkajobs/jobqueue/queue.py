import json
import kafka3
import os
from kafka3.admin import KafkaAdminClient, NewTopic

def strSerializer(jobName):
    return jobName.encode('utf-8')

def strDeserializer(jobNameBytes):
    return jobNameBytes.decode('utf-8')

def dictSerializer(job):
    #print(type(job))
    #print(job)
    return json.dumps(job, indent=2).encode('utf-8')

def dictDeserializer(jobBytes):
    #print(type(job))
    #print(job)
    return json.loads(jobBytes.decode('utf-8'))

class JobQueue:
    def __init__(self, kafkaBootstrapUrl,topicName, appName, num_partitions=None, replication_factor=None, retentionHours = None):
        if replication_factor is None:
            replication_factor = int(os.environ.get('KAFKA_REPLICATION_FACTOR', '1'))
        if num_partitions is None:
            num_partitions = int(os.environ.get('KAFKA_NUM_PARTITIONS', '8'))
        if retentionHours is None:
            retentionHours = int(os.environ.get('KAFKA_RETENTION_HOURS', '168')) # 168 hours = 1 week

        self.kafkaBootstrapUrl = kafkaBootstrapUrl
        self.topicName = topicName
        self.appName = appName
        admin_client = KafkaAdminClient(
            bootstrap_servers=kafkaBootstrapUrl, 
            client_id=appName
            )

        topic_list = []
        topic_configs = {
            'retention.ms': str(retentionHours*60*60*1000),
        }
        topic_list.append(NewTopic(name=topicName, num_partitions=num_partitions, replication_factor=replication_factor,topic_configs=topic_configs))
        topics = admin_client.list_topics()
        if not (topicName in topics):
            try:
                admin_client.create_topics(new_topics=topic_list, validate_only=False)
                print("Topic {0} is created".format(topicName))
            except kafka3.errors.TopicAlreadyExistsError:
                print("Topic {0} already exists".format(topicName))
        else:
            print("Topic {0} already exists".format(topicName))
        admin_client.close()

class JobQueueProducer(JobQueue):
    '''Posts Jobs as JSON serialized python dicts'''
    def __init__(self, *args, **kwargs):
        super(JobQueueProducer, self).__init__(*args, **kwargs)

        self.producer = kafka3.KafkaProducer( \
            bootstrap_servers = self.kafkaBootstrapUrl, \
            client_id = self.appName,
            key_serializer = strSerializer,
            value_serializer = dictSerializer,
            max_request_size = 32*1024*1024,
            acks = "all",
            retries = 10,
            compression_type = "gzip")

    def Enqueue(self, jobName, jobBody):
        success = False
        attempt = 0
        while (not success) and (attempt < 10):
            try:
                self.producer.send(self.topicName, value=jobBody, key= jobName)
                self.producer.flush()
                success = True
            except kafka3.errors.KafkaTimeoutError as err:
                attempt += 1
                print(f"Error during kafka job message enqueue: {err}. Attempt {attempt}")
        if success:
            return
        else:
            raise "Failed to enqueue the message to Kafka"
                
class JobQueueWorker(JobQueue):
    '''Fetchs sobs as JSON serialized python dicts'''
    def __init__(self, group_id, max_permited_work_time_sec=300, *args, **kwargs):
        super(JobQueueWorker, self).__init__(*args, **kwargs)

        self.teardown = False
        self.consumer = kafka3.KafkaConsumer(self.topicName, \
            bootstrap_servers = self.kafkaBootstrapUrl, \
            client_id = self.appName,
            group_id = group_id,
            auto_offset_reset = "earliest",
            key_deserializer = strDeserializer,
            enable_auto_commit = False,
            max_poll_interval_ms = max_permited_work_time_sec * 1000,
            value_deserializer = dictDeserializer)

    def GetNextJob(self, pollingIntervalMs = 1000):
        extracted = False
        while (not self.teardown) and (not extracted):
            res = self.consumer.poll(pollingIntervalMs, max_records=1)
            #print("Got {0}. Len {1}".format(res,len(res)))
            if(len(res) == 1):
                for key in res:
                    jobValue = res.get(key)[0].value
                    return jobValue        

    def TryGetNextJob(self, pollingIntervalMs = 1000):
        res = self.consumer.poll(pollingIntervalMs, max_records=1)
        #print("Got {0}. Len {1}".format(res,len(res)))
        if(len(res) == 1):
            for key in res:
                jobValue = res.get(key)[0].value
                return jobValue
        else:
            return None


    def Commit(self):
        self.consumer.commit()