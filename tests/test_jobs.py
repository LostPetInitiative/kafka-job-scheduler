import unittest

from src.kafkajobs.jobqueue.queue import JobQueueProducer, JobQueueWorker

class TestSum(unittest.TestCase):
    def test_pub_sub(self):
        consumer = JobQueueWorker('test_consumer',kafkaBootstrapUrl='localhost:9092',topicName='test_topic',appName='test_consumer', replication_factor=1)
        producer = JobQueueProducer('localhost:9092', 'test_topic', 'test_producer', replication_factor=1)
        producer.Enqueue('test_job', {'test': 'test'})
        print("Enqueued job")
        for i in range(0,30):
            job = consumer.TryGetNextJob(1000)
            if not(job is None):
                break
            else:
                print("No job found")
        consumer.Commit()
        self.assertDictEqual(job, {'test': 'test'}, "Should be {'test': 'test'}")


if __name__ == '__main__':
    unittest.main()
