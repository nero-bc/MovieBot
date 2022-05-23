"""This file contains a Messenger class which sends post requests to the facebook API."""

import requests


class MessengerFlask:
    def __init__(self, user_id, token):
        """Initializes structs and uri's for Messenger."""

        self.user_id = user_id
        self.buttons = {}
        self.token = token
        self.typing_on_uri = (
            "https://graph.facebook.com/v2.6/me/messages?access_token=" + self.token
        )
        self.mark_seen_uri = (
            "https://graph.facebook.com/v2.6/me/messages?access_token=" + self.token
        )

    def quickreply(self, text, title, payload):
        """Posts a list of quickreply buttons.
        Args:
            text: quickreply title
            title: button text
            payload: button payload

        Returns:
            post request containing quickreply json and quickreply uri

        """
        replies = []
        for i, title in enumerate(title):
            replies.append(
                {"content_type": "text", "title": title, "payload": payload[i]}
            )
        quick_reply = {
            "recipient": {"id": self.user_id},
            "messaging_type": "RESPONSE",
            "message": {"text": text, "quick_replies": replies},
        }
        return quick_reply

    def create_buttons(self, options):
        """Creates a list of buttons.

        Args:
            options: structs with values

        Returns:
            list of buttons

        """
        buttons = []
        for option in options:
            if option["button_type"] == "postback":
                buttons.append(
                    {
                        "type": option["button_type"],
                        "title": option["title"],
                        "payload": option["payload"],
                    }
                )
            if option["button_type"] == "web_url":
                buttons.append(
                    {
                        "type": option["button_type"],
                        "title": option["title"],
                        "url": option["url"],
                    }
                )
        return buttons

    def url_button(self, title, options):
        """Posts a button template of type url_button.
        Args:
            title: button title
            options: structs with values

        Returns:
            post request containing url_button json and url_button uri

        """
        buttons = self.create_buttons(options)
        template = {
            "recipient": {"id": self.user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": title,
                        "buttons": buttons,
                    },
                }
            },
        }
        return template

    def typing_on(self):
        """Displays typing bubble."""
        typing = {"recipient": {"id": self.user_id}, "sender_action": "typing_on"}
        return requests.post(self.typing_on_uri, json=typing).json()

    def mark_seen(self):
        """Displays mark seen icon until new reply is recieved."""
        mark_seen = {"recipient": {"id": self.user_id}, "sender_action": "mark_seen"}
        return requests.post(self.mark_seen_uri, json=mark_seen).json()

    def text(self, message, intent="UNK"):
        """Sends text response.
        Args:
            message: string

        Returns:
            post request with text json and text uri

        """
        text = {
            "recipient": {"id": self.user_id},
            "message": {"text": message, "intent": intent},
        }
        return text

    def template(self, buttons, image, url, subtitle, title):
        """Sends a template response.

        Args:
            buttons: list of buttons
            image: image url
            url: url
            subtitle: text below title
            title: template title

        Returns:
            post request with template json and template uri

        """
        template = {
            "recipient": {"id": self.user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": title,
                                "image_url": image,
                                "subtitle": subtitle,
                                "default_action": {
                                    "type": "web_url",
                                    "url": url,
                                    "webview_height_ratio": "full",
                                },
                                "buttons": buttons,
                            }
                        ],
                    },
                }
            },
        }
        return template

    def buttons_template(self, buttons, text, intent="UNK"):
        """Sends a button template with different button types.

        Args:
            buttons: list of buttons
            text: template title

        Returns:
            post request with button template json and button template uri

        """
        template = {
            "recipient": {"id": self.user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons,
                    },
                }
            },
        }
        return {
            "recipient": {"id": self.user_id},
            "message": {"text": text, "intent": intent},
        }
