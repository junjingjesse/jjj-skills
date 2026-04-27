---
name: JJJ-general-email-notify
description: "通用邮件通知工具。被其他JJJ技能调用发送通知邮件，支持自定义主题、正文、调用者名称。触发 当其他JJJ技能完成任务后需要发送邮件通知时调用此技能。"
---

# 通用邮件通知工具

此技能是被其他JJJ技能调用的，不单独使用。

---

## 使用方式

### 命令行调用

```bash
cd skills/JJJ-general-email-notify
python send_mail.py -t <收件人> -s <主题> -b <正文> -c <调用者>
```

### 参数说明

| 参数 | 简写 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| --to | -t | ✅ | 收件人邮箱 | jessejunjing@163.com |
| --subject | -s | - | 邮件主题，默认"任务完成" | 投资分析报告 |
| --body | -b | - | 邮件正文 | 分析结论：xxx |
| --caller | -c | - | 调用者名称，显示在主题前缀 | JJJ-invest |

### 邮件效果

- 主题：`[调用者] 主题`
- 例如：`[JJJ-invest] 投资分析报告`

---

## 调用示例

### 其他技能调用方式（Python）

```python
import subprocess
result = subprocess.run([
    'python', 'send_mail.py',
    '-t', 'jessejunjing@163.com',
    '-s', '投资分析报告完成',
    '-b', '分析结论：A公司建议买入',
    '-c', 'JJJ-invest'
], capture_output=True, text=True)
print(result.stdout)
```

---

## 配置方法

### 第1步：复制配置模板

```powershell
Copy-Item .env.example "$env:USERPROFILE\.claude\mail-126.env"
```

### 第2步：编辑配置文件

打开 `C:\Users\admin\.claude\mail-126.env`

#### 默认配置（无需修改）

| 变量名 | 默认值 |
|--------|--------|
| SMTP_HOST | smtp.126.com |
| SMTP_PORT | 465 |
| SMTP_SECURE | true |

#### 需要填写

| 变量名 | 说明 |
|--------|------|
| SMTP_USER | 你的126邮箱 |
| SMTP_PASS | SMTP授权码（去126邮箱设置获取） |

### .env.example 模板

```env
# ===== 126邮箱配置 =====
# 配置文件路径：C:\Users\admin\.claude\mail-126.env

# ===== 默认配置（无需修改）=====
SMTP_HOST=smtp.126.com
SMTP_PORT=465
SMTP_SECURE=true

# ===== 需要填写 ======
# 你的126邮箱
SMTP_USER=your-email@126.com

# SMTP授权码（不是登录密码，去126邮箱设置获取）
SMTP_PASS=your-auth-code
```

---

## 授权码获取

1. 登录126邮箱：https://mail.126.com
2. 设置 → 邮箱密码管理
3. 开启"SMTP服务"
4. 获取授权码

---

## send_mail.py 代码

```python
import os
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置文件路径
ENV_PATH = r"C:\Users\admin\.claude\mail-126.env"

def load_env(env_path):
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def send_email(to_email, subject, body, caller="任务"):
    load_env(ENV_PATH)

    smtp_host = os.environ.get('SMTP_HOST', 'smtp.126.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '465'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')

    if not smtp_user:
        return "错误：请先配置 SMTP_USER"
    if not smtp_pass:
        return "错误：请先配置 SMTP_PASS"
    if not to_email:
        return "错误：请提供收件人邮箱 (-t 参数)"

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = f"[{caller}] {subject}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port) if os.environ.get('SMTP_SECURE') == 'true' else smtplib.SMTP(smtp_host, smtp_port)
        if os.environ.get('SMTP_SECURE') != 'true':
            server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return f"邮件发送成功！发送到：{to_email}"
    except Exception as e:
        return f"发送失败：{str(e)}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--to', type=str, required=True)
    parser.add_argument('-s', '--subject', type=str, default='任务完成')
    parser.add_argument('-b', '--body', type=str, default='任务已完成！')
    parser.add_argument('-c', '--caller', type=str, default='JJJ技能')
    args = parser.parse_args()
    result = send_email(args.to, args.subject, args.body, args.caller)
    print(result)
```

---

## 其他技能如何集成

当你的其他JJJ技能（如 JJJ-invest、JJJ-paper）完成任务时：

**1. 询问用户**
"需要发送邮件通知你吗？"

**2. 用户确认后，生成邮件内容**
- 主题：根据技能自动生成
- 正文：技能执行结果摘要
- 调用者：技能名称

**3. 调用 send_mail.py**
使用 subprocess 调用，或直接 import 后调用 send_email() 函数。