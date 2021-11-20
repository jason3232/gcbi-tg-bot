#!/usr/bin/env python

import os
import logging

from dotenv import load_dotenv
from telegram import Update, ChatMemberUpdated, ChatMember, ParseMode
from telegram.ext import CallbackContext, Updater, CommandHandler, ChatMemberHandler
from typing import Tuple, Optional

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

MESSAGE_TIMEOUT = 120


def greet_chat_members(update: Update, context: CallbackContext) -> None:
    """Greets new users in chats and announces when someone leaves"""
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    logger.info("triggered channel event")

    was_member, is_member = result
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        logger.info("new user joined the group, username: {}".format(
            update.chat_member.new_chat_member.user.full_name))

        update.effective_chat.send_message(
            f"歡迎 {member_name} 加入GCBI有問必答. Welcome!\n"
            "發問前可以先參考 <a href=\"https://docs.google.com/presentation/d/1QnfLG"
            "8HGZb8TuwbEyeQoS5jRMDHIhQEK-i05g9aHtPA/edit?usp=sharing\">計劃詳情</a>\n"
            "可以直接係group問問題 admin 見到會答\n"
            "私人問題可以直接搵admin問\n"
            "/help 召喚傳送門",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    elif was_member and not is_member:
        logger.info("user left the group, username: {}".format(
            update.chat_member.new_chat_member.user.full_name))

        update.effective_chat.send_message(
            f"bye bye {member_name} 得閒飲茶",
            parse_mode=ParseMode.HTML,
        )


def extract_status_change(
        chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:

    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member",
                                                                       (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = (
        old_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    )
    is_member = (
        new_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (new_status == ChatMember.RESTRICTED and new_is_member is True)
    )

    return was_member, is_member


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!"
    )

    if message.chat.type == "group":
        context.job_queue.run_once(
            clean_message,
            MESSAGE_TIMEOUT,
            context={
                "chat_id": update.message.chat_id,
                "message_id": message.message_id
            }
        )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    message = update.message.reply_text(
        "傳送門\n"
        "<a href=\"https: // forms.gle/DFpj8kfLFfs3D8zu9\">申請表格</a>\n"
        "Email： gcbi.toronto@gmail.com\n"
        "<a href=\"https://gcbinorth.com/\">GCBI North offical website </a>\n"
        "<a href=\"https://docs.google.com/presentation/d/1QnfLG8HGZb8TuwbEye"
        "QoS5jRMDHIhQEK-i05g9aHtPA/edit?usp=sharing\">計劃詳情</a>",
        parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    if message.chat.type == "group":
        context.job_queue.run_once(
            clean_message,
            MESSAGE_TIMEOUT,
            context={
                "chat_id": update.message.chat_id,
                "message_id": message.message_id
            }
        )


def clean_message(context: CallbackContext) -> None:
    """Clean up messages."""
    context.bot.delete_message(
        context.job.context["chat_id"], context.job.context["message_id"])


def main() -> None:
    """Start the bot."""
    updater = Updater(os.environ.get("API_TOKEN"))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(ChatMemberHandler(
        greet_chat_members, ChatMemberHandler.CHAT_MEMBER))

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


if __name__ == '__main__':
    main()
