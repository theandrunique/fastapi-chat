from functools import wraps
import time

import pymongo

from core.config import settings


class ChatInMongoDB:
    def __init__(
        self,
        user_id: int,
        chat_id: int,
    ) -> None:
        """initialize connection to mongodb, create new chat collection if needed"""

        self.client = pymongo.MongoClient(settings.MONGODB_URI)
        self.db = self.client["chats"]
        self.collection = self.db[str(chat_id)]

        self.user_id = user_id
        self.chat_id = chat_id

    def send_message(self, message):
        count_messages = self.get_count_chat_messages()
        current_time = time.time()
        self.collection.insert_one({
                "from_id": self.user_id,
                "message": message,
                "time": current_time,
                "message_id": count_messages + 1,
        })
        
        inserted_message = self.collection.find_one({"message_id": count_messages + 1})
        inserted_message.pop("_id")
        return inserted_message

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