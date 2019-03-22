---
title: C#笔记8 ASPNET CORE中websocket
date: 2018-09-29 23:06:26
modified: 
tags: [C#]
categories: C#
---

在asp.net core 的webapi项目中使用websocket服务.并且是使用websocket4net坐客户端。
主要参考 https://www.cnblogs.com/maxzhang1985/p/6208165.html 的内容

![示例图片](csharp8/20180929.jpg)

<!--more-->

在asp.net core的项目中使用websocket不必使用superwebsocket.直接引入Microsoft.AspNetCore.WebSockets.Server即可.

## 引入Microsoft.AspNetCore.WebSockets.Server包

## 创建SocketHandlerl类
```C#
using System;
using System.Threading.Tasks;

using System.Net.WebSockets;
using System.Threading;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

namespace WebApplication5
{
    public class SocketHandler
    {
        public const int BufferSize = 4096;

        WebSocket socket;

        SocketHandler(WebSocket socket)
        {
            this.socket = socket;
        }

        async Task EchoLoop()
        {
            var buffer = new byte[BufferSize];
            var seg = new ArraySegment<byte>(buffer);

            while (this.socket.State == WebSocketState.Open)
            {
                var incoming = await this.socket.ReceiveAsync(seg, CancellationToken.None);
                var outgoing = new ArraySegment<byte>(buffer, 0, incoming.Count);
                await this.socket.SendAsync(outgoing, WebSocketMessageType.Text, true, CancellationToken.None);
            }
        }

        static async Task Acceptor(HttpContext hc, Func<Task> n)
        {
            if (!hc.WebSockets.IsWebSocketRequest)
                return;

            var sid = hc.Request.Query["sid"];

            var socket = await hc.WebSockets.AcceptWebSocketAsync();
            var h = new SocketHandler(socket);
            await h.EchoLoop();
        }

        /// <summary>
        /// branches the request pipeline for this SocketHandler usage
        /// </summary>
        /// <param name="app"></param>
        public static void Map(IApplicationBuilder app)
        {
            app.UseWebSockets();
            app.Use(SocketHandler.Acceptor);
        }
    }
}

```
然后在Startup.cs的Configure函数中添加
```C#
app.UseDefaultFiles();
app.UseStaticFiles();

app.Map("/ws", SocketHandler.Map);
```

## 客户端代码
首先引入WebSocket4Net包，
调用部分的代码如下
```C#
#region webSocket4Net
        WebSocket4Net.WebSocket websocket2;

        string sid2 = "22";

        private void InitWebSocketNetFoxbot()
        {
            try
            {
                //string socketUrl = ConfigurationManager.AppSettings["WebSocketUrl"].ToString();
                //sid2 = ConfigurationManager.AppSettings["WebSocketId2"].ToString();

                string socketUrl = "ws://localhost:5000/ws";
                string url = socketUrl + "?sid=" + sid2;
                websocket2 = new WebSocket4Net.WebSocket(url);
                //websocket.Opened += new EventHandler(websocket_Opened);
                //websocket.Error += new EventHandler<ErrorEventArgs>(websocket_Error);
                //websocket.Closed += new EventHandler(websocket_Closed);
                //websocket.MessageReceived += new EventHandler(websocket_MessageReceived);
                websocket2.MessageReceived += Websocket2_MessageReceived;
                websocket2.Open();
            }
            catch (System.Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        private void Websocket2_MessageReceived(object sender, WebSocket4Net.MessageReceivedEventArgs e)
        {
            MessageBox.Show(e.Message);
        }

        private void WebSocket4NetSendFoxbot(object data)
        {
            try
            {
                MsgTemplate sendHandshakeMsg = new MsgTemplate
                {
                    Content = JsonConvert.SerializeObject(data),
                    //ClientType = (int)ClientTypeEnum.WfClient,
                    MessageType = (int)MsgTypeEnum.SendEquipmentRealtimeData,
                    ReceiverID = "",
                    SenderID = sid2
                };

                websocket2.Send(JsonConvert.SerializeObject(sendHandshakeMsg));
                websocket2.Send(new byte[2] { 0x01, 0x02 }, 0, 2);
                //_chatWebSocket.SendStringAsync(_cln, JsonConvert.SerializeObject(sendHandshakeMsg), new CancellationToken()).Wait();


            }
            catch (System.Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }
        #endregion
```

