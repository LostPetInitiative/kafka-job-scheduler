import unittest

from numpy import append

from src.kafkajobs.jobqueue.queue import JobQueueProducer, JobQueueWorker

class TestSum(unittest.TestCase):
    def test_pub_sub(self):
        producer = JobQueueProducer('localhost:9092', 'test_topic', 'test_producer', replication_factor=1)
        consumer = JobQueueWorker('test_consumer',kafkaBootstrapUrl='localhost:9092',topicName='test_topic',appName='test_consumer')
        producer.Enqueue('test_job', {'test': 'test'})
        job = consumer.TryGetNextJob()
        consumer.Commit()
        self.assertDictEqual(job, {'test': 'test'}, "Should be {'test': 'test'}")


if __name__ == '__main__':
    unittest.main()
