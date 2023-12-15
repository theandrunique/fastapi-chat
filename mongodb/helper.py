from functools import wraps
import time

import pymongo

from core.config import settings


class ChatInMongoDB:
    def __init__(
        self,
        user_id: int,
        chat_id: str = None,
    ) -> None:
        """initialize connection to mongodb, create new chat collection if needed"""

        self.client = pymongo.MongoClient(settings.MONGODB_URI)
        self.db = self.client["chats"]
        self.collection = self.db[chat_id]

        self.user_id = user_id
        self.chat_id = chat_id

    def send_message(self, message):
        last_message = next(
            self.collection.find({"message": {"$exists": True}})
            .sort([("message_id", -1)])
            .limit(1),
            None,
        )
        next_message_id = 1
        if last_message:
            next_message_id = last_message.get("message_id") + 1

        current_time = time.time()
        self.collection.insert_one({
                "from_id": self.user_id,
                "message": message,
                "time": current_time,
                "message_id": next_message_id,
        })
        return next_message_id

    def get_count_chat_messages(self):
        last_message = next(
            self.collection.find({"message": {"$exists": True}})
            .sort([("message_id", -1)])
            .limit(1),
            None,
        )
        if last_message:
            return last_message.get("message_id")
        elif last_message is None:
            return 0

    def get_chat_messages(self, count=20, offset=0):
        cursor = (
            self.collection.find({"message": {"$exists": True}})
            .sort([("message_id", -1)])
            .limit(count)
            .skip(offset)
        )
        messages = []

        for document in cursor:
            document.pop("_id", None)
            messages.append(document)

        return messages