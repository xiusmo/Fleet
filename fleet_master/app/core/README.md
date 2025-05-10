config/
├── node-A/
│   ├── private.pem        # node-A 用于签名
│   └── public_keys/
│       ├── node-A.pem     # 自己的公钥
│       ├── node-B.pem     # 其他节点的公钥
│       └── node-C.pem
├── node-B/
│   └── public_keys/       # node-B 无需私钥，只需验证其他节点的 JWT
│       ├── node-A.pem
│       ├── node-B.pem
│       └── node-C.pem
...