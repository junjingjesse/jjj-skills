import os
import smtplib
import argparse
from datetime import datetime
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

def get_html_template(subject, body, caller):
    """生成漂亮的HTML邮件模板"""
    # 获取当前时间
    now = datetime.now().strftime("%Y年%m月%d日 %H:%M")

    # 处理换行：将换行符转换为HTML换行
    body_html = body.replace('\n', '<br>')

    # 处理列表：如果内容中有 - 或 • 开头的行，转换为li
    lines = body.split('\n')
    list_items = []
    normal_lines = []
    for line in lines:
        if line.strip().startswith(('- ', '• ')):
            list_items.append(f"<li>{line.strip()[2:]}</li>")
        else:
            normal_lines.append(line)

    # 构建列表HTML
    list_html = ""
    if list_items:
        list_html = f"<ul>{''.join(list_items)}</ul>"
    body_html = '<br>'.join(normal_lines) + list_html

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            margin: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .caller-tag {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: #ffffff;
            padding: 6px 16px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 14px;
        }}
        .content {{
            padding: 30px;
            color: #333333;
            font-size: 16px;
            line-height: 1.8;
        }}
        .content ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        .content li {{
            margin: 8px 0;
            color: #555555;
        }}
        .footer {{
            padding: 20px 30px;
            background: #f8f9fa;
            text-align: center;
            color: #999999;
            font-size: 13px;
        }}
        .footer .time {{
            color: #667eea;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{subject}</h1>
            <div class="caller-tag">{caller}</div>
        </div>
        <div class="content">
            {body_html}
        </div>
        <div class="footer">
            <span class="time">{now}</span> · JJJ Skills 邮件通知
        </div>
    </div>
</body>
</html>
"""
    return html

def send_email(to_email, subject, body, caller="任务"):
    """发送邮件

    参数说明：
    - to_email: 收件人邮箱
    - subject: 邮件主题
    - body: 邮件正文（支持换行和列表：- 项目）
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

    # 生成HTML版本
    html_body = get_html_template(subject, body, caller)

    # 构建邮件（同时发送纯文本和HTML）
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = f"[{caller}] {subject}"

    # 纯文本版本
    text_part = MIMEText(body, 'plain', 'utf-8')
    # HTML版本
    html_part = MIMEText(html_body, 'html', 'utf-8')

    msg.attach(text_part)
    msg.attach(html_part)

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
    parser.add_argument('-b', '--body', type=str, default='任务已完成！', help='邮件正文（支持换行和列表：- 项目）')
    parser.add_argument('-c', '--caller', type=str, default='JJJ技能', help='调用者名称（显示在邮件主题前缀）')

    args = parser.parse_args()
    result = send_email(args.to, args.subject, args.body, args.caller)
    print(result)