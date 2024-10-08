import logging

from fastapi import APIRouter, HTTPException

from app.database import comment_table, database, post_table
from models.post import Comment, CommentIn, UserPost, UserPostIn, UserPostWithComments

router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"Finding post with id: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    logger.info(f"Creating post with body: {post.body}")
    data = post.model_dump()
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    logger.info(
        f"Creating comment with body: {comment.body} for post: {comment.post_id}"
    )
    post = await find_post(comment.post_id)
    if not post:
        logger.error(f"Post not found: {comment.post_id}")
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comment_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info(f"Getting comments on post: {post_id}")
    post = await find_post(post_id)
    if not post:
        logger.error(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")

    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info(f"Getting post with comments: {post_id}")
    post = await find_post(post_id)
    if not post:
        logger.error(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
