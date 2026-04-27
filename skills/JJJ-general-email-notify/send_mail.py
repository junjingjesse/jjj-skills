import os
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置文件路径
ENV_PATH = r"C:\Users\admin\.claude\mail-126.env"

def load_env(env_path):
    """从配置文件加载环境变量"""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def send_email(to_email, subject, body, caller="任务"):
    """发送邮件

    参数说明：
    - to_email: 收件人邮箱
    - subject: 邮件主题
    - body: 邮件正文
    - caller: 调用者名称（如技能名），用于邮件标题前缀
    """
    # 加载配置
    load_env(ENV_PATH)

    # 从环境变量读取配置
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.126.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '465'))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')

    # 检查配置完整性
    if not smtp_user:
        return "错误：请先配置 SMTP_USER"
    if not smtp_pass:
        return "错误：请先配置 SMTP_PASS"
    if not to_email:
        return "错误：请提供收件人邮箱 (-t 参数)"

    # 构建邮件
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
    parser = argparse.ArgumentParser(description='发送邮件通知')
    parser.add_argument('-t', '--to', type=str, required=True, help='收件人邮箱')
    parser.add_argument('-s', '--subject', type=str, default='任务完成', help='邮件主题')
    parser.add_argument('-b', '--body', type=str, default='任务已完成！', help='邮件正文')
    parser.add_argument('-c', '--caller', type=str, default='JJJ技能', help='调用者名称（显示在邮件主题前缀）')

    args = parser.parse_args()
    result = send_email(args.to, args.subject, args.body, args.caller)
    print(result)