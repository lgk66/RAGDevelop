# Node.js应用场景面试题

以下是15道Node.js应用场景的面试题，分为低、中、高难度，并附有答案和代码示例。

### 低难度

1. **问题：如何创建一个简单的HTTP服务器？**
   **答案：**

```javascript
   const http = require('http');

   const server = http.createServer((req, res) => {
     res.statusCode = 200;
     res.setHeader('Content-Type', 'text/plain');
     res.end('Hello, World!\n');
   });

   server.listen(3000, '127.0.0.1', () => {
     console.log('服务器运行在 http://127.0.0.1:3000/');
   });
```

1. **问题：如何读取文件内容并在控制台输出？**
   **答案：**

```javascript
   const fs = require('fs');

   fs.readFile('example.txt', 'utf8', (err, data) => {
     if (err) {
       console.error(err);
       return;
     }
     console.log(data);
   });
```

1. **问题：如何使用Node.js的path模块获取文件的扩展名？**
   **答案：**

```javascript
   const path = require('path');

   const ext = path.extname('example.txt');
   console.log(ext); // 输出: .txt
```

1. **问题：如何使用Node.js的os模块获取系统的主机名？**
   **答案：**

```javascript
   const os = require('os');

   const hostname = os.hostname();
   console.log(hostname);
```

1. **问题：如何使用Node.js的events模块创建一个事件发射器？**
   **答案：**

```javascript
   const EventEmitter = require('events');

   class MyEmitter extends EventEmitter {}

   const myEmitter = new MyEmitter();
   myEmitter.on('event', () => {
     console.log('事件触发');
   });

   myEmitter.emit('event');
```

### 中难度

1. **问题：如何使用Express框架创建一个简单的RESTful API？**
   **答案：**

```javascript
   const express = require('express');
   const app = express();
   const port = 3000;

   app.get('/api', (req, res) => {
     res.json({ message: 'Hello, World!' });
   });

   app.listen(port, () => {
     console.log(`服务器运行在 http://localhost:${port}`);
   });
Copy
```

1. **问题：如何使用Node.js的crypto模块生成一个随机字符串？**
   **答案：**

```javascript
   const crypto = require('crypto');

   const randomString = crypto.randomBytes(16).toString('hex');
   console.log(randomString);
```

1. **问题：如何使用Node.js的child_process模块执行一个外部命令？**
   **答案：**

```javascript
   const { exec } = require('child_process');

   exec('ls', (err, stdout, stderr) => {
     if (err) {
       console.error(`执行错误: ${err}`);
       return;
     }
     console.log(`标准输出: ${stdout}`);
     console.error(`标准错误: ${stderr}`);
   });
```

1. **问题：如何使用Node.js的http模块发起一个GET请求？**
   **答案：**

```javascript
   const http = require('http');

   http.get('http://www.example.com', (res) => {
     let data = '';

     res.on('data', (chunk) => {
       data += chunk;
     });

     res.on('end', () => {
       console.log(data);
     });
   }).on('error', (err) => {
     console.error(`请求错误: ${err.message}`);
   });
```

1. **问题：如何使用Node.js的stream模块创建一个可读流并将其内容写入文件？**
   **答案：**

   ```javascript
   const fs = require('fs');
   
   const readable = fs.createReadStream('source.txt');
   const writable = fs.createWriteStream('destination.txt');
   
   readable.pipe(writable);
   ```

### 高难度

1. **问题：如何使用Node.js的cluster模块创建一个多进程HTTP服务器？**
   **答案：**

   ```javascript
   const cluster = require('cluster');
   const http = require('http');
   const numCPUs = require('os').cpus().length;
   
   if (cluster.isMaster) {
     console.log(`主进程 ${process.pid} 正在运行`);
   
     // Fork workers.
     for (let i = 0; i < numCPUs; i++) {
       cluster.fork();
     }
   
     cluster.on('exit', (worker, code, signal) => {
       console.log(`工作进程 ${worker.process.pid} 已退出`);
     });
   } else {
     http.createServer((req, res) => {
       res.writeHead(200);
       res.end('Hello, World!\n');
     }).listen(8000);
   
     console.log(`工作进程 ${process.pid} 已启动`);
   }
   Copy
   ```

2. **问题：如何使用Node.js的worker_threads模块创建一个工作线程？**
   **答案：**

   ```javascript
   const { Worker, isMainThread, parentPort } = require('worker_threads');
   
   if (isMainThread) {
     const worker = new Worker(__filename);
     worker.on('message', (message) => {
       console.log(`从工作线程接收到消息: ${message}`);
     });
     worker.postMessage('Hello, Worker!');
   } else {
     parentPort.on('message', (message) => {
       console.log(`从主线程接收到消息: ${message}`);
       parentPort.postMessage('Hello, Main Thread!');
     });
   }
   ```

3. **问题：如何使用Node.js的net模块创建一个TCP服务器？**
   **答案：**

   ```javascript
   const net = require('net');
   
   const server = net.createServer((socket) => {
     socket.write('Hello, Client!\n');
     socket.on('data', (data) => {
       console.log(`接收到数据: ${data}`);
     });
   });
   
   server.listen(8080, '127.0.0.1', () => {
     console.log('TCP服务器运行在 http://127.0.0.1:8080/');
   });
   Copy
   ```

4. **问题：如何使用Node.js的zlib模块压缩文件？**
   **答案：**

   ```javascript
   const fs = require('fs');
   const zlib = require('zlib');
   
   const gzip = zlib.createGzip();
   const input = fs.createReadStream('input.txt');
   const output = fs.createWriteStream('input.txt.gz');
   
   input.pipe(gzip).pipe(output);
   Copy
   ```

5. **问题：如何使用Node.js的http2模块创建一个HTTP/2服务器？**
   **答案：**

   ```javascript
   const http2 = require('http2');
   const fs = require('fs');
   
   const server = http2.createSecureServer({
     key: fs.readFileSync('server-key.pem'),
     cert: fs.readFileSync('server-cert.pem')
   });
   
   server.on('stream', (stream, headers) => {
     stream.respond({
       'content-type': 'text/html; charset=utf-8',
       ':status': 200
     });
     stream.end('<h1>Hello, World!</h1>');
   });
   
   server.listen(8443, () => {
     console.log('HTTP/2服务器运行在 https://localhost:8443/');
   });
   ```

这些问题涵盖了Node.js的基础知识、常用模块以及高级特性，适合不同水平的面试者。希望这些问题和答案对你有所帮助！