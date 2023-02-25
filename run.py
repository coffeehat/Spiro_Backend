from spiro import Server, SpiroConfig

SpiroConfig.network.listen_ip= "0.0.0.0"
SpiroConfig.network.port = "5000"

# You must use your own token key, you can set whatever you want, but keep secret
SpiroConfig.network.token_key = "spiro"

# If you want to use email, you need to set enabled to True and give the parameters below
SpiroConfig.email.enabled = False
SpiroConfig.email.send_addr = ""
SpiroConfig.email.recv_addr = ""
SpiroConfig.email.port = 25
SpiroConfig.email.smtp_server = ""
SpiroConfig.email.password = ""

server = Server()
server.run()