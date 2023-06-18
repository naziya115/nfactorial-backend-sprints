from typing import Any
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.database import Database
from pymongo.results import DeleteResult, UpdateResult
from fastapi import HTTPException


class ShanyrakRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_shanyrak(self, user_id: str, data: dict[str, Any]):
        data["user_id"] = ObjectId(user_id)
        payload = {
            "type": data["type"],
            "price": data["price"],
            "address": data["address"],
            "area": data["area"],
            "rooms_count": data["rooms_count"],
            "description": data["description"],
            "location": data["location"],
            "created_at": datetime.utcnow(),
            "user_id": ObjectId(user_id),
        }

        insert_result = self.database["shanyraks"].insert_one(payload)
        return insert_result.inserted_id

    def get_shanyrak(self, shanyrak_id: str):
        return self.database["shanyraks"].find_one({"_id": ObjectId(shanyrak_id)})

    def update_shanyrak(
        self, shanyrak_id: str, user_id: str, data: dict[str, Any]
    ) -> UpdateResult:
        return self.database["shanyraks"].update_one(
            filter={"_id": ObjectId(shanyrak_id), "user_id": ObjectId(user_id)},
            update={
                "$set": data,
            },
        )

    def delete_shanyrak(self, shanyrak_id: str, user_id: str) -> DeleteResult:
        return self.database["shanyraks"].delete_one(
            {"_id": ObjectId(shanyrak_id), "user_id": ObjectId(user_id)}
        )

    def connect_image_to_shanyrak(
        self, shanyrak_id: str, image_id: str
    ) -> UpdateResult:
        return self.database["shanyraks"].update_one(
            filter={"_id": ObjectId(shanyrak_id)},
            update={"$push": {"images": image_id}},
        )

    def update_shanyrak_images(
        self, shanyrak_id: str, user_id: str, update_query: dict
    ) -> UpdateResult:
        filter_query = {"_id": ObjectId(shanyrak_id), "user_id": ObjectId(user_id)}
        update_result = self.database["shanyraks"].update_one(
            filter_query, update_query
        )
        return update_result

    def add_comment(self, author_id: str, shanyrak_id: str, comment: dict):
        comment["created_at"] = datetime.utcnow()
        comment_id = str(ObjectId())

        update_result = self.database["shanyraks"].update_one(
            {"_id": ObjectId(shanyrak_id)},
            {
                "$push": {
                    "comments": {
                        "_id": ObjectId(comment_id),
                        "content": comment["content"],
                        "created_at": comment["created_at"],
                        "author_id": ObjectId(author_id),
                    }
                }
            },
        )

        if update_result.modified_count != 1:
            pass

        return comment_id

    def update_comment(
        self, shanyrak_id: str, comment_id: str, updated_content: str
    ) -> UpdateResult:
        filter_query = {
            "_id": ObjectId(shanyrak_id),
            "comments._id": ObjectId(comment_id),
        }
        update_query = {"$set": {"comments.$.content": updated_content}}

        result = self.database["shanyraks"].update_one(filter_query, update_query)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Shanyrak or comment not found")

        return result

    def delete_comment(self, shanyrak_id: str, comment_id: str):
        filter_query = {
            "_id": ObjectId(shanyrak_id),
            "comments._id": ObjectId(comment_id),
        }

        update_query = {"$pull": {"comments": {"_id": ObjectId(comment_id)}}}

        result = self.database["shanyraks"].update_one(filter_query, update_query)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Shanyrak or comment not found")

    def get_all_comments(self, shanyrak_id: str):
        shanyrak = self.database["shanyraks"].find_one({"_id": ObjectId(shanyrak_id)})
        if not shanyrak:
            pass
        comments = shanyrak.get("comments", [])
        return {"comments": comments}

    def get_shanyraks_by_parameters(
        self,
        limit: int,
        offset: int,
        latitude=None,
        longitude=None,
        radius=None,
        rooms_count=None,
        shanyrak_type=None,
        price_from=None,
        price_until=None,
    ):
        if (
            (latitude is not None and longitude is None)
            or (latitude is None and longitude is not None)
            or (radius is not None and (latitude is None or longitude is None))
        ):
            raise HTTPException(
                status_code=400,
                detail="Latitude, longitude, and radius must be provided together for location-based search.",
            )

        if (latitude is not None or longitude is not None or radius is not None) and (
            latitude is None or longitude is None or radius is None
        ):
            raise HTTPException(
                status_code=400,
                detail="Latitude, longitude, and radius must all be provided for location-based search.",
            )

        query = {}

        if rooms_count is not None:
            query["rooms_count"] = {"$gt": rooms_count}

        if shanyrak_type is not None:
            query["type"] = shanyrak_type

        if price_from is not None and price_until is not None:
            query["price"] = {"$gte": price_from, "$lte": price_until}
        elif price_from is not None:
            query["price"] = {"$gte": price_from}
        elif price_until is not None:
            query["price"] = {"$lte": price_until}

        if latitude is not None and longitude is not None and radius is not None:
            query["location"] = {
                "$geoWithin": {
                    "$centerSphere": [[longitude, latitude], radius / 3963.2]
                }
            }

        total_count = self.database["shanyraks"].count_documents(query)
        cursor = (
            self.database["shanyraks"]
            .find(query)
            .limit(limit)
            .skip(offset)
            .sort("created_at", -1)
        )

        shanyraks = list(cursor)
        return {"total": total_count, "objects": shanyraks}
