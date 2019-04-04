---
title: 'c#调用MQ'
date: 2018-05-23 17:44:26
tags:
---

MQ.

![示例图片](csharp1/5501127.jpg)

<!--more-->

# 1 引入RabbitMQ.Client
# 2 发送端代码
```
class Program
{
	static void Main(string[] args)
	{
		var factory = new ConnectionFactory();
		factory.HostName = "localhost";
		factory.UserName = "liujinquan";
		factory.Password = "123456";

		try
		{
			using (var connection = factory.CreateConnection())
			{
				using (var channel = connection.CreateModel())
				{
					channel.QueueDeclare("hello", false, false, false, null);
					string message = "Hello World";
					var body = Encoding.UTF8.GetBytes(message);
					channel.BasicPublish("", "hello", null, body);
					Console.WriteLine(" set {0}", message);
				}
			}
		}
		catch (Exception ex)
		{
			Console.WriteLine(ex.Message);
		}
	}
}
```
# 3接收端代码
```
class Program
    {
        static void Main(string[] args)
        {
            var factory = new ConnectionFactory();
            factory.HostName = "localhost";
            factory.UserName = "liujinquan";
            factory.Password = "123456";

            try
            {
                using (var connection = factory.CreateConnection())
                {
                    using (var channel = connection.CreateModel())
                    {
                        channel.QueueDeclare("hello", false, false, false, null);

                        var consumer = new QueueingBasicConsumer(channel);
                        channel.BasicConsume("hello", true, consumer);

                        Console.WriteLine(" waiting for message.");
                        while (true)
                        {
                            var ea = (BasicDeliverEventArgs)consumer.Queue.Dequeue();

                            var body = ea.Body;
                            var message = Encoding.UTF8.GetString(body);
                            Console.WriteLine("Received {0}", message);

                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }
    }
```