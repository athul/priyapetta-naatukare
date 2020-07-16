This is a bot to send announcements from College Website to a Telegram via a Telegram Bot. 

Uses the **GitHub API**. Made in Python. Deployed on Deta.

The Data for the Message is got from a GitHub Webhook to the `point` endpoint. The Announcements.yml is only checked when a pull request is merged and converted to json via a yaml loader. The first data part is used and send to telegram.

