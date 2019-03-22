---
title: C#笔记5 SUPERSOCKET处理二进制报文
date: 2018-08-21 14:00:02
modified: 
tags: [C#]
categories: C#
---

以前做项目使用socket是自己实现的服务端，虽然也能使用但接入数量和高并发估计不怎么样。最近相对空闲，突然想起开源的supersocket。

![示例图片](csharp5/20180821.jpg)

<!--more-->

网上的示例代码多是从源代码的QuickStart目录中截取的，大部分都是基于string命令行的，不符合实际项目中都是HEX格式的协议的实际。  
在网上找到一些基于FixedHeaderReceiveFilter的示例代码，FixedHeaderReceiveFilter模板适合整包发送的情况，而实际上TCP的半包和粘包的情况是很多的，必须要先缓冲然后分包，所以FixedHeaderReceiveFilter并不是理想的模板，不过研究后发现可以继承IReceiveFilter自定义实现。

## 安装
从nuget下载SuperSocket.Engine

## 示例代码
CustomProtocolSession.cs
```csharp
using SuperSocket.SocketBase;
using SuperSocket.SocketBase.Protocol;
using System;

namespace CustomProtocol
{
    public class CustomProtocolSession : AppSession<CustomProtocolSession, BinaryRequestInfo>
    {
        protected override void HandleException(Exception e)
        {
            base.HandleException(e);
        }

        protected override void HandleUnknownRequest(BinaryRequestInfo requestInfo)
        {
            base.HandleUnknownRequest(requestInfo);
        }

        protected override void OnInit()
        {
            base.OnInit();
        }

        protected override void OnSessionClosed(SuperSocket.SocketBase.CloseReason reason)
        {
            string log = string.Format("session {0} closed, reason is {1}", SessionID, reason);
            Console.WriteLine(log);
            base.OnSessionClosed(reason);
        }

        protected override void OnSessionStarted()
        {
            string log = string.Format("session {0} started", SessionID);
            Console.WriteLine(log);

            base.OnSessionStarted();
        }
    }
}
```
自定义filter. MyFilter.cs
```csharp
using SuperSocket.SocketBase.Protocol;
using System;
using System.Linq;

namespace CustomProtocol
{
    public class MyFilter : IReceiveFilter<BinaryRequestInfo>
    {
        public int LeftBufferSize { get; }

        public IReceiveFilter<BinaryRequestInfo> NextReceiveFilter { get; }

        public FilterState State { get; }

        public BinaryRequestInfo Filter(byte[] readBuffer, int offset, int length, bool toBeCopied, out int rest)
        {
            rest = 0;
            var data = readBuffer.Skip(offset).Take(length).ToArray();

            string log = BitConverter.ToString(data);
            Console.WriteLine(log);
            return new BinaryRequestInfo("hello", data);
        }

        public void Reset()
        {
        }
    }
}
```
CustomProtocolServer.cs
```csharp
using SuperSocket.SocketBase;
using SuperSocket.SocketBase.Protocol;

namespace CustomProtocol
{
    public class CustomProtocolServer : AppServer<CustomProtocolSession, BinaryRequestInfo>
    {
        public CustomProtocolServer()
            : base(new DefaultReceiveFilterFactory<MyFilter, BinaryRequestInfo>())
        {
        }
    }
}
```
最后是program.cs
```csharp
using SuperSocket.SocketBase;
using SuperSocket.SocketBase.Config;
using System;

namespace CustomProtocol
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Press any key to start ther server!");

            Console.ReadKey();
            Console.WriteLine();

            CustomProtocolServer appServer = new CustomProtocolServer();

            var serverConfig = new ServerConfig
            {
                Mode = SocketMode.Tcp,
                MaxConnectionNumber = 100,
                Port = 2012 //set the listening port
            };
            if (!appServer.Setup(2012))
            {
                Console.WriteLine("Failed to setup!");
                Console.ReadKey();
                return;
            }

            appServer.NewRequestReceived += AppServer_NewRequestReceived1;
            Console.WriteLine();

            if (!appServer.Start())
            {
                Console.WriteLine("Failed to start");
                Console.ReadKey();
                return;
            }

            Console.WriteLine("The server started successfully, press key 'q' to stop it!");

            while (Console.ReadKey().KeyChar != 'q')
            {
                Console.WriteLine();
                continue;
            }

            appServer.Stop();
            Console.WriteLine("The server was stopped!");
            Console.ReadKey();
        }

        private static void AppServer_NewRequestReceived1(CustomProtocolSession session, SuperSocket.SocketBase.Protocol.BinaryRequestInfo requestInfo)
        {
            //throw new NotImplementedException();
            session.Send(requestInfo.Body, 0, requestInfo.Body.Length);

            Console.WriteLine(string.Format("session count is {0}", session.AppServer.SessionCount));
        }
    }
}
```

## 附件
[源代码](CustomProtocol.zip)  


## WEBSOCKET支持
supersocket也支持superwebsocket，代码风格也比较类似。

从nuget下载SuperSocket.Engine, SuperSocket.WebSocket.

服务端代码如下：
```csharp
using SuperSocket.WebSocket;
using System;
using System.Windows.Forms;

namespace SuperWebSocketDemo
{
    public partial class Form1 : Form
    {
        WebSocketServer appServer = new WebSocketServer();
        public Form1()
        {
            InitializeComponent();

            InitEvents();
        }

        ~Form1()
        {
            UnInitEvents();
        }

        private void InitEvents()
        {
            appServer.NewMessageReceived += AppServer_NewMessageReceived;
        }

        private void UnInitEvents()
        {
            appServer.NewMessageReceived -= AppServer_NewMessageReceived;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (!appServer.Setup(2012))
            {
                MessageBox.Show("服务设置失败");
                return;
            }

            if (!appServer.Start())
            {
                MessageBox.Show("服务启动失败");
                return;
            }
        }

        private void AppServer_NewMessageReceived(WebSocketSession session, string value)
        {
            session.Send("server: " + value);

            session.AppServer.Broadcast(session.AppServer.GetAllSessions(), "server: " + value, (s, b) => {; });
        }

        private void button2_Click(object sender, EventArgs e)
        {
            appServer.Stop();
        }
    }
}
```

客户端测试暂时只能使用html
```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>

<head>
    <title>Test</title>
    <script type="text/javascript" src="http://libs.baidu.com/jquery/1.9.1/jquery.min.js"></script>
    <script type="text/javascript">
        var noSupportMessage = "Your browser cannot support WebSocket!";
        var ws;
        function appendMessage(message) {
            $('body').append(message);
        }
        function connectSocketServer() {
            var support = "MozWebSocket" in window ? 'MozWebSocket' : ("WebSocket" in window ? 'WebSocket' : null);
            if (support == null) {
                appendMessage("* " + noSupportMessage + "<br/>");
                return;
            }
            appendMessage("* Connecting to server ..<br/>");
            // create a new websocket and connect
            ws = new window[support]('ws://localhost:2012/');
            // when data is comming from the server, this metod is called
            ws.onmessage = function (evt) {
                appendMessage("# " + evt.data + "<br />");
            };
            // when the connection is established, this method is called
            ws.onopen = function () {
                appendMessage('* Connection open<br/>');
                //$('#messageInput').attr("disabled", "");
                //$('#sendButton').attr("disabled", "");
                //$('#connectButton').attr("disabled", "disabled");
                //$('#disconnectButton').attr("disabled", "");
            };
            // when the connection is closed, this method is called
            ws.onclose = function () {
                appendMessage('* Connection closed<br/>');
                //$('#messageInput').attr("disabled", "disabled");
                //$('#sendButton').attr("disabled", "disabled");
                //$('#connectButton').attr("disabled", "");
                //$('#disconnectButton').attr("disabled", "disabled");
            }
        }
        function sendMessage() {
            if (ws) {
                var messageBox = document.getElementById('messageInput');
                ws.send(messageBox.value);
                messageBox.value = "";
            }
        }
        function disconnectWebSocket() {
            if (ws) {
                ws.close();
            }
        }
        function connectWebSocket() {
            connectSocketServer();
        }
        window.onload = function () {
            //$('#messageInput').attr("disabled", "disabled");
            //$('#sendButton').attr("disabled", "disabled");
            //$('#disconnectButton').attr("disabled", "disabled");
        }

    </script>
</head>

<body>
    <input type="button" id="connectButton" value="Connect" onclick="connectWebSocket()" /> <input type="button" id="disconnectButton"
        value="Disconnect" onclick="disconnectWebSocket()" /> <input type="text" id="messageInput" /> <input type="button" id="sendButton"
        value="Send" onclick="sendMessage()" /> <br />
</body>

</html>
```
websocket客户端应该也可以使用 System.Net.WebSockets下的类来实现

P.S. WIN7好像不支持websocket协议,所以WINFORM，控制台程序都会抛出异常 '此平台不支持 WebSocket 协议。'

## SUPERSOCKET客户端
### 从nuget下载SuperSocket.ClientEngine和SuperSocket.ProtoBase
### 编写自定义ReceiveFilter
```csharp
using SuperSocket.ProtoBase;

namespace SuperSocketDemo1
{
    public class CustomFilter : IReceiveFilter<BufferedPackageInfo>
    {
        public IReceiveFilter<BufferedPackageInfo> NextReceiveFilter { get; }

        public FilterState State { get; }

        public BufferedPackageInfo Filter(BufferList data, out int rest)
        {
            rest = 0;
            return new BufferedPackageInfo("foxbot", data);
        }

        public void Reset()
        {
        }
    }
}
```
### 创建EasyClient实例和通信
```csharp
using SuperSocket.ClientEngine;
using System;
using System.Linq;
using System.Net;
using System.Text;
using System.Windows.Forms;

namespace SuperSocketDemo1
{
    public partial class Form1 : Form
    {
        private EasyClient client = new EasyClient();
        private CustomFilter filter = new CustomFilter();

        public Form1()
        {
            InitializeComponent();
            CheckForIllegalCrossThreadCalls = false;
            Init();
        }

        ~Form1()
        {
            UnInit();
        }

        private void Init()
        {
            client.Initialize(filter, (request) =>
            {
                if (request.Data.Count > 0)
                {
                    var d = request.Data.SelectMany(r => r.ToArray()).ToArray();
                    string s = BitConverter.ToString(d);
                    Console.WriteLine(s);
                }
            });
            client.Connected += Client_Connected;
            client.Closed += Client_Closed;
            client.Error += Client_Error;
        }

        private void UnInit()
        {
            client.Connected -= Client_Connected;
            client.Closed -= Client_Closed;
            client.Error -= Client_Error;
        }

        private void Client_Error(object sender, ErrorEventArgs e)
        {
            Console.WriteLine("error");
        }

        private void Client_Closed(object sender, EventArgs e)
        {
            Console.WriteLine("closed");
        }

        private void Client_Connected(object sender, EventArgs e)
        {
            Console.WriteLine("connected");
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (client.IsConnected)
                client.Close();
            bool result = client.ConnectAsync(new IPEndPoint(IPAddress.Parse("192.168.1.48"), 8000)).Result;
            if (result)
            {
                MessageBox.Show("连接成功");
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            bool result = client.Close().Result;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            string s = "s1212121";
            if (client.IsConnected)
                client.Send(Encoding.Default.GetBytes(s));
        }
    }
}
```

